"""
The command populates/updates the database locations using the Ukrainian KATOTTG index.
The source CSV comes from https://mindev.gov.ua/diialnist/rozvytok-mistsevoho-samovriaduvannia/kodyfikator-administratyvno-terytorialnykh-odynyts-ta-terytorii-terytorialnykh-hromad
And consists of locations organized by hierarchical KATOTTG codes of the following structure:

                                UA XX YY AAA BBB CC ZZZZZ (e.g. UA01050651270051902), where:
                                    UA - country code
                                    XX - region code
                                    YY - subregion code
                                    AAA - hromada code (sub-subregion)
                                    BBB - populated place code (city/town/village/etc)
                                    CC - city district code (if any)
                                    ZZZZZ - autocode (randomly assigned ID)

Both the hierarchical part of the code and the autocode part are unique. However, autocode does not change over time.
Hence, it's used here to correctly identify and update locations even if their hierarchy code changes.
(Most often caused by merging/splitting subregions and hromadas affecting all children codes).
Hierarchy part is still needed to query and compare locations in an optimized manner (one string encapsulates all info).

The file comes in the format that almost immediately follows the structure of the database yet requires granular tweaks.
The default expected location of the file is set in settings.py with DEFAULT_KATOTTG_CSV_PATH

Downloading the source file at that point is strictly manual, since updates are rare and are not immediately adopted.

Basic usage:
./manage.py update_locations
"""

import csv
from copy import deepcopy

from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Location


# ============== CSV OVERRIDES ================

class KATOTTG_FIELDNAME_OVERRIDES:
    """
    Grouped constants:\n
    CSV fieldnames overrides (for unified referencing).
    """

    REGION_CODE = 'region_code'
    SUBREGION_CODE = 'subregion_code'
    HROMADA_CODE = 'hromada_code'
    PPL_CODE = 'ppl_code'
    CITY_DIST_CODE = 'city_dist_code'
    KATOTTG_CATEGORY = 'katottg_category'
    NAME = 'name'

    @classmethod
    def get_all(cls):
        return (
            cls.REGION_CODE,
            cls.SUBREGION_CODE,
            cls.HROMADA_CODE,
            cls.PPL_CODE,
            cls.CITY_DIST_CODE,
            cls.KATOTTG_CATEGORY,
            cls.NAME
        )


# ============ HELPER CLASSES =============

class CategoryMapper:
    """Translates KATOTTG entry-type indicators into Location categories"""

    class CategoryMap:
        """Stores KATOTTG indicators that suggest this Location category"""

        def __init__(self, indicators: tuple[str, ...], category: str):
            self.indicators = indicators
            self.category = category

    class CategoryError(ValueError):
        def __init__(self, message='Unknown category'):
            self.message = message
            super().__init__(self.message)

    # Categories used for Location types
    REGION = CategoryMap(indicators=('O',), category=Location.CategoryChoices.REGION[0])
    CAPITAL = CategoryMap(indicators=('K',), category=Location.CategoryChoices.CITY[0])
    CITY_DISTRICT = CategoryMap(indicators=('B',), category=Location.CategoryChoices.CITY_DISTRICT[0])
    OTHER_PPL = CategoryMap(indicators=('C', 'T', 'X', 'M'), category=Location.CategoryChoices.OTHER_PPL[0])

    # Categories used for naming only
    SUBREGION = CategoryMap(indicators=('P',), category='s')
    HROMADA = CategoryMap(indicators=('H',), category='h')

    # All categories tuples for convenience
    CATEGORY_MAPS = (REGION, SUBREGION, HROMADA, CAPITAL, OTHER_PPL, CITY_DISTRICT)
    CATEGORY_KEYS = [catmap.category for catmap in CATEGORY_MAPS]

    @classmethod
    def map(cls, source_category_indicator: str) -> str:
        for category_map in cls.CATEGORY_MAPS:
            if source_category_indicator in category_map.indicators:
                return category_map.category
        else:
            raise cls.CategoryError(f'Unknown KATOTTG category: "{source_category_indicator}".\n')


class LocationFlatData:
    """Parses a flat location entry (CSV row) and determines its category and code."""

    def __init__(self, csv_row: dict):
        # Parse the values
        self.region_code = csv_row[KATOTTG_FIELDNAME_OVERRIDES.REGION_CODE]
        self.subregion_code = csv_row[KATOTTG_FIELDNAME_OVERRIDES.SUBREGION_CODE]
        self.hromada_code = csv_row[KATOTTG_FIELDNAME_OVERRIDES.HROMADA_CODE]
        self.ppl_code = csv_row[KATOTTG_FIELDNAME_OVERRIDES.PPL_CODE]
        self.city_dist_code = csv_row[KATOTTG_FIELDNAME_OVERRIDES.CITY_DIST_CODE]
        self.src_category = csv_row[KATOTTG_FIELDNAME_OVERRIDES.KATOTTG_CATEGORY]
        self.name = csv_row[KATOTTG_FIELDNAME_OVERRIDES.NAME]

        # Determine the corresponding Location category
        # We'll have to update the script if an unknown category is met, so failing the execution if so
        try:
            self.category = CategoryMapper.map(self.src_category)
        except CategoryMapper.CategoryError as e:
            raise ValueError(f'\n{e.message}'
                             f'In row:\n{list(csv_row.values())}\n\n') from e

        # Determine the code pointing to the entry and split for further processing
        self.full_code = self._get_full_katottg_code()                    # Full location code
        self.hierarchy_code = self.full_code[:14]                         # Informative part
        self.trimmed_hierarchy_code = self._get_trimmed_hierarchy_code()  # ^ Trimmed for db
        self.autocode = self.full_code[-5:]                               # Random ID part

    def _get_full_katottg_code(self) -> str:
        """Get the code identifying the main entity of this location entry (region, city, city dist, etc.)"""

        category_to_code_mapping = {
            CategoryMapper.REGION.category: self.region_code,
            CategoryMapper.CAPITAL.category: self.region_code,
            CategoryMapper.OTHER_PPL.category: self.ppl_code,
            CategoryMapper.CITY_DISTRICT.category: self.city_dist_code,
            CategoryMapper.SUBREGION.category: self.subregion_code,
            CategoryMapper.HROMADA.category: self.hromada_code
        }
        return category_to_code_mapping.get(self.category)

    def _get_trimmed_hierarchy_code(self) -> str:
        hierarchy_lengths = {
            CategoryMapper.REGION.category: 4,
            CategoryMapper.CAPITAL.category: 12,
            CategoryMapper.OTHER_PPL.category: 12,
            CategoryMapper.CITY_DISTRICT.category: 14
        }
        return self.hierarchy_code[:hierarchy_lengths[self.category]] if self.category in hierarchy_lengths else None


class LocationWithParentsData:
    """Stores a location entry with its parents (region, subregion, hromada, city_dist)."""

    def __init__(
            self,
            category: str,
            region: LocationFlatData,   # Region is top level, it's always present; other levels depend on category
            subregion: LocationFlatData | None = None,
            hromada: LocationFlatData | None = None,
            ppl: LocationFlatData | None = None,
            city_district: LocationFlatData | None = None
    ):
        self.category = category
        self.region = region
        self.subregion = subregion
        self.hromada = hromada
        self.ppl = ppl
        self.city_dist = city_district

    @property
    def main_entry(self) -> LocationFlatData:
        """Determine the main entity of this location entry (region, city, city dist, etc.)"""

        category_to_entry_mapping = {
            CategoryMapper.REGION.category: self.region,
            CategoryMapper.CAPITAL.category: self.ppl or self.region,  # City in csv has ppl level, capital - region
            CategoryMapper.OTHER_PPL.category: self.ppl,
            CategoryMapper.CITY_DISTRICT.category: self.city_dist,
            CategoryMapper.SUBREGION.category: self.subregion,
            CategoryMapper.HROMADA.category: self.hromada
        }
        return category_to_entry_mapping.get(self.category)


class LocationDataRegistry:
    """
    Registers and stores csv rows as parented location data objects organized by category, e.g:
    {
        'r': {  <- regions
            'UA0400...': LocationWithParentsData(Lvivska),
            ...other_regions
        },
        'c': {    <- cities
            'UA0101...': LocationWithParentsData(Kyiv),
            ...other_cities
        },
        ...other_categories
    }
    """

    def __init__(self):
        self.locations: dict[str, dict[str, LocationWithParentsData]] = {
            key: {}
            for key
            in CategoryMapper.CATEGORY_KEYS
        }
        self._locations_uncategorized: dict[str, LocationWithParentsData] = {}

    def register(self, csv_row) -> None:
        """Register a location and link to known parents if any"""

        entry = LocationFlatData(csv_row)
        entry_with_parents = self._assign_with_parents(entry)
        self.locations[entry.category][entry.full_code] = entry_with_parents  # For representation (categorized dict)
        self._locations_uncategorized[entry.full_code] = entry_with_parents   # For search (flat dict)

    def search_by_name(self, name: str, category: str) -> list[LocationWithParentsData]:
        locations = []
        for location in self.locations[category].values():
            if location.main_entry.name == name:
                locations.append(location)
        return locations

    def _assign_with_parents(self, entry: LocationFlatData) -> LocationWithParentsData:
        """Links a flat entry to its parents if any (region, subregion, hromada, city_dist)"""

        category_mapper = CategoryMapper
        category = entry.category

        # Assign parents (if any) to their corresponding hierarchy levels
        linked_entry = LocationWithParentsData(
            category=category,
            region=self._get_flat_entry_by_full_code(entry.region_code),
            subregion=self._get_flat_entry_by_full_code(entry.subregion_code),
            hromada=self._get_flat_entry_by_full_code(entry.hromada_code),
            ppl=self._get_flat_entry_by_full_code(entry.ppl_code)
        )

        # Assign the entry itself to its corresponding hierarchy level
        if any((category == category_mapper.REGION.category, category == category_mapper.CAPITAL.category)):
            linked_entry.region = entry
        elif category == category_mapper.SUBREGION.category:
            linked_entry.subregion = entry
        elif category == category_mapper.HROMADA.category:
            linked_entry.hromada = entry
        elif category == category_mapper.OTHER_PPL.category:
            linked_entry.ppl = entry
        elif category == category_mapper.CITY_DISTRICT.category:
            linked_entry.city_dist = entry

        return linked_entry

    def _get_flat_entry_by_full_code(self, location_code: str) -> LocationFlatData | None:
        if entry := self._locations_uncategorized.get(location_code):
            return entry.main_entry


def parse_katottg_entries(csv_file) -> LocationDataRegistry:
    """Parses a CSV file containing KATOTTG entries and returns a LocationDataRegistry object"""
    katottg_entries = LocationDataRegistry()

    with (open(csv_file, 'r', encoding='utf-8') as file):
        reader = csv.DictReader(file, fieldnames=KATOTTG_FIELDNAME_OVERRIDES.get_all())
        next(reader)           # Skip the first row
        rows = list(reader)    # Get the rest listed

        # TQDM for progress bar
        for row in tqdm(rows, desc="Parsing CSV", unit="rows"):
            katottg_entries.register(row)

    return katottg_entries


class SpecialCasesFixer:
    """Fixes special cases in the parsed location data"""

    # Constants
    _KYIV_NAME = 'Київ'
    _KYIV_REGION_NAME = 'Київська'
    _CRIMEA_NAME_ORIGINAL = 'Автономна Республіка Крим'
    _CRIMEA_NAME_OVERRIDE = 'АР Крим'

    # To augment original code [e.g. UA010100000000] to treat capitals as cities
    # (Original code tail (00000000) suggests a region against app logic)
    _HIERARCHY_TAIL_OVERRIDE = '99999999'

    def __init__(self, parsed_locations: LocationDataRegistry):
        self._fixed_locations = deepcopy(parsed_locations)

    def fix(self) -> LocationDataRegistry:
        self._override_crimea()
        self._fix_capitals()
        return self._fixed_locations

    def _override_crimea(self):
        crimea_entry = self._fixed_locations.search_by_name(
            self._CRIMEA_NAME_ORIGINAL,
            CategoryMapper.REGION.category
        )[0].main_entry
        crimea_entry.name = self._CRIMEA_NAME_OVERRIDE

    def _fix_capitals(self):
        for capital in self._fixed_locations.locations[CategoryMapper.CAPITAL.category].values():
            capital_entity = capital.main_entry

            # 1) Make all capital parents beyond the region point to the capital itself
            capital.subregion = capital.region
            capital.hromada = capital.region
            capital.ppl = capital.region

            # 2) Assign a proper region to the capital (it comes as a region itself)
            region_search_name = self._KYIV_REGION_NAME \
                if capital_entity.name == self._KYIV_NAME \
                else self._CRIMEA_NAME_OVERRIDE
            proper_region = self._fixed_locations.search_by_name(
                region_search_name,
                CategoryMapper.REGION.category
            )[0].main_entry
            capital.region = proper_region

            # 3) Create proper hierarchy code (shortened) (region short hierarchy with default capital tail)
            proper_hierarchy = proper_region.trimmed_hierarchy_code + self._HIERARCHY_TAIL_OVERRIDE
            capital_entity.hierarchy_code = proper_hierarchy

            # 4) Process districts of that capital
            for district in self._fixed_locations.locations[CategoryMapper.CITY_DISTRICT.category].values():
                if district.ppl == capital_entity:
                    # Give this capital's district a proper region
                    district.region = capital.region
                    # Add district number to chain for right hierarchy code
                    district.main_entry.hierarchy_code = proper_hierarchy + district.main_entry.hierarchy_code[-2:]


class LocationModelsBuilder:
    """
    Builds final Location models from the location data
    Outputs a dict of Location models keyed by autocode
    """

    WHOLE_COUNTRY_MODEL = Location(
        hierarchy='UA',
        autocode='00000',
        category=Location.CategoryChoices.WHOLE_COUNTRY[0],
        search_name='Вся Україна'
    )

    def __init__(self, fixed_locations: LocationDataRegistry):
        self._fixed_locations = fixed_locations
        self._locations_to_create_or_update: dict[str, Location] = {}

    def make_locations(self) -> dict[str, Location]:
        self._prepare_whole_country()
        self._prepare_location_models()
        return self._locations_to_create_or_update

    def _prepare_whole_country(self) -> None:
        self._locations_to_create_or_update[self.WHOLE_COUNTRY_MODEL.autocode] = self.WHOLE_COUNTRY_MODEL

    def _prepare_location_models(self) -> None:
        for location_type in (
                CategoryMapper.REGION.category,
                CategoryMapper.CAPITAL.category,
                CategoryMapper.OTHER_PPL.category,
                CategoryMapper.CITY_DISTRICT.category
        ):
            for _, new_location_data in self._fixed_locations.locations[location_type].items():
                self._prepare_location_model(new_location_data)

    def _prepare_location_model(self, new_location_data: LocationWithParentsData) -> None:
        # Prepare region data
        category = new_location_data.category
        autocode = new_location_data.main_entry.autocode
        hierarchy = new_location_data.main_entry.trimmed_hierarchy_code
        search_name = new_location_data.main_entry.name
        region_name = new_location_data.region.name
        subregion_name = None
        ppl_name = None
        district_name = None
        city = None

        # Update if the entry is below region level
        if category in (
                CategoryMapper.CITY_DISTRICT.category,
                CategoryMapper.CAPITAL.category,
                CategoryMapper.OTHER_PPL.category
        ):
            subregion_name = new_location_data.subregion.name
            ppl_name = new_location_data.ppl.name

            # Update further if the entry is a city district
            if category == CategoryMapper.CITY_DISTRICT.category:
                district_name = new_location_data.city_dist.name
                new_city = self._locations_to_create_or_update[new_location_data.ppl.autocode]
                new_city.category = CategoryMapper.CAPITAL.category
                city = new_city
                region_name = new_city.region_name

        # Create and store the model
        new_location = Location(
            autocode=autocode,
            category=category,
            hierarchy=hierarchy,
            region_name=region_name,
            subregion_name=subregion_name,
            ppl_name=ppl_name,
            district_name=district_name,
            search_name=search_name,
            city=city
        )
        self._locations_to_create_or_update[autocode] = new_location


# ============ MAIN PROCESS ===============

class Command(BaseCommand):
    help = ('Import KATOTTG locations from CSV source to database\n'
            'Specify the source via positional argument or use the default from settings')

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='?', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file'] or settings.DEFAULT_KATOTTG_CSV_PATH

        self.stdout.write('Parsing CSV...')
        parsed_entries = parse_katottg_entries(csv_file)

        self.stdout.write('Fixing special cases to fit the database...')
        fixed_entries = SpecialCasesFixer(parsed_entries).fix()

        self.stdout.write('Creating models...')
        locations_to_create_update = LocationModelsBuilder(fixed_entries).make_locations()

        self.stdout.write('Updating the database...')
        self._update_database(locations_to_create_update)

        self.stdout.write(self.style.SUCCESS(
            f'Locations updated successfully. Total locations: {len(locations_to_create_update.values())}'
        ))

    def _update_database(self, locations_to_create_or_update: dict[str, Location]) -> None:
        Location.objects.bulk_create(
            locations_to_create_or_update.values(),
            update_conflicts=True,
            unique_fields=['autocode'],
            update_fields=['category', 'hierarchy', 'region_name', 'subregion_name', 'ppl_name', 'district_name',
                           'city', 'search_name']
        )
        Location.objects.exclude(autocode__in=locations_to_create_or_update.keys()).delete()

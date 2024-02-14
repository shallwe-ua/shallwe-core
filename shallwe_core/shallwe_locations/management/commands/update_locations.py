import csv
from copy import deepcopy

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Location


class CapitalsProperValues:
    class CapitalProperValues:
        def __init__(self, region_name, city_name):
            self.region_name = region_name
            self.city_name = city_name

    KYIV = CapitalProperValues('Київська', 'Київ')
    SEVASTOPOL = CapitalProperValues('АР Крим', 'Севастополь')
    HIERARCHY_TAIL = '99999999'


class KATOTTGFieldnames:
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


class KATOTTGEntity:
    class CategoryMapper:
        """Maps KATOTTG entity category to a database Location category"""
        class CategoryMap:
            def __init__(self, indicators: tuple[str, ...], category: str):
                self.indicators = indicators
                self.category = category

        class CategoryError(ValueError):
            def __init__(self, message='Unknown category'):
                self.message = message
                super().__init__(self.message)

        # For database population
        REGION = CategoryMap(indicators=('O',), category=Location.CategoryChoices.REGION[0])
        CAPITAL = CategoryMap(indicators=('K',), category=Location.CategoryChoices.CITY[0])
        CITY_DISTRICT = CategoryMap(indicators=('B',), category=Location.CategoryChoices.CITY_DISTRICT[0])
        OTHER_PPL = CategoryMap(indicators=('C', 'T', 'X', 'M'), category=Location.CategoryChoices.OTHER_PPL[0])
        # For names only
        SUBREGION = CategoryMap(indicators=('P',), category='s')
        HROMADA = CategoryMap(indicators=('H',), category='h')
        # All categories
        CATEGORY_MAPS = (REGION, SUBREGION, HROMADA, CAPITAL, OTHER_PPL, CITY_DISTRICT)

        @classmethod
        def map(cls, source_indicator):
            for category_map in cls.CATEGORY_MAPS:
                if source_indicator in category_map.indicators:
                    return category_map.category
            else:
                raise cls.CategoryError(f'Unknown KATOTTG category: "{source_indicator}".\n')

    def __init__(self, csv_row: dict):
        self.region_code = csv_row[KATOTTGFieldnames.REGION_CODE]
        self.subregion_code = csv_row[KATOTTGFieldnames.SUBREGION_CODE]
        self.hromada_code = csv_row[KATOTTGFieldnames.HROMADA_CODE]
        self.ppl_code = csv_row[KATOTTGFieldnames.PPL_CODE]
        self.city_dist_code = csv_row[KATOTTGFieldnames.CITY_DIST_CODE]
        self.src_category = csv_row[KATOTTGFieldnames.KATOTTG_CATEGORY]
        self.name = csv_row[KATOTTGFieldnames.NAME]
        try:
            self.category = self.CategoryMapper.map(self.src_category)
        except self.CategoryMapper.CategoryError as e:
            raise ValueError(f'\n{e.message}'
                             f'In row:\n{list(csv_row.values())}\n\n')
        self.full_code = self._get_katottg_code()
        self.hierarchy_part = self.full_code[:14]
        self.autocode_part = self.full_code[-5:]

    def _get_katottg_code(self):
        category_to_code_mapping = {
            self.CategoryMapper.REGION.category: self.region_code,
            self.CategoryMapper.CAPITAL.category: self.region_code,
            self.CategoryMapper.OTHER_PPL.category: self.ppl_code,
            self.CategoryMapper.CITY_DISTRICT.category: self.city_dist_code,
            self.CategoryMapper.SUBREGION.category: self.subregion_code,
            self.CategoryMapper.HROMADA.category: self.hromada_code
        }
        return category_to_code_mapping.get(self.category)


class KATOTTGLinkedLocation:
    def __init__(
            self,
            category: str,
            region: KATOTTGEntity = None,
            subregion: KATOTTGEntity = None,
            hromada: KATOTTGEntity = None,
            ppl: KATOTTGEntity = None,
            city_district: KATOTTGEntity = None
    ):
        self.category = category
        self.region = region
        self.subregion = subregion
        self.hromada = hromada
        self.ppl = ppl
        self.city_dist = city_district

    def get_main_entity(self) -> KATOTTGEntity:
        category_to_entity_mapping = {
            KATOTTGEntity.CategoryMapper.REGION.category: self.region,
            KATOTTGEntity.CategoryMapper.CAPITAL.category: self.ppl or self.region,
            KATOTTGEntity.CategoryMapper.OTHER_PPL.category: self.ppl,
            KATOTTGEntity.CategoryMapper.CITY_DISTRICT.category: self.city_dist,
            KATOTTGEntity.CategoryMapper.SUBREGION.category: self.subregion,
            KATOTTGEntity.CategoryMapper.HROMADA.category: self.hromada
        }
        return category_to_entity_mapping.get(self.category)


class KATOTTGLinkedLocationsRegistry:
    CATEGORY_KEYS = [catmap.category for catmap in KATOTTGEntity.CategoryMapper.CATEGORY_MAPS]

    def __init__(self):
        # e.g.
        # {
        #   'r': {  <- regions
        #       'UA0400...': KATOTTGResolvedLocation(Lvivska),
        #       ...
        #    },
        #   'c':    <- cities
        #       {...},
        # ...
        # }
        self.locations: dict[str, dict[str, KATOTTGLinkedLocation]] = {key: {} for key in self.CATEGORY_KEYS}

    def register(self, entity: KATOTTGEntity) -> None:
        category = entity.category

        if category in self.CATEGORY_KEYS:
            self.locations[category] |= {
                entity.full_code: self.resolve(entity)
            }
        else:
            raise ValueError(f'Category unknown: {category} in {entity.full_code}')

    def resolve(self, entity: KATOTTGEntity) -> KATOTTGLinkedLocation:
        category_mapper = KATOTTGEntity.CategoryMapper
        category = entity.category

        # Set parent entities or Nones
        location = KATOTTGLinkedLocation(
            category=entity.category,
            region=self.get_entity_by_full_code(entity.region_code),
            subregion=self.get_entity_by_full_code(entity.subregion_code),
            hromada=self.get_entity_by_full_code(entity.hromada_code),
            ppl=self.get_entity_by_full_code(entity.ppl_code)
        )

        # Set this entity
        if category == category_mapper.REGION.category:
            location.region = entity
        elif category == category_mapper.SUBREGION.category:
            location.subregion = entity
        elif category == category_mapper.HROMADA.category:
            location.hromada = entity
        elif category == category_mapper.CAPITAL.category:
            location.region = entity
        elif category == category_mapper.OTHER_PPL.category:
            location.ppl = entity
        elif category == category_mapper.CITY_DISTRICT.category:
            location.city_dist = entity

        return location

    def search_by_name(self, name, category) -> list[KATOTTGLinkedLocation]:
        locations = []
        for location in self.locations[category].values():
            if location.get_main_entity().name == name:
                locations.append(location)
        return locations

    def get_global_dict(self) -> dict[str, KATOTTGLinkedLocation]:
        global_dict = {}
        for location_type in self.locations.keys():
            global_dict |= self.locations[location_type]
        return global_dict

    def get_location_by_full_code(self, location_code: str) -> KATOTTGLinkedLocation:
        return self.get_global_dict().get(location_code)

    def get_location_by_autocode(self, autocode: str) -> KATOTTGLinkedLocation:
        global_dict = self.get_global_dict()
        for code, location in global_dict.items():
            if location.get_main_entity().autocode_part == autocode:
                return location

    def get_locations_by_name(self, name: str, category: str) -> list[KATOTTGLinkedLocation]:
        locations = [
            location for location
            in self.locations[category].values()
            if location.get_main_entity().name == name
        ]
        return locations

    def get_entity_by_full_code(self, location_code: str) -> KATOTTGEntity:
        if location := self.get_location_by_full_code(location_code):
            return location.get_main_entity()


class Command(BaseCommand):
    help = ('Import KATOTTG locations from CSV source to database\n'
            'Specify the source via argument or use the default')

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='?', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file'] or settings.DEFAULT_KATOTTG_CSV_PATH
        self.stdout.write('Parsing CSV...')
        katottg_resolved_locations = self._parse_katottg_csv(csv_file)
        self.stdout.write('Restructuring locations to fit the database...')
        katottg_restructured_locations = self._restructure_for_database(katottg_resolved_locations)
        self.stdout.write('Creating models...')
        locations_to_create_or_update = self._prepare_models(katottg_restructured_locations)
        self.stdout.write('Updating the database...')
        self._update_database(locations_to_create_or_update)
        self.stdout.write(self.style.SUCCESS(f'Locations updated successfully. Total locations: {len(locations_to_create_or_update.values())}'))

    def _update_database(self, locations_to_create_or_update: dict[str, Location]) -> None:
        Location.objects.bulk_create(
            locations_to_create_or_update.values(),
            update_conflicts=True,
            unique_fields=['autocode'],
            update_fields=['category', 'hierarchy', 'region_name', 'subregion_name', 'ppl_name', 'district_name',
                           'city', 'search_name']
        )
        Location.objects.exclude(autocode__in=locations_to_create_or_update.keys()).delete()

    def _prepare_models(self, katottg_resolved_locations: KATOTTGLinkedLocationsRegistry) -> dict[str, Location]:
        category_mapper = KATOTTGEntity.CategoryMapper

        whole_country = Location(
            hierarchy='UA',
            autocode='00000',
            category=Location.CategoryChoices.WHOLE_COUNTRY[0],
            search_name='Вся Україна'
        )

        locations_to_create_or_update = {
            whole_country.autocode: whole_country
        }

        for location_type in (
                category_mapper.REGION.category,
                category_mapper.CAPITAL.category,
                category_mapper.OTHER_PPL.category,
                category_mapper.CITY_DISTRICT.category
        ):
            for _, new_location_data in katottg_resolved_locations.locations[location_type].items():
                category = new_location_data.category
                autocode = new_location_data.get_main_entity().autocode_part
                hierarchy = self._get_short_hierarchy(new_location_data.get_main_entity().hierarchy_part, category)
                search_name = new_location_data.get_main_entity().name
                region_name = new_location_data.region.name
                subregion_name = None
                ppl_name = None
                district_name = None
                city = None

                if category in (
                    category_mapper.CITY_DISTRICT.category,
                    category_mapper.CAPITAL.category,
                    category_mapper.OTHER_PPL.category
                ):
                    subregion_name = new_location_data.subregion.name
                    ppl_name = new_location_data.ppl.name

                    if category == category_mapper.CITY_DISTRICT.category:
                        district_name = new_location_data.city_dist.name
                        # Creating city relation
                        new_city = locations_to_create_or_update[new_location_data.ppl.autocode_part]
                        new_city.category = category_mapper.CAPITAL.category  # Convert PPL to City with districts
                        city = new_city
                        region_name = new_city.region_name

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
                locations_to_create_or_update[autocode] = new_location

        return locations_to_create_or_update

    def _restructure_for_database(self, locations: KATOTTGLinkedLocationsRegistry):
        # For convenience
        kyiv_name = CapitalsProperValues.KYIV.city_name
        kyiv_region_name = CapitalsProperValues.KYIV.region_name
        sevastopol_region_name = CapitalsProperValues.SEVASTOPOL.region_name
        tail = CapitalsProperValues.HIERARCHY_TAIL

        # Copy to not mess up with original
        locations = deepcopy(locations)

        # Shorten the name of the Crimea region
        crimea_region = locations.search_by_name(
            'Автономна Республіка Крим',
            KATOTTGEntity.CategoryMapper.REGION.category
        )[0].get_main_entity()
        crimea_region.name = sevastopol_region_name

        # Process capitals
        for capital in locations.locations[KATOTTGEntity.CategoryMapper.CAPITAL.category].values():
            capital_entity = capital.get_main_entity()

            # Give capital lower than region levels equal to capital itself
            capital.ppl = capital.region
            capital.subregion = capital.region
            capital.hromada = capital.region

            # Search for the region to get proper hierarchy by region
            region_search_name = kyiv_region_name if capital_entity.name == kyiv_name else sevastopol_region_name
            proper_region = locations.search_by_name(
                region_search_name,
                KATOTTGEntity.CategoryMapper.REGION.category
            )[0].get_main_entity()
            capital.region = proper_region

            # Create proper hierarchy code (shortened) (basically region short hierarchy + basic capital tail)
            proper_hierarchy = self._get_short_hierarchy(
                proper_region.hierarchy_part,
                category=KATOTTGEntity.CategoryMapper.REGION.category
            ) + tail
            capital_entity.hierarchy_part = proper_hierarchy

            # Process districts of that capital
            for district in locations.locations[KATOTTGEntity.CategoryMapper.CITY_DISTRICT.category].values():
                if district.ppl == capital_entity:
                    # Give this capital's district a proper region
                    district.region = capital.region
                    # Add district number to chain for right hierarchy code
                    district.get_main_entity().hierarchy_part =\
                        proper_hierarchy + district.get_main_entity().hierarchy_part[-2:]

        return locations

    def _parse_katottg_csv(self, csv_file) -> KATOTTGLinkedLocationsRegistry:
        locations = KATOTTGLinkedLocationsRegistry()
        with (open(csv_file, 'r', encoding='utf-8') as file):
            reader = csv.DictReader(file, fieldnames=KATOTTGFieldnames.get_all())
            next(reader)
            for row in reader:
                if src_entity := KATOTTGEntity(row):
                    locations.register(src_entity)
        return locations

    def _get_short_hierarchy(self, hierarchy_part, category):
        category_mapper = KATOTTGEntity.CategoryMapper
        hierarchy_lengts = {
            category_mapper.REGION.category: 4,
            category_mapper.CAPITAL.category: 12,
            category_mapper.OTHER_PPL.category: 12,
            category_mapper.CITY_DISTRICT.category: 14
        }
        return hierarchy_part[:hierarchy_lengts[category]]

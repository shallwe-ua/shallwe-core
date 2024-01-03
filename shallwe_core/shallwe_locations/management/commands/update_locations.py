import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from ...models import Location


class Command(BaseCommand):
    help = 'Import data from CSV file to database'

    class KATOTTGEntity:
        class CategoryMapper:
            """Maps KATOTTG entity category to a database Location category"""
            class CategoryMap:
                def __init__(self, indicators, category):
                    self.indicators = indicators
                    self.category = category

            REGION = CategoryMap(indicators=('О',), category=Location.CategoryChoices.REGION[0])
            CAPITAL = CategoryMap(indicators=('К',), category=Location.CategoryChoices.CITY[0])
            CITY_DISTRICT = CategoryMap(indicators=('В',), category=Location.CategoryChoices.CITY_DISTRICT[0])
            OTHER_PPL = CategoryMap(indicators=('С', 'Т', 'Х', 'М'), category=Location.CategoryChoices.OTHER_PPL[0])
            CATEGORY_MAPS = (REGION, CAPITAL, CITY_DISTRICT, OTHER_PPL)

            @classmethod
            def map(cls, source_indicator):
                for category_map in cls.CATEGORY_MAPS:
                    if source_indicator in category_map.indicators:
                        return category_map.category

        def __init__(self, csv_row):
            self.region_code = csv_row['Перший рівень']
            self.subregion_code = csv_row['Другий рівень']
            self.community_code = csv_row['Третій рівень']
            self.ppl_code = csv_row['Четвертий рівень']
            self.city_dist_code = csv_row['Додатковий рівень']
            self.src_category = csv_row['Категорія об’єкта']
            self.name = csv_row['Назва об’єкта']
            self.prep_category = self.CategoryMapper.map(self.src_category)
            full_code = self._get_katottg_code()
            self.hierarchy = full_code[:14]
            self.autocode = full_code[-5:]

        def _get_katottg_code(self):
            # Todo: if I want to search name by hierarchy I should also include it here for subregions/communities
            if self.prep_category == self.CategoryMapper.REGION.category:
                return self.region_code
            elif self.prep_category in (
                    self.CategoryMapper.CAPITAL.category,
                    self.CategoryMapper.OTHER_PPL.category
            ):
                return self.ppl_code
            elif self.prep_category == self.CategoryMapper.CITY_DISTRICT.category:
                return self.city_dist_code

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='?', type=str, help='Path to the CSV file')

    @staticmethod
    def _get_default_csv_path():
        script_dir = Path(__file__).resolve().parent.parent.parent
        csv_path = script_dir / 'locations_src' / 'katottg.csv'
        return csv_path

    def handle(self, *args, **options):
        csv_file = options['csv_file'] or self._get_default_csv_path()

        with (open(csv_file, 'r', encoding='utf-8') as file):
            reader = csv.DictReader(file)
            for row in reader:
                if src_entity := self.KATOTTGEntity.recognize(row):
                    # Todo: HANDLING FOR CAPITALS hierarchy!!!!!! (Idk maybe just hardcode Kyiv and Sevastopol)
                    # Todo: Namings search
                    # Todo: Exclude creation of subregions/communities locations, only parse entities for namings
                    location = Location(
                        autocode=int(src_entity.autocode),
                        hierarchy=src_entity.hierarchy,
                        category=src_entity.prep_category,

                    )

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

    # def _get_autocode(self, ):

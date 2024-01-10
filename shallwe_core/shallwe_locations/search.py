from django.db.models import QuerySet

from .models import Location

from shallwe_util.efficiency import time_measure

import environ

env = environ.Env()
environ.Env.read_env()


class SearchResult:
    def __init__(self, regions: QuerySet[dict], cities: QuerySet[dict], other_ppls: QuerySet[dict]):
        self.regions = regions
        self.cities = cities
        self.other_ppls = other_ppls

    def to_dict(self) -> dict:
        for city in self.cities:
            city['districts'] = list(city['districts'])

        return {
            'regions': list(self.regions),
            'cities': list(self.cities),
            'other_ppls': list(self.other_ppls)
        }

    def is_empty(self) -> bool:
        return not any((self.regions, self.cities, self.other_ppls))


def search(search_term: str) -> SearchResult:
    search_term = search_term.lower()

    regions = Location.objects.filter(
        search_name__istartswith=search_term,
        category='r'
    ).values('autocode', 'region_name')

    cities = Location.objects.filter(
        search_name__istartswith=search_term,
        category='c'
    ).values('autocode', 'ppl_name', 'region_name')

    other_ppls = Location.objects.filter(
        search_name__istartswith=search_term,
        category='p'
    ).values('autocode', 'ppl_name', 'region_name', 'subregion_name')

    # Retrieving related districts for each city
    for city in cities:
        city['districts'] = Location.objects.filter(
            city_id=city['autocode'],
            category='d'
        ).values('autocode', 'district_name')

    result = SearchResult(regions, cities, other_ppls)
    return result


if env('SHALLWE_BACKEND_MODE') == 'DEV':
    search = time_measure(search)

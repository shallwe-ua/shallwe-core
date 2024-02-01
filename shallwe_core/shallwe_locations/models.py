from django.db import models
from django.db.models import CheckConstraint, Q


class Location(models.Model):
    class CategoryChoices(models.TextChoices):
        WHOLE_COUNTRY = 'a', 'Whole country'
        REGION = 'r', 'Region'
        CITY = 'c', 'City'
        OTHER_PPL = 'p', 'Other PPL'
        CITY_DISTRICT = 'd', 'City district'

    # Last 5 symbols of KATOTTG, doesn't change over time
    autocode = models.CharField(primary_key=True, max_length=5, null=False, unique=True)

    # First 2-14 symbols of KATOTTG, changes over time
    # Key: UAXXYYZZZWWWQQ, where XX - region, YY - subregion, ZZZ - community, WWW - ppl, QQ - city district
    # Only consists of parts relevant for that category of location
    hierarchy = models.CharField(max_length=14, null=False, unique=True)

    category = models.CharField(choices=CategoryChoices.choices, max_length=1, null=False)
    region_name = models.CharField(max_length=32, null=True)
    subregion_name = models.CharField(max_length=32, null=True)
    ppl_name = models.CharField(max_length=32, null=True)
    district_name = models.CharField(max_length=32, null=True)
    search_name = models.CharField(max_length=32, null=False)

    # For city districts only
    city = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, db_column='city_autocode', related_name='districts')

    class Meta:
        ordering = [
            'hierarchy'
        ]

        constraints = [
            # City District category constraints
            CheckConstraint(
                name='city_district_valid_fields',
                check=(
                    Q(
                        (Q(category='d') &
                         Q(city_id__isnull=False) &
                         Q(district_name__isnull=False) &
                         Q(ppl_name__isnull=False) &
                         Q(subregion_name__isnull=False) &
                         Q(region_name__isnull=False))
                    ) |
                    ~Q(category='d')
                )
            ),
            # City and Other PPL category constraints
            CheckConstraint(
                name='ppl_valid_fields',
                check=(
                    Q(
                        ((Q(category='c') | Q(category='p')) &
                         Q(city_id__isnull=True) &
                         Q(district_name__isnull=True) &
                         Q(ppl_name__isnull=False) &
                         Q(subregion_name__isnull=False) &
                         Q(region_name__isnull=False))
                    ) |
                    ~Q(category__in=['c', 'p'])
                )
            ),
            # Region category constraints
            CheckConstraint(
                name='region_valid_fields',
                check=(
                    Q(
                        (Q(category='r') &
                         Q(city_id__isnull=True) &
                         Q(district_name__isnull=True) &
                         Q(ppl_name__isnull=True) &
                         Q(subregion_name__isnull=True) &
                         Q(region_name__isnull=False))
                    ) |
                    ~Q(category='r')
                )
            ),
            # Whole country category constraints
            CheckConstraint(
                name='country_valid_fields',
                check=(
                    Q(
                        (Q(category='a') &
                         Q(city_id__isnull=True) &
                         Q(district_name__isnull=True) &
                         Q(ppl_name__isnull=True) &
                         Q(subregion_name__isnull=True) &
                         Q(region_name__isnull=True))
                    ) |
                    ~Q(category='a')
                )
            ),
        ]

    @staticmethod
    def get_all_country() -> 'Location':
        return Location.objects.get(category='a')

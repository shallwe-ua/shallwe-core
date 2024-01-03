from django.db import models
from django.db.models import CheckConstraint


class Location(models.Model):
    class LocationNameField(models.CharField):
        def __init__(self, *args, **kwargs):
            kwargs['max_length'] = 32  # Set max_length to 32
            kwargs['null'] = False  # Set null to False
            super().__init__(*args, **kwargs)

    # hierarchy 'UA', autocode 00000
    class CategoryChoices(models.TextChoices):
        WHOLE_COUNTRY = 'a', 'Whole country'
        REGION = 'r', 'Region'
        CITY = 'c', 'City'
        OTHER_PPL = 'p', 'Other PPL'
        CITY_DISTRICT = 'd', 'City district'

    # last 5 symbols of KATOTTG, doesn't change over time
    autocode = models.IntegerField(primary_key=True, max_length=5, null=False, unique=True)

    # first 14 symbols of KATOTTG, changes over time
    # Key: UAXXYYZZZWWWQQ, where XX - region, YY - subregion, ZZZ - community, WWW - ppl, QQ - city district
    hierarchy = models.CharField(max_length=14, null=False, unique=True)

    city = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True)

    category = models.IntegerField(choices=CategoryChoices.choices, max_length=1, null=False)
    region_name = LocationNameField()
    subregion_name = LocationNameField()
    ppl_name = LocationNameField()
    district_name = LocationNameField()

    class Meta:
        constraints = [
            # City District category constraints
            CheckConstraint(
                name='city_district_valid_fields',
                check=(
                    "((category = 'd') "
                    "AND city_id IS NOT NULL "
                    "AND district_name IS NOT NULL "
                    "AND ppl_name IS NOT NULL "
                    "AND subregion_name IS NOT NULL "
                    "AND region_name IS NOT NULL) "
                    "OR (category != 'd')"
                ),
            ),
            # City and Other PPL category constraints
            CheckConstraint(
                name='ppl_valid_fields',
                check=(
                    "(((category = 'c') OR (category = 'p')) "
                    "AND city_id IS NULL "
                    "AND district_name IS NULL "
                    "AND ppl_name IS NOT NULL "
                    "AND subregion_name IS NOT NULL "
                    "AND region_name IS NOT NULL) "
                    "OR ((category != 'c') AND (category != 'p'))"
                ),
            ),
            # Region category constraints
            CheckConstraint(
                name='region_valid_fields',
                check=(
                    "((category = 'r') "
                    "AND city_id IS NULL "
                    "AND district_name IS NULL "
                    "AND ppl_name IS NULL "
                    "AND subregion_name IS NULL "
                    "AND region_name IS NOT NULL) "
                    "OR (category != 'r')"
                ),
            ),
            # Whole country category constraints
            CheckConstraint(
                name='country_valid_fields',
                check=(
                    "((category = 'a') "
                    "AND city_id IS NULL "
                    "AND district_name IS NULL "
                    "AND ppl_name IS NULL "
                    "AND subregion_name IS NULL "
                    "AND region_name IS NULL) "
                    "OR (category != 'a')"
                ),
            ),
        ]

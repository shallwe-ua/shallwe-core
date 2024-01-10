from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'autocode',
        'hierarchy',
        'region_name',
        'subregion_name',
        'ppl_name',
        'district_name',
        'city_id',
        'search_name'
    )

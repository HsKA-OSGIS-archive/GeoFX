from django.contrib import admin
from django.contrib.gis import admin as geo_admin
from .models import Map, GeofencePoly

admin.site.register(Map)
admin.site.register(GeofencePoly, geo_admin.GeoModelAdmin)
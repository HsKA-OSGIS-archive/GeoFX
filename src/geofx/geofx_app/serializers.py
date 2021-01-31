from rest_framework import serializers
from .models import Map


class MapSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Map
        fields = ('url_name', 'display_name', 'description',
                  'title', 'fence_enter_message', 'fence_leave_message', 'map_center',
                  'map_zoom_level', 'basemap', 'geofencing_layer_name')

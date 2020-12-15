from django.conf import settings
from django.contrib.gis.db import models
from django.forms import ModelForm

class Map(models.Model):
    url_name = models.TextField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    display_name = models.TextField(blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    geofencing_message = models.TextField(blank=True)
    map_center = models.JSONField(null=True)
    map_zoom_level = models.IntegerField(null=True)
    basemap = models.JSONField(null=True) # {type: , url:}
    geofencing_layer_name = models.TextField(blank=True)

    def get_absolute_url(self):
        return "/map/%s/" % self.url_name

class MapCreateForm(ModelForm):
    class Meta:
        model = Map
        exclude = ('user',)
        fields = ['url_name']

    def __init__(self, *args, **kwargs):
        print(dir(self))
        super(MapCreateForm, self).__init__(*args, **kwargs)


class GeofencePoly(models.Model):
    geom = models.PolygonField()
    map_url_name = models.ForeignKey('Map',on_delete=models.CASCADE)
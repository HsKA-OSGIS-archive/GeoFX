from django.conf import settings
from django.contrib.gis.db import models
import django.forms as forms

class Map(models.Model):
    url_name = models.TextField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    display_name = models.TextField(blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    fence_enter_message = models.TextField(blank=True)
    fence_leave_message = models.TextField(blank=True)
    map_center = models.JSONField(null=True)
    map_zoom_level = models.IntegerField(null=True)
    basemap = models.JSONField(null=True)
    geofencing_layer_name = models.TextField(blank=True)

    def get_absolute_url(self):
        return "/map/%s/" % self.url_name

class MapCreateForm(forms.ModelForm):
    url_name = forms.CharField(max_length=100)
    display_name = forms.CharField(required=False)
    title = forms.CharField(required=False)
    description = forms.CharField(required=False)
    fence_enter_message = forms.CharField(required=False)
    fence_leave_message = forms.CharField(required=False)
    map_center = forms.CharField(required=False)
    map_zoom_level = forms.IntegerField(required=False)
    basemap = forms.CharField(required=False)

    class Meta:
        model = Map
        exclude = ('owner',)

    def __init__(self, *args, **kwargs):
        super(MapCreateForm, self).__init__(*args, **kwargs)



class GeofencePoly(models.Model):
    geom = models.PolygonField()
    map_url_name = models.ForeignKey('Map',on_delete=models.CASCADE)
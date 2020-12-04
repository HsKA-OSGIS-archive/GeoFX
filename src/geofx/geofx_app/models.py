from django.contrib.gis.db import models

class Map(models.Model):
    url_name = models.TextField(primary_key=True)
    display_name = models.TextField(blank=True)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    geofencing_message = models.TextField(blank=True)
    map_center = models.JSONField(null=True)
    map_zoom_level = models.IntegerField(null=True)
    basemap = models.JSONField(null=True) # {type: , url:}
    geofencing_layer_name = models.TextField()

    def get_absolute_url(self):
        return "/map/%s/" % self.url_name


class GeofencePoly(models.Model):
    geom = models.PolygonField()
    map_url_name = models.ForeignKey('Map',on_delete=models.CASCADE)
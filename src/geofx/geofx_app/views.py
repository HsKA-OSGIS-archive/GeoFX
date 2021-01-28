from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse,\
    Http404, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView 

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.files.storage import default_storage
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
import os.path
import requests
from requests.auth import HTTPBasicAuth

from .serializers import MapSerializer
from .models import Map, GeofencePoly, MapCreateForm

from geofx.settings_config import GEOSERVER_USERNAME, \
    GEOSERVER_PASSWORD, GEOSERVER_URL


class PolygonCreate(View):
    def post(self, request, pk):
        # Validation ...
        if not request.user.is_authenticated:
            return HttpResponseNotAllowed
        if request.method == 'POST':
            if not 'geofencing_layer_name' in request.POST or request.POST['geofencing_layer_name'] == '':
              return JsonResponse({'success': False, 'error': 'You must provide a layer name'})
            if not 'geofencing_polygon' in request.FILES or request.FILES['geofencing_polygon'] == '':
              return JsonResponse({'success': False, 'error': 'Missing geojson file'})
            maps = Map.objects.filter(url_name=pk)
            # Find the map instance for which the polygon should be uploaded
            if maps.count() > 0:
                map_key = maps.first()
                up_file = request.FILES['geofencing_polygon']
                path = os.path.join('temp_storage', up_file.name)
                # GEOJSON file is stored for further processing
                file_name = default_storage.save(path, up_file)
                ds = DataSource(file_name)
                lyr = ds[0]
                # Check the geometry
                if not lyr.geom_type.name in ['Polygon', 'MultiPolygon']:
                    return HttpResponseNotAllowed('Layer must be of geometry Polygon or MultiPolygon')
                for feature in lyr:
                    if feature.geom_type.name == 'MultiPolygon':
                        for poly in feature.geom:
                            GeofencePoly.objects.create(geom=poly.wkt, map_url_name=map_key)
                    else:
                        GeofencePoly.objects.create(geom=feature.geom.wkt, map_url_name=map_key)
                # publish a new layer of the geofence_polygon table
                #Future improvement: Handling if epsg is not web mercator
                data_dict = {
                    'featureType': {
                        'name': 'geofence_%s' % pk,
                        'nativeName': 'geofx_app_geofencepoly',
                        'title': 'Geofencing polygon of %s' % pk,
                        "srs": "EPSG:3857",
                        'cqlFilter': 'map_url_name_id = \'%s\'' % pk
                    }
                }
                res = requests.post(GEOSERVER_URL +'rest/workspaces/geofx/featuretypes',\
                    auth=HTTPBasicAuth(GEOSERVER_USERNAME, GEOSERVER_PASSWORD),\
                    json=data_dict
                    )
                if res.status_code >= 200 and res.status_code < 400:
                  response = {'success': True}
                else:
                  response = {'success': False, 'reason': res.text}
                return JsonResponse(response)
            else:
                return HttpResponseNotFound
        else:
            return HttpResponseNotAllowed


class MapView(TemplateView):
    template_name = 'map_view.html'

    def get_context_data(self, url_name):
        maps = Map.objects.filter(url_name=url_name)
        if maps.count() > 0:
            serializer = MapSerializer()
            map_result = maps.first()
            c_dict = serializer.to_representation(map_result)            
            c_dict['map_data'] = c_dict.copy()
            return c_dict
        else:
            raise Http404

class MapCreate(LoginRequiredMixin, CreateView):
    template_name = 'map_edit.html'
    model = Map
    form_class = MapCreateForm

    def get_context_data(self, form=None):
      c_dict = {}
      available_zoom_levels = list(range(3,19))
      c_dict["available_zoom_levels"] = available_zoom_levels
      return c_dict

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return HttpResponseRedirect('/map/' + obj.url_name + '/edit/')

class MapList(TemplateView):
    template_name = 'map_list.html'

    def get_context_data(self):
        maps = Map.objects.filter()
        c_dict = {
            "maps": []
        }
        serializer = MapSerializer()
        for map_i in maps:            
            c_dict["maps"].append(serializer.to_representation(map_i))

        return c_dict
        
class MapEdit(LoginRequiredMixin, UpdateView):
    template_name = 'map_edit.html'
    model = Map
    form_class = MapCreateForm

    def get_context_data(self, form=None):
        maps = Map.objects.filter(url_name=self.kwargs['pk'])
        if maps.count() > 0:
            serializer = MapSerializer()
            map_result = maps.first()
            c_dict = serializer.to_representation(map_result)            
            c_dict['map_data'] = c_dict.copy()
            available_zoom_levels = list(range(3,19))
            c_dict["available_zoom_levels"] = available_zoom_levels
            return c_dict
        else:
            raise Http404

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return HttpResponseRedirect('/map/' + obj.url_name)

    def form_invalid(self, form):
        raise Http404

class MapDelete(DeleteView):
    model = Map
    success_url = '/user/'

class UserOverview(LoginRequiredMixin, TemplateView):
    template_name = 'user_overview.html'

    def get_context_data(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied()
        user = self.request.user
        maps = Map.objects.filter(owner = user)
        serializer = MapSerializer()
        maps = [serializer.to_representation(map_i) for map_i in maps]
        c_dict = {
            "maps" : maps
        }
        return c_dict

def register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            return redirect('login')
    else:
        f = UserCreationForm()

    return render(request, 'registration/register.html', {'form': f})

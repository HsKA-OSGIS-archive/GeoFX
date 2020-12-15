from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse,\
    Http404, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView    

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.files.storage import default_storage
from django.contrib.gis.gdal import DataSource
import os.path
import requests
from requests.auth import HTTPBasicAuth


from .serializers import MapSerializer
from .models import Map, GeofencePoly, MapCreateForm


class PolygonCreate(View):
    #@method_decorator(csrf_exempt, name='dispatch')
    #@csrf_exempt
    def post(self, request, pk):
        print("yo polygon create: ", request, "name: ", pk)
        if request.method == 'POST':  
            maps = Map.objects.filter(url_name=pk)
            if maps.count() > 0:
                map_key = maps.first()

                # Todo: validate (is_valid()?)
                    # Map.objects.filter(url_name=pk).count() > 0:
                up_file = request.FILES['geofencing_polygon']   
                path = os.path.join('temp_storage', up_file.name)
                # Todo: Is it possible to init the DataSource without saving the file to the disk?
                file_name = default_storage.save(path, up_file)
                ds = DataSource(file_name)
                # Todo: handling of more than one layer in the file
                lyr = ds[0]
                # Todo: handling of several polygons/ multipolygon
                feature = lyr[0]
                new_geofence = GeofencePoly.objects.create(geom=feature.geom.wkt, map_url_name=map_key)

                # publish a new layer of the geofence_polygon table
                #Todo: do not use geoserveradmin credentials
                #Todo: what if epsg is not web mercator
                data_dict = {
                    'featureType': {
                        'name': 'geofence_%s' % pk,
                        'nativeName': 'geofx_app_geofencepoly',
                        'title': 'Geofencing polygon of %s' % pk,
                        "srs": "EPSG:3857",
                        'cqlFilter': 'map_url_name_id = \'%s\'' % pk
                    }
                }
                print("publishing new layer: ", data_dict['featureType']['name'])
                res = requests.post('http://localhost/geoserver/rest/workspaces/geofx/featuretypes',\
                    auth=HTTPBasicAuth('admin', 'geoserver'),\
                    json=data_dict
                    )
                import pdb; pdb.set_trace()
                print(res.text)
                response = {'success': 'true'}
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

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return HttpResponseRedirect('/map/' + obj.url_name)


class MapEdit(LoginRequiredMixin, UpdateView):
    template_name = 'map_edit.html'
    model = Map
    fields = ['url_name']

    def get_context_data(self):
        maps = Map.objects.filter(url_name=self.kwargs['pk'])
        if maps.count() > 0:
            serializer = MapSerializer()
            map_result = maps.first()
            c_dict = serializer.to_representation(map_result)
            return c_dict
        else:
            raise Http404

class UserOverview(LoginRequiredMixin, TemplateView):
    template_name = 'user_overview.html'

    def get_context_data(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied()

def register(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        print("is valid: ", f.is_valid())
        if f.is_valid():
            f.save()
            return redirect('login')
    else:
        f = UserCreationForm()

    return render(request, 'registration/register.html', {'form': f})

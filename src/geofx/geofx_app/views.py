#from django.shortcuts import render

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, Http404, HttpResponseNotAllowed
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from django.core.files.storage import default_storage
from django.contrib.gis.gdal import DataSource
import os.path


from .serializers import MapSerializer
from .models import Map, GeofencePoly


class PolygonCreate(View):
    #@method_decorator(csrf_exempt, name='dispatch')
    #@csrf_exempt
    def post(self, request, pk):
        print("yo polygon create: ", request, "name: ", pk)
        if request.method == 'POST':  
            maps = Map.objects.filter(url_name=pk)
            if maps.count() > 0:
                map_key = maps.first()

                # todo: validate (is_valid()?)
                    # Map.objects.filter(url_name=pk).count() > 0:
                up_file = request.FILES['geofencing_polygon']   
                path = os.path.join('temp_storage', up_file.name)
                file_name = default_storage.save(path, up_file)
                print("fiiiiiiiile", file_name)
                ds = DataSource(file_name)
                # todo handling of more than one layer in the file
                lyr = ds[0]
                # todo: handling of several polygons/ multipolygon
                feature = lyr[0]
                new_geofence = GeofencePoly.objects.create(geom=feature.geom.wkt, map_url_name=map_key)
                response = {'hey': 'yo'}
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


class MapCreate(CreateView):
    template_name = 'map_edit.html'
    model = Map
    fields = ['url_name']

class MapEdit(UpdateView):
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
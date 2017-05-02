import json

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from LabModule.app_models.Bandeja import Bandeja
from LabModule.app_models.Maquina import Maquina
from LabModule.app_models.Solicitud import Solicitud
from LabModule.app_models.SolicitudMaquina import SolicitudMaquina
from LabModule.app_models.SolicitudMuestra import SolicitudMuestra
from LabModule.app_models.Usuario import Usuario


def listar_solicitud_muestra(request):
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_manageRequest"):
        section = {}
        section['title'] = 'Listar Solicitudes de Muestras'

        lista_solicitudes = Solicitud.objects.all().exclude(estado = 'aprobada')

        idSolicitudes = [solicitud.id for solicitud in lista_solicitudes]
        lista_MuestraSol = SolicitudMuestra.objects.all().filter(solicitud__in = idSolicitudes)

        context = {'section': section, 'solicitudes': lista_MuestraSol, 'mensaje': 'ok'}
        return render(request, 'solicitudes/aprobarMuestras.html', context)
    else:
        return HttpResponse('No autorizado', status = 401)


def aprobar_solicitud_muestra(request):
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_manageRequest"):
        section = {}
        section['title'] = 'Detalle Solicitud de Muestras'
        try:
            lista_lugares_pos = {}
            solicitud = Solicitud.objects.get(id = request.GET.get('pk', 0))
            muestraSolicitud = SolicitudMuestra.objects.get(solicitud = solicitud)
            usuario = Usuario.objects.get(user = request.user)
            contador = muestraSolicitud.cantidad
            muestra = muestraSolicitud.muestra
            if muestra.calc_disp() == 'Si':
                bandejas = Bandeja.objects.all().filter(muestra = muestra).extra(order_by = ['lugarAlmacenamiento'])
                for bandeja in bandejas:
                    if contador > 0 and bandeja.libre == False:
                        lugar = bandeja.lugarAlmacenamiento.nombre
                        if lugar in lista_lugares_pos:
                            lista_lugares_pos[lugar] += ',' + str(bandeja.posicion)
                        else:
                            lista_lugares_pos[lugar] = str(bandeja.posicion)
                        bandeja.libre = True
                        bandeja.save()
                        contador = contador - 1
                muestraSolicitud.solicitud.aprobador = usuario
                muestraSolicitud.solicitud.estado = 'aprobada'
                muestraSolicitud.solicitud.save()

                contexto = {'lugaresConPos'   : lista_lugares_pos, 'section': section,
                            'muestraSolicitud': muestraSolicitud}
                return render(request, 'solicitudes/resumenAprobadoMuestra.html', contexto)
            else:
                contexto = {
                    'mensaje': 'No es posible aprobar la solicitud porque no hay bandejas disponibles para suplir la demanda'}
        except ObjectDoesNotExist as e:
            contexto = {'mensaje': 'No hay solicitudes con el id solicitado'}
        except MultipleObjectsReturned as e:
            contexto = {'mensaje': 'Muchas solicitudes con ese id'}
        return render(request, 'solicitudes/aprobarMuestras.html', contexto)
    else:
        return HttpResponse('No autorizado', status = 401)


@csrf_exempt
def maquina_reservations(request, pk):
    if request.user.is_authenticated() and request.user.has_perm("LabModule.can_listRequest"):
        lista_maquina = Maquina.objects.filter(idSistema = pk)
        solicitudes = SolicitudMaquina.objects.filter(maquina = lista_maquina)
        results = [ob.as_json(request.user.id) for ob in solicitudes]
        return HttpResponse(json.dumps(results), content_type = "application/json")
    else:
        return HttpResponse()
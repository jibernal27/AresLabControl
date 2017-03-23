# -*- coding: utf-8 -*-

"""Este módulo se encarga de generar las vistas a partir de los modelos, así como de hacer la lógica del negocio. """

__docformat__ = 'reStructuredText'

import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from registration.backends.default.views import RegistrationView

from models import AccountProfile
from models import Bandeja
from models import Experimento
from models import LugarAlmacenamiento
from models import MaquinaEnLab
from models import MaquinaProfile
from models import Muestra
from models import MuestraSolicitud
from models import Paso
from models import Protocolo
from models import Solicitud
from .forms import LugarAlmacenamientoForm
from .forms import MuestraSolicitudForm
from .forms import PosicionesLugarAlmacenamientoForm
from .forms import UserCreationForm


# Create your views here.
def home(request):
    context = {}
    return render(request, "home.html", context)


class UserRegistrationView(RegistrationView):
    form_class = UserCreationForm


def agregar_lugar(request):
    """Desplegar y comprobar los valores a insertar.

           Se encarga de:
               * Mostar el formulario para agregar un lugar de almacenamiento.
               * Mostar el formulario para editar un lugar de almacenamiento ya existente.
               * Agregar un lugar de almacenamiento a la base de datos, agregar la relación entre lugar de almacenamiento y el laboratorio en el que está.

        :param request: El HttpRequest que se va a responder.
        :type request: HttpRequest.
        :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a la modificación del lugar de almacenamiento. Sino redirecciona al mismo formulario mostrando los errores.

       """
    mensaje = ""
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = LugarAlmacenamientoForm(request.POST, request.FILES)
            formPos = PosicionesLugarAlmacenamientoForm(request.POST or None, request.FILES or None)
            items = request.POST.get('items').split('\r\n')

            if form.is_valid() and formPos.is_valid():
                lugar = form.save(commit=False)
                lugarEnLab = formPos.save(commit=False)

                ocupado = MaquinaEnLab.objects.filter(idLaboratorio=lugarEnLab.idLaboratorio, xPos=lugarEnLab.posX,
                                                      yPos=lugarEnLab.posY).exists()
                # lamisma = MaquinaEnLab.objects.filter(pk=lugarEnLab.pk).exists()

                if ocupado:
                    formPos.add_error("posX", "La posición x ya esta ocupada")
                    formPos.add_error("posY", "La posición y ya esta ocupada")

                    mensaje = "El lugar en el que desea guadar ya esta ocupado"
                else:
                    mensaje = "La posición [" + str(lugarEnLab.posX) + "," + str(
                        lugarEnLab.posY) + "] no se encuentra en el rango del laboratorio"
                    lab = lugarEnLab.idLaboratorio
                    masX = lab.numX >= lugarEnLab.posX
                    masY = lab.numY >= lugarEnLab.posY
                    posible = masX and masY
                    if not posible:
                        if not masX:
                            formPos.add_error("posX", "La posición x sobrepasa el valor máximo de " + str(lab.numX))
                        if not masY:
                            formPos.add_error("posY", "La posición y sobrepasa el valor máximo de " + str(lab.numY))
                    else:
                        lugar.save()
                        lugarEnLab.idLugar = lugar
                        lugarEnLab.save()

                        if items is not None and len(items) > 0:
                            for item in items:
                                if item is not None and item != '':
                                    tamano = item.split(',')[0].split(':')[1]
                                    cantidad = item.split(',')[1].split(':')[1]
                                    bandeja = Bandeja(tamano=tamano, cantidad=cantidad, lugarAlmacenamiento=lugar)
                                    bandeja.save()

                        return HttpResponseRedirect(reverse('home'))
        else:
            form = LugarAlmacenamientoForm()
            formPos = PosicionesLugarAlmacenamientoForm()

        return render(request, 'LugarAlmacenamiento/agregar.html',
                      {'form': form, 'formPos': formPos, 'mensaje': mensaje})
    else:
        return HttpResponse('No autorizado', status=401)


class MaquinaForm(ModelForm):
    """Formulario  para crear y modificar una máquina.

        Se encarga de:
            * Tener una instancia del modelo de la máquina
            * Seleccionar cuales campos del modelo seran desplegados en el formulario. Nombre, descripción, si esta reservado,activa
              y la id dada por el sistema.
            * Agregar una máquina a la base de datos, agregar la relación entre la máquina y el laboratorio en el que está.
            * Modificar los datos  de una máquina ya existente.

     :param ModelForm: Instancia de Django.forms.
     :type ModelForm: ModelForm.

    """

    class Meta:
        model = MaquinaProfile
        fields = ['nombre', 'descripcion', 'con_reserva', 'activa', 'idSistema',
                  'imagen']


class PosicionesForm(ModelForm):
    """Formulario  para crear y modificar la ubicación de una máquina.

        Se encarga de:
            * Tener una instancia del modelo de la máquina en laboraotrio.
            * Definir las posición x, la posición y y el laboratorio en el cual se va aguardar la máquina.
            * Agregar una máquina a la base de datos, agregar la relación entre la máquina y el laboratorio en el que está.
            * Modificar la ubicación de una máquina ya existente.

     :param ModelForm: Instancia de Django.forms.
     :type ModelForm: ModelForm.

    """

    class Meta:
        model = MaquinaEnLab
        # fields=['xPos','yPos','idLaboratorio','idMaquina']
        exclude = ('idMaquina',)


def comprobarPostMaquina(form, formPos, request, template_name, section):
    """Desplegar y comprobar los valores a insertar.

        Se encarga de:
            * Mostar el formulario para agregar una máquina.
            * Mostar el formulario para editar una máquina ya existente.
            * Agregar una máquina a la base de datos, agregar la relación entre la máquina y el laboratorio en el que está.

     :param form: La información relevante de la máquina.
     :type form: MaquinaForm.
     :param formPos: La posición y el laboratorio en el que se va a guardar la máquina.
     :type formPos: PosicionesForm.
     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a la modificación de la nueva máquina. Sino redirecciona al mismo formulario mostrand los errores.

    """
    mensaje = ""

    if form.is_valid() and formPos.is_valid():
        new_maquina = form.save(commit=False)
        new_maquinaEnLab = formPos.save(commit=False)
        xPos = new_maquinaEnLab.xPos
        yPos = new_maquinaEnLab.yPos
        ocupadoX = MaquinaEnLab.objects.filter(idLaboratorio=new_maquinaEnLab.idLaboratorio, xPos=xPos).exists()
        ocupadoY = MaquinaEnLab.objects.filter(idLaboratorio=new_maquinaEnLab.idLaboratorio, yPos=yPos).exists()
        # lamisma=MaquinaEnLab.objects.filter(idLaboratorio=new_maquinaEnLab.idLaboratorio, yPos=yPos,xPos=xPos,idMaquina).exists()
        lamisma = MaquinaEnLab.objects.filter(pk=new_maquinaEnLab.pk).exists()
        if (ocupadoX or ocupadoY) and not lamisma:
            if (ocupadoX):
                formPos.add_error("xPos", "La posición x ya esta ocupada")
            if (ocupadoY):
                formPos.add_error("yPos", "La posición y ya esta ocupada")
            mensaje = "El lugar en el que desea guadar ya esta ocupado"
        else:
            mensaje = "La posición [" + str(xPos) + "," + str(yPos) + "] no se encuentra en el rango del labortorio"
            lab = new_maquinaEnLab.idLaboratorio
            masX = lab.numX >= xPos
            masY = lab.numY >= yPos
            posible = masX and masY
            if not posible:
                if not masX:
                    formPos.add_error("xPos", "La posición x sobrepasa el valor máximo de " + str(lab.numX))
                if not masY:
                    formPos.add_error("yPos", "La posición y sobrepasa el valor máximo de " + str(lab.numY))
            else:
                new_maquina.save()
                new_maquinaEnLab.idMaquina = new_maquina
                new_maquinaEnLab.save()
                return redirect(reverse('maquina-update', kwargs={'pk': new_maquina.pk}))

    return render(request, template_name,
                  {'form': form, 'formPos': formPos, 'section': section, 'mensaje': mensaje})


def maquina_create(request, template_name='Maquinas/agregar.html'):
    """Comporbar si el usuario puede agregar una máquina y obtener los campos necesarios.

        Se encarga de:
            * Comprobar si hay un usario logeuado
            * Comprobar si el suario tiene permisos para agregar máquinas
            * Obtener los campos y archivos para redireccionarlos a :func:`comprobarPostMaquina` así
              como decirle el section
            * Definir el template a usar


     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a la modificación de la nueva
                               máquina. Sino redirecciona al mismo formulario mostrando los errores. Si no esta autorizado se envia un código 401

    """

    if request.user.is_authenticated() and request.user.has_perm("account.can_addMachine"):
        section = {}
        section['title'] = 'Agregar máquina'
        section['agregar'] = True
        form = MaquinaForm(request.POST or None, request.FILES or None)
        formPos = PosicionesForm(request.POST or None, request.FILES or None)
        return comprobarPostMaquina(form, formPos, request, template_name, section)
    else:
        return HttpResponse('No autorizado', status=401)


def maquina_update(request, pk, template_name='Maquinas/agregar.html'):
    """Comporbar si el usuario puede modificar una máquina, obtener los campos necesarios.

        Se encarga de:
            * Comprobar si hay un usario logeuado
            * Comprobar si el suario tiene permisos para modificar máquinas
            * Obtener los campos y archivos para redireccionarlos a :func:`comprobarPostMaquina` así
              como decirle el section
            * Definir el template a usar


     :param request: El HttpRequest que se va a responder.
     :type request: HttpRequest.
     :param template_name: La template sobre la cual se va a renderizar.
     :type template_name: html.
     :param pk: La llave primaria de la máquina a modificar
     :type pk: String.
     :param section: Objeto que permite diferenciar entre la modificación de una máquina y la adición de esta.
     :type section: {‘title’:,’agregar’}.
     :returns: HttpResponse -- La respuesta a la petición, en caso de que todo salga bien redirecciona a si mismo. Sino redirecciona al mismo formulario mostrando los errores. Si no esta autorizado se envia un código 401

    """

    if request.user.is_authenticated() and request.user.has_perm("account.can_edditMachine"):
        server = get_object_or_404(MaquinaProfile, pk=pk)
        serverRelacionLab = get_object_or_404(MaquinaEnLab, idMaquina=server)
        mensaje = ""
        form = MaquinaForm(request.POST or None, request.FILES or None, instance=server)
        formPos = PosicionesForm(request.POST or None, request.FILES or None, instance=serverRelacionLab)
        section = {}
        section['title'] = 'Modificar máquina'
        section['agregar'] = False
        return comprobarPostMaquina(form, formPos, request, template_name, section)
    else:
        return HttpResponse('No autorizado', status=401)


def ListarMaquinas(request,pag=1,que=""):
    if request.user.is_authenticated():
            section = {}
            section['title'] = 'Máquinas'
            lista_maquinas=MaquinaProfile.objects.all().filter(nombre__icontains=que).extra(order_by=['name'])
            paginatorMaquinas=Paginator(lista_maquinas,1)
            lista_Posiciones=MaquinaEnLab.objects.all().filter()
            try:
                maquinas = paginatorMaquinas.page(pag)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                maquinas = paginatorMaquinas.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                maquinas = paginatorMaquinas.page(paginatorMaquinas.num_pages)

            context = {'maquinas': maquinas,'lista_Posiciones':lista_Posiciones,'section':section}
            return render(request, 'Maquinas/ListaMaquinas.html', context)
    return HttpResponse('No autorizado', status=401)


def listar_lugares(request):
    """Desplegar y comprobar los valores a consultar.

              Se encarga de:
                  * Mostar el formulario para consultar los lugares de almacenamiento.

           :param request: El HttpRequest que se va a responder.
           :type request: HttpRequest.
           :returns: HttpResponse -- La respuesta a la petición, con información de los lugares de almacenamiento existentes.

          """
    lista_lugares = LugarAlmacenamiento.objects.all()
    context = {'lista_lugares': lista_lugares}
    return render(request, 'LugarAlmacenamiento/listar.html', context)


def crear_solicitud_muestra(request):
    if request.user.is_authenticated() and request.user.has_perm("account.can_solMuestra"):
        mensaje = 'ok'
        try:

            muestra = Muestra.objects.get(id=request.GET.get('id', 0))
            profile = AccountProfile.objects.get(user_id=request.user.id)

            if request.method == 'POST':

                requestObj = Solicitud()
                requestObj.descripcion = 'Solicitud de uso de muestra'
                requestObj.fechaInicial = request.POST['fechaInicial_year'] + "-" + request.POST[
                    'fechaInicial_month'] + "-" + \
                                          request.POST['fechaInicial_day']
                requestObj.estado = 'creada'
                requestObj.solicitante = profile.id
                requestObj.fechaActual = datetime.date.today()
                requestObj.paso = Paso.objects.get(id=request.POST['step'])
                requestObj.save()
                sampleRequest = MuestraSolicitud()
                sampleRequest.solicitud = requestObj
                sampleRequest.muestra = muestra
                sampleRequest.cantidad = request.POST['cantidad']
                sampleRequest.tipo = 'uso'
                sampleRequest.save()
                return redirect("../")

            else:
                form = MuestraSolicitudForm(muestra, profile.id)

        except ObjectDoesNotExist as e:
            form = {}
            mensaje = 'No hay muestras o pasos con el id solicitado'
        except MultipleObjectsReturned as e:
            form = {}
            mensaje = 'Muchas muestras con ese id'
        return render(request, "Solicitudes/crear_muestra_solicitud.html", {'form': form, 'mensaje': mensaje})
    else:
        return HttpResponse('No autorizado', status=401)

def poblar_datos(request):

    MaquinaProfile.objects.create(
    nombre='Laboratorio genomica',
    descripcion = "Aca se hace genomica"
    imagen = models.ImageField(upload_to='images', verbose_name="Imagen", default='images/image-not-found.jpg')
    idSistema = models.CharField(max_length=20, default='', verbose_name="Identificación", null=False, primary_key=True)
    con_reserva = models.BooleanField(default=True, verbose_name="Reservable")
    activa = models.BooleanField(default=True, verbose_name="Activa")

    )
    return HttpResponseRedirect(reverse('home'))


@csrf_exempt
def cargar_experimentos(request):
    if request.GET['project_id'] != "":
        experiments = Experimento.objects.filter(projecto=request.GET['project_id'])
        experimentsDict = dict([(c.id, c.nombre) for c in experiments])
        return HttpResponse(json.dumps(experimentsDict))
    else:
        return HttpResponse()


@csrf_exempt
def cargar_protocolos(request):
    if request.GET['experiment_id'] != "":
        protocols = Protocolo.objects.filter(experimento=request.GET['experiment_id'])
        protocolsDict = dict([(c.id, c.nombre) for c in protocols])
        return HttpResponse(json.dumps(protocolsDict))
    else:
        return HttpResponse()


@csrf_exempt
def cargar_pasos(request):
    if request.GET['protocol_id'] != "":
        steps = Paso.objects.filter(protocolo=request.GET['protocol_id'])
        stepsDict = dict([(c.id, c.nombre) for c in steps])
        return HttpResponse(json.dumps(stepsDict))
    else:
        return HttpResponse()

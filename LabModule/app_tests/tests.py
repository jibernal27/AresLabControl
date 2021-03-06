# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import date

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.test import Client
from django.test import RequestFactory
from django.test import TestCase

from LabModule.app_models.Almacenamiento import Almacenamiento
from LabModule.app_models.Bandeja import Bandeja
from LabModule.app_models.Experimento import Experimento
from LabModule.app_models.Laboratorio import Laboratorio
from LabModule.app_models.Maquina import Maquina
from LabModule.app_models.Muestra import Muestra
from LabModule.app_models.Paso import Paso
from LabModule.app_models.Protocolo import Protocolo
from LabModule.app_models.Proyecto import Proyecto
from LabModule.app_models.Solicitud import Solicitud
from LabModule.app_models.SolicitudMaquina import SolicitudMaquina
from LabModule.app_models.SolicitudMuestra import SolicitudMuestra
from LabModule.app_models.TipoDocumento import TipoDocumento
from LabModule.app_models.Usuario import Usuario
from LabModule.app_views.Almacenamiento import lugar_add
from LabModule.app_views.Maquina import maquina_add, maquina_list, maquina_request, maquina_update
from LabModule.app_views.Solicitud import solicitud_muestra_aprobar, solicitud_muestra_list

c = Client(HTTP_USER_AGENT = 'Mozilla/5.0')
CONTRASENA = getattr(settings, "CONTRASENA")


class AddMaquinasTest(TestCase):
    """Prueba los servicios de agregar y editar máquinas
        Se encarga de:
            * Probar la autorización de servicios
            * Probar los servicios de agregar
    """

    def setUp(self):
        """Inicia el estado del test
            Se encarga de :
                * Crear un usario y darle los permisos de agregar y editar
                * Crear un laboratorio
                * Definir varias máquinas que serviran para probar la lógica del negocio
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username = 'john',
                                             email = 'jlennon@beatles.com',
                                             password = CONTRASENA)
        c.login(username = self.user.username, password = CONTRASENA)

        agregar = Permission.objects.get(name = 'Maquina||agregar')
        editar = Permission.objects.get(name = 'Maquina||editar')
        self.user.user_permissions.add(agregar, editar)
        self.LaboratorioPrueba = Laboratorio.objects.create(nombre = "Laboratorio genetica", id = "LAB_101")

        self.maquinaPrueba = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_010",
            "con_reserva"  : False,
            "posX"         : 0,
            "posY"         : 0,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        self.maquina1 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_001",
            "con_reserva"  : False,
            "posX"         : 10,
            "posY"         : 10,
            "idLaboratorio": self.LaboratorioPrueba.id
        }
        self.maquina2 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_002",
            "con_reserva"  : False,
            "posX"         : 0,
            "posY"         : 0,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        self.maquina3 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_010",
            "con_reserva"  : False,
            "posX"         : 1,
            "posY"         : 1,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        self.maquina4 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_004",
            "con_reserva"  : False,
            "posX"         : 2,
            "posY"         : 2,
            "idLaboratorio": "No existente"
        }

        self.maquina5 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_005",
            "con_reserva"  : False,
            "posX"         : -1,
            "posY"         : -1,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        self.maquina6 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_005",
            "con_reserva"  : False,
            "posX"         : 100,
            "posY"         : 3,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        self.maquina7 = {
            "nombre"       : "Autoclave Portátil",
            "descripcion"  : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_005",
            "con_reserva"  : False,
            "posX"         : 3,
            "posY"         : 100,
            "idLaboratorio": self.LaboratorioPrueba.id
        }
        self.maquina8 = {
            "nombres"      : "Autoclave Portátil",
            "descripcions" : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"    : "AUTO_008",
            "con_reserva"  : False,
            "posX"         : 1,
            "posY"         : 1,
            "idLaboratorio": self.LaboratorioPrueba.id
        }

        request = self.factory.post('/Maquina/add', data = self.maquinaPrueba)
        request.user = self.user
        maquina_add(request)

    def test_PermisoAgregar(self):
        """Comprueba que un usario no autenticado no pueda agregar máquinas.
           También comprueba con un usario con el permiso de agregar máquinas pueda hacerlo
        """
        request = self.factory.get('/Maquina/add', follow = True)
        request.user = AnonymousUser()
        response = maquina_add(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

        request.user = self.user

        response = maquina_add(request)
        self.assertEqual(response.status_code, 200, "Debe estar autorizado")

    def test_ModificarMaquina(self):
        """ Comprueba que un usario no autenticado no pueda editar una máquinas
            tabmíen comprueba que un usuario autenticado pueda hacerlo
        """
        request = self.factory.get('/Maquina/', follow = True)
        request.user = AnonymousUser()
        response = maquina_update(request, 1)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")
        request.user = self.user
        try:
            response = maquina_update(request, 1)
            self.fail("No deberia existir la Maquina")
        except Http404:
            pass

    def test_agregarMaquina(self):
        """ Comprueba que el servicio REST de agregar máquinas sea correcto para un usuario autorizado,
            también comprueba que un usario autorizado pueda editar una máquina existente
        """
        request = self.factory.post('/Maquina/add', data = self.maquina1)
        request.user = self.user
        response = maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_001").exists()
        self.assertEqual(eMaquina, True, "El cientifico debe poder agregar máquinas")

        request = self.factory.get('/Maquina/')

        request.user = self.user
        response = maquina_update(request, 'AUTO_001')
        self.assertEqual(response.status_code, 200, "El cientifico debe estar autorizado y la máquina existir")

    def test_agregarOcupado(self):
        """Agregar una nueva máquina en un lugar ya ocupado
        """
        request = self.factory.post('/Maquina/add', data = self.maquina2)
        request.user = self.user
        maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_002").exists()
        self.assertEqual(eMaquina, False, "El campo ya esta ocupado")

    def test_AgregarIdRepetido(self):
        """Agregar una máquina con un ID ya existente
        """
        request = self.factory.post('/Maquina/add', data = self.maquina3)
        request.user = self.user
        maquina_add(request)
        con = Maquina.objects.filter(con_reserva = False).count()
        eMaquina = con == 1
        self.assertEqual(eMaquina, True, "Deberia solo haber una maquia pero hay " + str(con))

    def test_AgregarLaboratorioInexistente(self):
        """Agregar una máquina a un aboratorio inexistente
        """

        request = self.factory.post('/Maquina/add', data = self.maquina4)
        request.user = self.user
        maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_004").exists()
        self.assertEqual(eMaquina, False, "El laboratorio no es valido")

    def test_AgregarPosicionNegativa(self):
        """
        Agregar una máquina en una posición invalidad en el laboratorio
        """

        request = self.factory.post('/Maquina/add', data = self.maquina5)
        request.user = self.user
        response = maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_005").exists()
        self.assertEqual(eMaquina, False, "La posicion es invalida")

    def test_AgregarxSuperior(self):
        """Agregar una máquina en una posición x mayor a la capacidad del laboratorio
        """

        request = self.factory.post('/Maquina/add', data = self.maquina6)
        request.user = self.user
        response = maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_005").exists()
        self.assertEqual(eMaquina, False, "La posicion es invalida")

    def test_AgregarySuperior(self):
        """Agregar una máquina en una posición y mayor a la capacidad del laboratorio
        """

        request = self.factory.post('/Maquina/add', data = self.maquina7)
        request.user = self.user
        response = maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_005").exists()
        self.assertEqual(eMaquina, False, "La posicion es invalida")

    def test_AgregarCamposInvalidos(self):
        """Prueba los campos obligatorios del servicio REST
        """

        request = self.factory.post('/Maquina/add', data = self.maquina8)
        request.user = self.user
        response = maquina_add(request)
        eMaquina = Maquina.objects.filter(pk = "AUTO_008").exists()
        self.assertEqual(eMaquina, False, "La posicion es invalida")


class listMaquinasTest(TestCase):
    """ Se encarga de probar los permissos de listar máquinas
         Se encarga de:
            * Crear usurios y agregarles sus permisos
            * Probar los servicios con cada usuario
    """

    def setUp(self):
        """"Crea un cientifico, un asistente y un jefe para probar sus permisos
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.cientifico = User.objects.create_user(username = 'john',
                                                   email = 'jlennon@beatles.com',
                                                   password = CONTRASENA)
        c.login(username = self.cientifico.username, password = CONTRASENA)

        ver = Permission.objects.get(name = 'Maquina||ver')
        self.cientifico.user_permissions.add(ver)
        self.LaboratorioPrueba = Laboratorio.objects.create(nombre = "Laboratorio genetica", id = "LAB_101")
        self.MaquinaPrueba = Maquina.objects.create(nombre = "prueba",
                                                    descripcion = "Maquina de prueba",
                                                    idSistema = "MAQ001")
        MaquinaEnLab.objects.get_or_create(idLaboratorio = self.LaboratorioPrueba, idMaquina = self.MaquinaPrueba,
                                           posX = 0, posY = 0)

        self.MaquinaPrueba = Maquina.objects.create(nombre = "Autoclave",
                                                    descripcion = "prueba",
                                                    idSistema = "MAQ002")
        MaquinaEnLab.objects.get_or_create(idLaboratorio = self.LaboratorioPrueba, idMaquina = self.MaquinaPrueba,
                                           posX = 1, posY = 1)

    def test_PermisoVer(self):
        """Comprueba que solo los usarios autorizados puedan ver la lista de máquinas
        """
        request = self.factory.get('/Maquina', follow = True)
        request.user = AnonymousUser()
        response = maquina_list(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")
        request.user = self.cientifico
        response = maquina_list(request)
        self.assertEqual(response.status_code, 200, "El cientifico debe estar autorizado")

    def test_Filtro(self):
        """Comrprueba que el filtro funcione
        """
        request = self.factory.get('/Maquina?que=blabla', follow = True)
        request.user = self.cientifico
        response = maquina_list(request)
        self.assertEqual(response.status_code, 200, "El cientifico debe estar autorizado")
        self.assertEqual("MAQ001" in response.content, False, "No debe encontrar la máquinas")

        request = self.factory.get('/Maquina?que=auto', follow = True)
        request.user = self.cientifico
        response = maquina_list(request)
        self.assertEqual("MAQ002" in response.content, True, "Debe encontrar la máquinas")


class LoginTest(TestCase):
    """Prueba el servicio de autenticación 
        Se encarga de:
            * Probar que el servicio REST de autenicación funcione
            * Autenticar varios usarios
    """

    def setUp(self):
        """"Registra un usuario en la aplicación
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.cientifico = User.objects.create_user(username = 'john',
                                                   email = 'jlennon@beatles.com',
                                                   password = CONTRASENA)
        # c.login(username=self.cientifico.username, password=CONTRASENA)

        ver = Permission.objects.get(name = 'usuario||agregar')
        self.cientifico.user_permissions.add(ver)

    def testLogin(self):
        """ Prueba que el usario registrado en la base de datos pueda inciar sesión"""
        postData = {"username": "john", "password": CONTRASENA}
        response = c.post('/accounts/login/', postData, follow = True)
        self.assertEqual(response.content, 200, "Debe poder inciar sesion")

        self.assertEqual(not "correct username" in response.content, True, "Debe poder inciar sesion")

    def testLogin(self):
        """ Prueba que no se pueda inicar sesión con un contraseña incorrecta"""
        postData = {"username": "john", "password": "estamal"}
        response = c.post('/accounts/login/', postData, follow = True)
        self.assertEqual("correct username" in response.content, True, "No debe poder inciar sesións")

    def testLogin(self):
        """ Prueba que no se pueda inicar sesión con un usario incorrecto"""
        postData = {"username": "incorrecto", "password": "estamal"}
        response = c.post('/accounts/login/', postData, follow = True)
        self.assertEqual("correct username" in response.content, True, "No debe poder inciar sesións")


class AprobarSolMuestraTest(TestCase):
    def setUp(self):
        """"Aprobar solicitudes de muestra
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.LaboratorioPrueba = Laboratorio.objects.create(nombre = "Laboratorio genetica", id = "LAB_101")
        self.user = User.objects.create_user(username = 'john',
                                             email = 'jlennon@beatles.com',
                                             password = CONTRASENA)
        c.login(username = self.user.username, password = CONTRASENA)

        admin = Permission.objects.get(name = 'solicitud||admin')
        self.user.user_permissions.add(admin)

        self.tipoId = TipoDocumento.objects.create(nombre_corto = "cc", descripcion = "")
        self.grupo = Group.objects.create(name = 'asistentes')
        self.usuario = Usuario.objects.create(nombre_usuario = "jlennon", correo_electronico = "jlennon@beatles.com",
                                              codigo_usuario = "201610780", nombres = "John", apellidos = "Lennon",
                                              telefono = "3005717606", userNatIdTyp = self.tipoId,
                                              userNatIdNum = "51603784",
                                              grupo = self.grupo, user = self.user, contrasena = CONTRASENA)
        self.userSinPermisos = User.objects.create_user(username = 'camilo',
                                                        email = 'ccastillo@amigos.com',
                                                        password = CONTRASENA)
        c.login(username = self.userSinPermisos.username, password = CONTRASENA)

        self.protocoloPrueba = Protocolo.objects.create(nombre = "Protocolo # 1",
                                                        descripcion = "Este es un protocolo de prueba",
                                                        objetivo = "Comprobar funcionalidad de solicitud maquinas")
        self.pasoPrueba = Paso.objects.create(id = "1", nombre = "Paso # 1", descripcion = "Este es un paso de prueba",
                                              protocolo = self.protocoloPrueba)
        self.proyectoPrueba = Proyecto.objects.create(nombre = "Proyecto # 1",
                                                      descripcion = "Este es un proyecto de prueba",
                                                      objetivo = "Comprobar funcionalidad de solicitud maquinas",
                                                      lider = self.usuario, activo = True)
        self.proyectoPrueba.asistentes.add(self.usuario)
        self.experimentoPrueba = Experimento.objects.create(nombre = "Experimento # 1",
                                                            descripcion = "Este es un experimento de prueba",
                                                            objetivo = "Comprobar funcionalidad de solicitud maquinas",
                                                            projecto = self.proyectoPrueba)
        self.experimentoPrueba.protocolos.add(self.protocoloPrueba)
        self.muestra = Muestra.objects.create(nombre = "Muestra #1", descripcion = "Esta es una muestra de prueba",
                                              valor = "1", unidadBase = "sobres",
                                              activa = True, controlado = True)
        self.solicitud = Solicitud.objects.create(descripcion = "Solicitud de muestra", fechaInicial = date(2017, 6, 2),
                                                  fechaFinal = date(2017, 6, 8), estado = 'creada',
                                                  solicitante = self.usuario,
                                                  fechaActual = date(2017, 6, 2), paso = self.pasoPrueba)
        self.solicitudMuestra = SolicitudMuestra.objects.create(tipo = "uso", cantidad = "2",
                                                                solicitud = self.solicitud,
                                                                muestra = self.muestra)
        self.segundaSolicitud = Solicitud.objects.create(descripcion = "Solicitud de muestra #2",
                                                         fechaInicial = date(2017, 6, 2),
                                                         fechaFinal = date(2017, 6, 8), estado = 'creada',
                                                         solicitante = self.usuario,
                                                         fechaActual = date(2017, 6, 2), paso = self.pasoPrueba)
        self.segundaSolicitudMuestra = SolicitudMuestra.objects.create(tipo = "uso", cantidad = "3",
                                                                       solicitud = self.segundaSolicitud,
                                                                       muestra = self.muestra)
        self.data = {
            "nombre"       : "Lugar # 1",
            "descripcion"  : "Lugar de almacenamiento de prueba",
            "capacidad"    : "5",
            "temperatura"  : "20.0",
            "idLaboratorio": self.LaboratorioPrueba.id,
            "posX"         : "2",
            "posY"         : "10"
        }
        request = self.factory.post('almacenamiento/add/', data = self.data)
        request.user = self.user
        lugar_add(request)
        self.lugarAlmacenamiento = Almacenamiento.objects.get(nombre = "Lugar # 1")
        self.bandejas = Bandeja.objects.all().filter(lugarAlmacenamiento = self.lugarAlmacenamiento)
        for bandeja in self.bandejas:
            bandeja.muestra = self.muestra
            bandeja.libre = False
            bandeja.save()

    def test_ingresar(self):
        """Comprueba que un usario no autenticado no pueda aprobar solicitud de muestra.
           También comprueba con un usario con el permiso de aprobar solicitud de muestra pueda hacerlo
        """
        request = self.factory.get('aprobarSolicitudMuestras/listar/', follow = True)
        request.user = AnonymousUser()
        response = solicitud_muestra_list(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

        request = self.factory.get('aprobarSolicitudMuestras/aprobar/', follow = True)
        request.user = AnonymousUser()
        response = solicitud_muestra_aprobar(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

        request = self.factory.get('aprobarSolicitudMuestras/aprobar/', follow = True)
        request.user = self.userSinPermisos
        response = solicitud_muestra_list(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

        request = self.factory.get('aprobarSolicitudMuestras/aprobar/', follow = True)
        request.user = self.userSinPermisos
        response = solicitud_muestra_aprobar(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

    def test_listar_solicitudes(self):
        """Comprueba que se pueda obtener la lista de solicitudes de muestra
                """
        lista_solicitudes = Solicitud.objects.all().exclude(estado = 'aprobada')
        self.assertEqual(len(lista_solicitudes), 2, "No es la cantidad de solicitudes correcta")
        idSolicitudes = [solicitud.id for solicitud in lista_solicitudes]
        lista_MuestraSol = SolicitudMuestra.objects.all().filter(solicitud__in = idSolicitudes)
        self.assertEqual(len(lista_MuestraSol), 2, "No es la cantidad de solicitudes de muestra correcta")

    def test_muestras_disponibles(self):
        """Comprueba que hayan muestras disponibles
                       """
        self.assertEqual(self.muestra.calc_disp(), 'Si', 'Deberian haber muestras disponibles')

    def test_aprobar_solicitud(self):
        """Comprueba que se pueda aprobar solicitud de muestra
                       """
        request = self.factory.get('aprobarSolicitudMuestras/aprobar/')
        request.GET = request.GET.copy()
        request.GET['pk'] = self.solicitud.pk
        request.user = self.user
        solicitud_muestra_aprobar(request)
        bandejasLibres = Bandeja.objects.all().filter(lugarAlmacenamiento = self.lugarAlmacenamiento, libre = True)
        self.assertEqual(len(bandejasLibres), 2, 'Deberian haber bandejas libres')
        muestraSol = SolicitudMuestra.objects.get(id = 1)
        self.assertEqual(muestraSol.solicitud.estado, 'aprobada', 'Deberian estar la solicitud aprobada')


class SolicitarMaquinaTest(TestCase):
    """Inicia el estado del test
                Se encarga de :
                    * Crear un usario y darle los permisos de solicitar
                    * Crear un laboratorio
                    * Definir varias máquinas que serviran para probar la lógica del negocio
                    * Crear proyecto, experimento, protocolos y pasos de prueba
            """

    # Every test needs access to the request factory.
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username = 'john',
                                             email = 'jlennon@beatles.com',
                                             password = CONTRASENA)
        c.login(username = self.user.username, password = CONTRASENA)
        self.tipoId = TipoDocumento.objects.create(nombre_corto = "cc", descripcion = "")
        self.grupo = Group.objects.create(name = 'asistentes')
        self.usuario = Usuario.objects.create(nombre_usuario = "jlennon", correo_electronico = "jlennon@beatles.com",
                                              codigo_usuario = "201610780", nombres = "John", apellidos = "Lennon",
                                              telefono = "3005717606", userNatIdTyp = self.tipoId,
                                              userNatIdNum = "51603784",
                                              grupo = self.grupo, user = self.user, contrasena = CONTRASENA)
        self.userSinPermisos = User.objects.create_user(username = 'camilo',
                                                        email = 'ccastillo@amigos.com',
                                                        password = CONTRASENA)
        c.login(username = self.userSinPermisos.username, password = CONTRASENA)

        solicitar = Permission.objects.get(name = 'Maquina||solicitar')

        self.user.user_permissions.add(solicitar)
        self.LaboratorioPrueba = Laboratorio.objects.create(nombre = "Laboratorio genetica", id = "LAB_101")

        self.maquinaPrueba = {
            "idAlmacenamiento": "1",
            "nombre"          : "Autoclave Portátil",
            "descripcion"     : "Un autoclave es un recipiente de presión metálico de paredes gruesas con un cierre hermético que permite trabajar a alta presión para realizar una reacción industrial, una cocción o una esterilización con vapor de agua",
            "idSistema"       : "AUTO_010",
            "con_reserva"     : False,
            "posX"            : 0,
            "posY"            : 0,
            "idLaboratorio"   : self.LaboratorioPrueba.id
        }

        request = self.factory.post('/Maquina/add', data = self.maquinaPrueba)
        request.user = self.user
        maquina_add(request)
        self.protocoloPrueba = Protocolo.objects.create(nombre = "Protocolo # 1",
                                                        descripcion = "Este es un protocolo de prueba",
                                                        objetivo = "Comprobar funcionalidad de solicitud maquinas")
        self.pasoPrueba = Paso.objects.create(id = "1", nombre = "Paso # 1", descripcion = "Este es un paso de prueba",
                                              protocolo = self.protocoloPrueba)
        self.proyectoPrueba = Proyecto.objects.create(nombre = "Proyecto # 1",
                                                      descripcion = "Este es un proyecto de prueba",
                                                      objetivo = "Comprobar funcionalidad de solicitud maquinas",
                                                      lider = self.usuario, activo = True)
        self.proyectoPrueba.asistentes.add(self.usuario)
        self.experimentoPrueba = Experimento.objects.create(nombre = "Experimento # 1",
                                                            descripcion = "Este es un experimento de prueba",
                                                            objetivo = "Comprobar funcionalidad de solicitud maquinas",
                                                            projecto = self.proyectoPrueba)
        self.experimentoPrueba.protocolos.add(self.protocoloPrueba)

    def test_UsuarioNoAutorizado(self):
        """Comprueba que un usario no autenticado no pueda solicitar máquinas.
           También comprueba con un usario con el permiso de agregar máquinas pueda hacerlo
        """
        request = self.factory.get('/Maquina/solicitar', follow = True)
        request.user = AnonymousUser()
        response = maquina_request(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

        request.user = self.userSinPermisos
        response = maquina_request(request)
        self.assertEqual(response.status_code, 401, "No debe estar autorizado")

    def test_MaquinaInexistente(self):
        """Comprueba que un usario no pueda solicitar una Maquina que no exista.

                """
        try:
            Maquina.objects.get(pk = '0', activa = True)
            self.fail("No deberia poder crear nada")
        except ObjectDoesNotExist:
            pass

    def test_crearSolicitud(self):
        """Comprueba que un usario pueda solicitar maquinas.

                        """
        self.data = {
            "fechaInicial": "2017-06-02",
            "fechaFinal"  : "2017-06-08",
            "step"        : "1"
        }
        request = self.factory.post('/Maquina/solicitar', data = self.data)
        request.user = self.user
        request.GET = request.GET.copy()
        request.GET['id'] = 1
        maquina_request(request)
        sMaquina = SolicitudMaquina.objects.filter(maquina = self.maquinaPrueba).exists()
        self.assertEqual(sMaquina, False, "La solicitud no fue creada")

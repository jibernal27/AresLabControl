# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.http import Http404
from django.test import Client
from django.test import RequestFactory
from django.test import TestCase

from LabModule.models import LaboratorioProfile
from LabModule.models import MaquinaEnLab
from LabModule.models import MaquinaProfile
from LabModule.views import maquina_add
from LabModule.views import maquina_list
from LabModule.views import maquina_update
from LabModule.views import muestra_list
from django.core.management.base import BaseCommand
import unittest
from django.core.urlresolvers import reverse


c = Client(HTTP_USER_AGENT = 'Mozilla/5.0')
CONTRASENA = getattr(settings, "CONTRASENA")




class Command(BaseCommand):
    help = """
    If you need Arguments, please check other modules in 
    django/core/management/commands.
    """

    def handle(self, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(ListarMuestras)
        unittest.TextTestRunner().run(suite)
        

class ListarMuestras(TestCase):
    """Hisotria de usuario desarrollada con TDD
        Se encarga de:
            * Comprobar que un asistente de laboratorio pueda listar y filtrar muestras
            * Comporbar que solo los autorizados vean las muestras.
    """
    def setUp(self):
        """Inicia el estado del test
            Se encarga de :
                * Loguearse con un usario existente
        """
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.anomimus=AnonymousUser()
        self.client = Client(HTTP_USER_AGENT = 'Mozilla/5.0')
        self.client.login(username='mgalindo',password=CONTRASENA)
    

    def test_IngresarURL(self):
        """Inicia el estado del test
            Se encarga de :
                * Crear un usario y darle los permisos de agregar y editar
                * Crear un laboratorio
                * Definir varias máquinas que serviran para probar la lógica del negocio
        """
        #request=self.factory.get('url muestra-list')
        #request.user=self.anomimus
        #response = muestra_list(request)
        response = self.client.get(reverse('muestra-list'))
        self.assertEqual(response.status_code, 200, "Debe ser capaz de acceder a la URL")

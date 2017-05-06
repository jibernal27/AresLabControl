# -*- coding: utf-8 -*-
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Mueble(models.Model):
    class Meta:
        verbose_name = _("Mueble")
        verbose_name_plural = _('Muebles')
        app_label = 'LabModule'

    idSistema = models.CharField(
            max_length = 20,
            default = '',
            verbose_name = _("Identificación"),
            null = False,
            primary_key = True
    )

    nombre = models.CharField(
            max_length = 100,
            default = '',
            verbose_name = _("Nombre"),
            null = False
    )

    descripcion = models.CharField(
            max_length = 1000,
            default = '',
            verbose_name = _("Descripción"),
            null = True
    )

    estado = models.CharField(
            max_length = 100,
            default = '',
            verbose_name = _('Estado'),
            null = True
    )

    imagen = models.ImageField(
            upload_to = 'images',
            verbose_name = _("Imagen"),
            default = 'images/image-not-found.jpg'
    )

    def __unicode__(self):
        return self.idSistema + " " + self.nombre

    def get_idSistema(self):
        return self.idSistema.capitalize()

    def get_nombre(self):
        return self.nombre.capitalize()

    def get_descripcion(self):
        return self.descripcion.capitalize()

    def get_estado(self):
        return self.estado

    def get_absolute_url(self):
        return reverse('author-detail', kwargs = {'pk': self.pk})
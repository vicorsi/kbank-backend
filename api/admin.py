from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from api import models


admin.site.register(models.Usuario)
admin.site.register(models.Conta)
admin.site.register(models.Transferencia)
admin.site.register(models.Movimentacao)
admin.site.register(models.Contato)
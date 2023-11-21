from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from api import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['id', 'nome_sobrenome', 'cpf']
    fieldsets = (
        (None, {'fields': ('email', 'senha',)}),
        (_('Informações Pessoais'), {'fields': ('nome_sobrenome', 'cpf',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Datas'), {'fields': ('created_at',)}),
    )
    readonly_fields = ['created_at']
    filter_horizontal = []  # Remova ou adicione os campos corretos aqui

    list_filter = (
        'is_active',
        'is_staff',
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'nome_sobrenome',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )

admin.site.register(models.Usuario, UserAdmin)

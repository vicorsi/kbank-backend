import os
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone

def user_image_field(instace, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'avatar', filename)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fiels):
        if not email:
            raise ValueError("O usuário precisa de um e-mail")

        user = self.model(email=self.normalize_email(email), **extra_fiels)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    cpf = models.CharField(max_length=11, unique=True)
    url_image = models.ImageField(null=True, upload_to=user_image_field)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

class Endereco(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_endereco = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    endereco_logradouro = models.CharField(max_length=10, blank=False, null=False)
    endereco_bairro = models.CharField(max_length=30, blank=False, null=False)
    endereco_cidade = models.CharField(max_length=30, blank=False, null=False)
    endereco_rua = models.CharField(max_length=20, blank=False, null=False)
    endereco_uf = models.CharField(max_length=2, blank=False, null=False)
    endereco_cep = models.CharField(max_length=8, blank=False, null=False)


class ClientePf(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_pf_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cliente_cpf = models.CharField(max_length=15, blank=False, null=False, unique=True)
    cliente_rg = models.CharField(max_length=15, blank=False, null=False, unique=True)


class ClientePj(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_pj_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cliente_cnpj = models.CharField(max_length=25, blank=False, null=False)
    inscricao_estadual = models.CharField(max_length=11, blank=True)


class Contato(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contato_numero = models.CharField(max_length=15, blank=False, null=False, unique=True)
    contato_email = models.EmailField(max_length=50, blank=False, null=False, unique=True)


class Conta(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conta_agencia = models.CharField(max_length=4, blank=False, null=False, default=9090)
    conta_numero = models.CharField(max_length=8, blank=False, null=False, unique=True)
    conta_tipo = models.CharField(max_length=20, blank=False, null=False, default='Standart')
    conta_saldo = models.FloatField(max_length=20, default=0.00, null=False, blank=False)
    created_at = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.conta_agencia} - {self.conta_numero}'


class Cartao(models.Model):
    id = models.AutoField(primary_key=True)
    conta_id = models.ForeignKey(Conta, on_delete=models.CASCADE)
    cartao_numero = models.CharField(max_length=19, blank=False, null=False, unique=True)
    cartao_cvv = models.CharField(max_length=3, blank=False, null=False)
    cartao_validade = models.DateField(blank=False, null=False)
    cartao_bandeira = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.conta_id


class Transferencia(models.Model):
    conta_id_origem = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='conta_origem')
    conta_id_destino = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='conta_destino')
    valor = models.FloatField()
    observacao = models.TextField(max_length=100, blank=True)
    tipo_transferencia = models.CharField(max_length=20)



class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    conta_id = models.ForeignKey(Conta, on_delete=models.CASCADE)
    transferencia = models.ForeignKey(Transferencia, on_delete=models.CASCADE)
    movimentacao_valor = models.FloatField()
    movimentacao_observacao = models.TextField(max_length=100)
    

class Emprestimo(models.Model):
    id = models.AutoField(primary_key=True)
    conta_id = models.ForeignKey(Conta, on_delete=models.CASCADE)
    emprestimo_valor = models.FloatField(blank=False, null=False)
    emprestimo_juros = models.FloatField(blank=False, null=False)
    emprestimo_quantidade_parcelas = models.IntegerField(blank=False, null=False)
    emprestimo_observacao = models.TextField(max_length=100)


class Investimento(models.Model):
    id = models.AutoField(primary_key=True)
    conta_id = models.ForeignKey(Conta, on_delete=models.CASCADE)
    investimento_aporte = models.FloatField(blank=False, null=False)
    investimento_prazo = models.DateField(blank=True)
    investimento_observacao = models.TextField(max_length=100)

class Extrato(models.Model):
    conta_id = models.ForeignKey('Conta', on_delete=models.CASCADE)
    data_transacao = models.DateTimeField(auto_now_add=True)
    tipo_transacao = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.conta_id} - {self.tipo_transacao} - {self.data_transacao}"
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.utils import timezone

class UserManager(BaseUserManager):

    def created_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Usuário precisa de um email")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def created_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Usuario(models.Model):
    nome_sobrenome = models.CharField(max_length=20, blank=False, null=False)
    data_nascimento = models.DateField(null=False, blank=False)
    email = models.EmailField(blank=False, null=False)
    cpf = models.CharField(max_length=11, unique=True, null=False)
    is_active = models.BooleanField(default=True)
    # url_imagem = models.ImageField(null=True, upload_to=user_image_field)
    senha = models.CharField(max_length=10, blank=False, null=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.nome_sobrenome


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
    cliente_pj_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cliente_cnpj = models.CharField(max_length=25, blank=False, null=False)
    inscricao_estadual = models.CharField(max_length=11, blank=True)


class Contato(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contato_numero = models.CharField(max_length=15, blank=False, null=False, unique=True)
    contato_email = models.EmailField(max_length=50, blank=False, null=False, unique=True)


class Conta(models.Model):
    id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    conta_agencia = models.CharField(max_length=5, blank=False, null=False, default=9090)
    conta_numero = models.CharField(max_length=20, blank=False, null=False, unique=True)
    conta_tipo = models.CharField(max_length=20, blank=False, null=False, default='Standart')
    conta_limite = models.FloatField(max_length=20)
    conta_saldo = models.FloatField(max_length=20, default=0.00, null=False, blank=False)
    conta_ativa = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.cliente_id)


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
    id = models.AutoField(primary_key=True)
    conta_id_origem = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='conta_id_origem')
    conta_id_destino = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='conta_id_destino')
    valor = models.FloatField(max_length=20, blank=False, null=False)
    observacao = models.TextField(max_length=100, blank=True)
    tipo_transferencia = models.CharField(max_length=20)


class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    conta_id = models.ForeignKey(Conta, on_delete=models.CASCADE, null=True, blank=True)
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
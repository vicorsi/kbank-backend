from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers
from .models import *


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'
        many = True


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name', 'cpf', 'created_at', 'url_image']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def updated(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()

        return user


class ClientePfSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientePf
        fields = '__all__'
        many = True


class ClientePjSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientePj
        fields = '__all__'
        many = True


class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields = '__all__'
        many = True


class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = ['id', 'conta_agencia', 'conta_numero', 'conta_saldo', 'conta_tipo']
        read_only_fields = ['conta_numero', 'conta_saldo']


class ContaDetailSerializer(serializers.ModelSerializer):
    class Meta(ContaSerializer.Meta):   
        fields = ['id', 'conta_saldo', 'conta_tipo', 'created_at', 'conta_numero',]
        read_only_fields = ContaSerializer.Meta.read_only_fields + ['id', 'conta_saldo', 'conta_tipo', 'created_at', 'conta_numero',]

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartao
        fields = '__all__'

class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = '__all__'
        many = True


class EmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = '__all__'
        many = True


class InvestimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investimento
        fields = '__all__'
        many = True


class DepositoSerializer(serializers.Serializer):
    value = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        fields = ['value']


class SaqueSerializer(serializers.Serializer):
    value = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        fields = ['value']


class TransferenciaSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Transferencia
        fields = ['conta_id_origem', 'conta_id_destino', 'valor', 'observacao', 'tipo_transferencia']


class ExtratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extrato
        fields = ['conta_id', 'tipo_transacao', 'valor', 'created_at']
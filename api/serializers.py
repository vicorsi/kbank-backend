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
        model = Usuario
        fields = '__all__'
        many = True
        extra_kwargs = {
            'senha': {'write_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        return get_user_model().objects.created_user(**validated_data)
    
    def updated(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user - super().update(instance, validated_data)

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
        fields = '__all__'
        many = True

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartao
        fields = '__all__'
        many = True

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

class TransferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transferencia
        fields = '__all__'
        many = True
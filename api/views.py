from django.shortcuts import render
from .models import *
from .serializers import *

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT
from serializers import UsuarioSerializer
from permissions import IsCreationOrIsAuthenticated

class CreateUserView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer

class ManagerUserAPiView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = UsuarioSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsCreationOrIsAuthenticated]

    def get_object(self):
        return self.request.user

class EnderecoView(ModelViewSet):
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer

class UsuarioView(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class ClientePfView(ModelViewSet):
    queryset = ClientePf.objects.all()
    serializer_class = ClientePfSerializer

class ClientePjView(ModelViewSet):
    queryset = ClientePj.objects.all()
    serializer_class = ClientePjSerializer


class ContatoView(ModelViewSet):
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer

class ContaView(ModelViewSet):
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer

class CartaoView(ModelViewSet):
    queryset = Cartao.objects.all()
    serializer_class = CartaoSerializer

class MovimentacaoView(ModelViewSet):
    queryset = Movimentacao.objects.all()
    serializer_class = MovimentacaoSerializer

class EmprestimoView(ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer

class InvestimentoView(ModelViewSet):
    queryset = Investimento.objects.all()
    serializer_class = InvestimentoSerializer

class TransferenciaView(ModelViewSet):
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer
from django.shortcuts import render
from .models import *
from .serializers import *

import random

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT
from .serializers import UsuarioSerializer
from .permissions import IsCreationOrIsAuthenticated
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication as authenticationJWT

class CreateUserView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer


class ManagerUserAPiView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = UsuarioSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsCreationOrIsAuthenticated]

    def get_object(self):
        return self.request.user

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    authentication_classes = [authenticationJWT.JWTAuthentication]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-created_at').distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContaDetailSerializer
        
        return ContaSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            agencia = '9090'
            numero = ''
            for i in range(8):
                numero += str(random.randint(0,9))
            conta = Conta(
                cliente_id = self.request.user,
                numero = numero,
                agencia = agencia,
            )
            conta.save()

            serialized_conta = self.serializer_class(conta)

            return Response({conta}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
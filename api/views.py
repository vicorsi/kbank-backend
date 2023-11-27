from django.shortcuts import render
from .models import *
from .serializers import *
from decimal import Decimal

from .serializers import SaqueSerializer
from .serializers import DepositoSerializer
from .serializers import TransferenciaSerializer

import random
import decimal

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
    serializer_class = ContaSerializer

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(
            cliente_id=self.request.user
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
            saldo = 0
            conta_tipo = 'Standart'
            for i in range(8):
                numero += str(random.randint(0,9))
            conta = Conta(
                cliente_id=self.request.user,
                conta_agencia=agencia,
                conta_numero=numero,
                conta_saldo=saldo,
                conta_tipo=conta_tipo   
            )

            conta.saldo = decimal.Decimal(0)
            conta.save()


            return Response({'message': 'created'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['POST'], detail=True, url_path='sacar')
    def sacar(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()

        if conta:
            serializer_recebido = SaqueSerializer(data=request.data)
            if serializer_recebido.is_valid():
                valor_saque = decimal.Decimal(serializer_recebido.validated_data.get('value'))
                saldo = decimal.Decimal(conta.conta_saldo)

                if saldo >= valor_saque:
                    novo_saldo = saldo - valor_saque
                    conta.conta_saldo = novo_saldo
                    conta.save()

                    return Response({"saldo": conta.conta_saldo}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "Saldo insuficiente"}, status=status.HTTP_403_FORBIDDEN)

        return Response({'message': "Conta não encontrada"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(methods=['POST'], detail=True, url_path='depositar')
    def depositar(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()
        serializer_recebido = DepositoSerializer(data=request.data)

        if conta and serializer_recebido.is_valid():
            valor_depositado = decimal.Decimal(serializer_recebido.validated_data.get('value'))
            saldo = decimal.Decimal(conta.conta_saldo)
            novo_saldo = saldo + valor_depositado

            conta.conta_saldo = novo_saldo
            conta.save()

            return Response({"saldo": conta.conta_saldo}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_recebido.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': "Conta não encontrada"}, status=status.HTTP_404_NOT_FOUND)


    @action(methods=['POST'], detail=False, url_path='transferir')
    def transferir(self, request):
        serializer = TransferenciaSerializer(data=request.data)
        if serializer.is_valid():
            conta_origem_id = serializer.validated_data.get('conta_id_origem')
            conta_destino_id = serializer.validated_data.get('conta_id_destino')
            valor_transferencia = Decimal(serializer.validated_data.get('valor'))

            try:
                conta_origem = Conta.objects.get(id=conta_origem_id)
                conta_destino = Conta.objects.get(id=conta_destino_id)
            except Conta.DoesNotExist:
                return Response({'message': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            if conta_origem.conta_saldo >= valor_transferencia:
                conta_origem.conta_saldo -= valor_transferencia
                conta_destino.conta_saldo += valor_transferencia

                conta_origem.save()
                conta_destino.save()

                Transferencia.objects.create(
                    conta_id_origem=conta_origem,
                    conta_id_destino=conta_destino,
                    valor=valor_transferencia,
                    observacao=serializer.validated_data.get('observacao', ''),
                    tipo_transferencia=serializer.validated_data.get('tipo_transferencia', '')
                )

                return Response({'message': 'Transferência realizada com sucesso'}, status=status.HTTP_200_OK)

            else:
                return Response({'message': 'Saldo insuficiente na conta de origem'}, status=status.HTTP_403_FORBIDDEN)

        else:
            return Response({'message': 'Erro na requisição de transferência'}, status=status.HTTP_400_BAD_REQUEST)

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
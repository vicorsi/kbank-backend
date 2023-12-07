from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from .models import *
from .serializers import *
from decimal import Decimal

from .serializers import SaqueSerializer
from .serializers import DepositoSerializer
from .serializers import TransferenciaSerializer

import random
import decimal

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT
from .serializers import UsuarioSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication as authenticationJWT

class CreateUserView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer


class ManagerUserAPiView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = UsuarioSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]

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

        if conta:
            if serializer_recebido.is_valid():
                valor_depositado = decimal.Decimal(serializer_recebido.validated_data.get('value'))
                saldo = decimal.Decimal(conta.conta_saldo)
                novo_saldo = saldo + valor_depositado

                conta.conta_saldo = novo_saldo
                conta.save()

                return Response({"saldo": conta.conta_saldo}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer_recebido.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Conta não encontrada"}, status=status.HTTP_404_NOT_FOUND)


    @action(methods=['POST'], detail=True, url_path='transferir')
    def transferir(self, request, pk=None):
        conta_destino = get_object_or_404(Conta, id=pk)

        conta_origem = self.request.user.conta_set.first()

        valor_transferencia = Decimal(request.data.get('valor', 0))

        if conta_origem and conta_destino:
            if conta_origem.conta_saldo >= valor_transferencia:
                conta_origem.conta_saldo = Decimal(str(conta_origem.conta_saldo)) - valor_transferencia

                conta_destino.conta_saldo = Decimal(str(conta_destino.conta_saldo)) + valor_transferencia

                conta_origem.save()
                conta_destino.save()

                Transferencia.objects.create(
                    conta_id_origem=conta_origem,
                    conta_id_destino=conta_destino,
                    valor=valor_transferencia,
                    observacao=request.data.get('observacao', ''),
                    tipo_transferencia=request.data.get('tipo_transferencia', '')
                )

                return Response({'message': 'Transferência realizada com sucesso'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Saldo insuficiente na conta de origem'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'Contas não encontradas'}, status=status.HTTP_404_NOT_FOUND) 
        

    @action(methods=['POST'], detail=True, url_path='emprestar')
    def emprestar(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()

        if conta:
            serializer = EmprestimoSerializer(data=request.data)

            if serializer.is_valid():
                valor_emprestimo = Decimal(serializer.validated_data.get('emprestimo_valor'))
                quantidade_parcelas = serializer.validated_data.get('emprestimo_quantidade_parcelas')
                observacao = serializer.validated_data.get('emprestimo_observacao', '')

                with transaction.atomic():
                    conta.conta_saldo = float(conta.conta_saldo) + float(valor_emprestimo)
                    conta.save()

                    Emprestimo.objects.create(
                        conta_id=conta,
                        emprestimo_valor=float(valor_emprestimo),
                        emprestimo_quantidade_parcelas=quantidade_parcelas,
                        emprestimo_observacao=observacao
                    )

                return Response({'message': 'Empréstimo realizado com sucesso'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=True, url_path='cartao')
    def criarCartao(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()

        if not conta:
            return Response({'error': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if conta.conta_saldo <= 1000:
            return Response({'error': 'Saldo insuficiente para criar um cartão'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartaoSerializer(data=request.data)

        if serializer.is_valid():
            cartao_numero = ''.join(str(random.randint(0, 9)) for _ in range(16))
            cartao_cvv = ''.join(str(random.randint(0, 9)) for _ in range(3))
            cartao_validade = '2025-12-07'
            cartao_bandeira = 'Mastercard'

            with transaction.atomic():
                conta.conta_saldo -= 1000
                conta.save()

                cartao = Cartao(
                    conta_id=conta,
                    cartao_numero=cartao_numero,
                    cartao_cvv=cartao_cvv,
                    cartao_validade=cartao_validade,
                    cartao_bandeira=cartao_bandeira
                )

                cartao.save()

            return Response({'success': 'Cartão criado'}, status=status.HTTP_201_CREATED)

        return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['GET'], detail=True, url_path='get/cartao')
    def obterCartao(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()

        if not conta:
            return Response({'error': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        cartao = Cartao.objects.filter(conta_id=conta).first()

        if not cartao:
            return Response({'error': 'Cartão não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartaoSerializer(cartao)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=True, url_path='comprar/credito')
    def realizar_compra(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()

        if not conta:
            return Response({'message': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RealizarCompraSerializer(data=request.data)

        if serializer.is_valid():
            valor_compra = Decimal(serializer.validated_data.get('valor'))

            cartao = Cartao.objects.filter(conta_id=conta).first()

            if not cartao:
                return Response({'error': 'Cartão não encontrado'}, status=status.HTTP_404_NOT_FOUND)

            cartao.cartao_saldo -= float(valor_compra)
            cartao.save()

            Extrato.objects.create(
                conta_id=conta,
                tipo_transacao='Compra',
                valor=valor_compra,
            )

            return Response({'message': 'Compra realizada com sucesso'}, status=status.HTTP_200_OK)

        return Response({'error': 'Dados inválidos', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# ...


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

class ExtratoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExtratoSerializer

    def get(self, request):
        usuario = request.user

        emprestimos = Emprestimo.objects.filter(conta_id__cliente_id=usuario)
        transferencias_origem = Transferencia.objects.filter(conta_id_origem__cliente_id=usuario)
        transferencias_destino = Transferencia.objects.filter(conta_id_destino__cliente_id=usuario)
        saques = Movimentacao.objects.filter(movimentacao_observacao='Saque', conta_id__cliente_id=usuario)
        depositos = Movimentacao.objects.filter(movimentacao_observacao='Depósito', conta_id__cliente_id=usuario)
        
        ultima_data_extrato = Extrato.objects.filter(conta_id__cliente_id=usuario).order_by('-created_at').first()

        for emprestimo in emprestimos:
            if not ultima_data_extrato or emprestimo.created_at > ultima_data_extrato.created_at:
                Extrato.objects.create(
                    conta_id=emprestimo.conta_id,
                    tipo_transacao='Emprestimo',
                    valor=emprestimo.emprestimo_valor
                )

        for transferencia_origem in transferencias_origem:
            if not ultima_data_extrato or transferencia_origem.created_at > ultima_data_extrato.created_at:
                Extrato.objects.create(
                    conta_id=transferencia_origem.conta_id_origem,
                    tipo_transacao='Transferência Entre Contas',
                    valor=transferencia_origem.valor
                )

        for transferencia_destino in transferencias_destino:
            if not ultima_data_extrato or transferencia_destino.created_at > ultima_data_extrato.created_at:
                Extrato.objects.create(
                    conta_id=transferencia_destino.conta_id_destino,
                    tipo_transacao='Transferência Entre Contas',
                    valor=transferencia_destino.valor
                )

        for saque in saques:
            if not ultima_data_extrato or saque.created_at > ultima_data_extrato.created_at:
                Extrato.objects.create(
                    conta_id=saque.conta_id,
                    tipo_transacao='Saque',
                    valor=saque.movimentacao_valor,
                    movimentacao_tipo='Saque'
                )

        for deposito in depositos:
            if not ultima_data_extrato or deposito.created_at > ultima_data_extrato.created_at:
                Extrato.objects.create(
                    conta_id=deposito.conta_id,
                    tipo_transacao='Depósito',
                    valor=deposito.movimentacao_valor,
                    movimentacao_tipo='Depósito'
                )

        extrato = Extrato.objects.filter(conta_id__cliente_id=usuario)
        extrato_serializado = self.serializer_class(extrato, many=True).data

        return Response({'extrato': extrato_serializado}, status=status.HTTP_200_OK)
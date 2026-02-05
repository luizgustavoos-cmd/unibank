# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # O OneToOneField garante que cada Usuário tenha exatamente um Profile.
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    
    # Campo para armazenar o número de telefone (apenas dígitos, validado no form)
    telefone = models.CharField(max_length=15, blank=False, null=False, unique=True) 
    
    # Campo para o saldo inicial de 0 reais
    saldo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00 # Saldo inicial de 0 reais
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'
    
class Transacao(models.Model):
    remetente = models.ForeignKey(User, related_name='transferencias_enviadas', on_delete=models.CASCADE)
    destinatario = models.ForeignKey(User, related_name='transferencias_recebidas', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.remetente} -> {self.destinatario}: R$ {self.valor}"
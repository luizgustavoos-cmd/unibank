from django import forms
from django.contrib.auth.models import User
import re
from django.contrib.auth.forms import AuthenticationForm 
from .models import Profile


class CadastroForm(forms.Form):
    username = forms.CharField(label='Nome de usuário', max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nome de usuário...'}))

    email = forms.EmailField(label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email...'}))

    telefone = forms.CharField(label='Telefone', max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Telefone (DDD) 9XXXX-XXXX...'}))

    senha = forms.CharField(label='Senha', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha...', 'id': 'senha'})) # ID para o JS do olho

    senha_confirmacao = forms.CharField(label='Confirmar Senha', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Senha...', 'id': 'confirmacao_senha'})) # ID para o JS
    


    #Validação de Telefone, E-mail e Confirmação de Senha
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Verifica se o nome de usuário já está cadastrado
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username
    
    def clean_telefone(self):
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'[^0-9]', '', self.cleaned_data['telefone']) # Alterei o nome da variável
        
        # Expressão regular para validar o formato brasileiro (10 ou 11 dígitos, com DDD)
        if not re.match(r'^\d{10,11}$', telefone_limpo):
            raise forms.ValidationError("Número de telefone inválido. Use o formato com DDD, ex: (11) 99999-9999 ou (11) 3333-3333.")
        
        # 2. ADICIONE A VERIFICAÇÃO DE UNICIDADE
        if Profile.objects.filter(telefone=telefone_limpo).exists():
            raise forms.ValidationError("Este número de telefone já está cadastrado em outra conta.")
            
        return telefone_limpo # Retorna apenas os dígitos para armazenamento
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica se o e-mail já está cadastrado
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        """Validação de Confirmação de Senha e E-mail Duplicado."""
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        senha_confirmacao = cleaned_data.get("senha_confirmacao")

        # Verifica se as senhas coincidem
        if senha and senha_confirmacao and senha != senha_confirmacao:
            self.add_error('senha_confirmacao', "As senhas não coincidem.")

        return cleaned_data
    
    #Formatação Padrão na Exibição

    def formatar_telefone(self, numero_telefone):
        """Formata o número de telefone para o padrão (XX) XXXX-XXXX ou (XX) 9XXXX-XXXX."""
        if not numero_telefone:
            return ""

        # Remove caracteres não numéricos
        digitos = re.sub(r'[^0-9]', '', numero_telefone)
        
        # Aplica a formatação
        if len(digitos) == 11:
            # (XX) 9XXXX-XXXX
            return f'({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}'
        elif len(digitos) == 10:
            # (XX) XXXX-XXXX
            return f'({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}'
        return numero_telefone
    



class LoginForm(AuthenticationForm):
    # Sobrescrevemos os campos para adicionar os atributos necessários para o seu CSS/HTML
    username = forms.CharField(
        label='Nome de usuário',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome de usuário...',
           
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Senha...',
            'id': 'senha_login' # Usaremos este ID para o JavaScript do 'olho'
        })
    )
    
    
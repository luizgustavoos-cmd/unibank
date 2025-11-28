from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required

# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        email = User.objects.filter(email=email).first()

        if email:
            return HttpResponse('Email já cadastrado!') 
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        user.save()

        return HttpResponse(f'Usuário {username} cadastrado com sucesso!')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            auth_login(request, user)
            return HttpResponse(f'Usuário {username} autenticado com sucesso!')
        else:
            return HttpResponse('Credenciais inválidas!')


@login_required(login_url='/auth/login/')
def plataforma(request):
    return HttpResponse('Bem-vindo à plataforma Unibank!')
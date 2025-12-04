from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CadastroForm 
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .forms import LoginForm 
from django.contrib.auth import logout



from .models import Profile # <--- IMPORTANTE: Importar o novo modelo Profile

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            # Obtém o telefone VALIDADO (somente dígitos)
            telefone_clean = form.cleaned_data['telefone'] 
            
            # 1. Cria o objeto User
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=senha
            )
            user.save()

            # 2. Cria o objeto Profile e associa ao User
            # O Saldo (saldo=0.00) é definido por padrão no models.py, 
            # mas podemos setar explicitamente aqui se quisermos.
            Profile.objects.create(
                user=user, 
                telefone=telefone_clean, 
                saldo=0.00 # Define o saldo inicial de 0.00
            )
            
            # Formatamos o telefone apenas para a mensagem de sucesso
            telefone_formatado = form.formatar_telefone(telefone_clean)
            
            messages.success(request, f'Usuário {username} cadastrado com sucesso! Telefone: {telefone_formatado}')
            
            return redirect('login') 
        
    else:
        form = CadastroForm()

    return render(request, 'cadastro.html', {'form': form})



def login(request):



    if request.method == 'POST':
        # Instancia o formulário com os dados POST
        form = LoginForm(request=request, data=request.POST) 
        
        if form.is_valid():
            # is_valid() já autentica o usuário internamente
            user = form.get_user()
            auth_login(request, user)
            
            messages.success(request, f'Bem-vindo(a), {user.username}!')
        
            return redirect('adm_inicio')
        else:
            # Se o formulário for inválido (credenciais erradas), o Django Messages 
            # não adiciona a mensagem automaticamente, mas o form.errors contém a informação.
            # Vamos usar o messages.error manualmente para manter o estilo do pop-up.
            messages.error(request, 'Credenciais inválidas. Verifique seu nome de usuário e senha.')
            
    else:
        # Método GET: Exibe o formulário vazio
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin, login_url='/auth/home_page/')
def adm_inicio(request):
    """
    Exibe a lista de todos os usuários (perfis) para a área administrativa.
    """
    # Busca todos os perfis, otimizando a consulta para incluir os dados do User.
    perfis = Profile.objects.select_related('user').all().order_by('user__username')
    
    context = {
        'perfis': perfis
    }
    

    return render(request, 'adm_inicio.html', context)

@login_required
def home_page(request):
    """
    Exibe a página inicial para usuários autenticados.
    """
    return render(request, 'home_page.html')

def custom_logout_view(request):
    """
    Desloga o usuário e adiciona uma mensagem de sucesso para ser exibida 
    na próxima página (a tela de login).
    """
    if request.user.is_authenticated:
        # 1. Adiciona a mensagem de sucesso antes de deslogar
        messages.success(request, "Sua sessão foi encerrada com sucesso.")
        
        # 2. Desloga o usuário
        logout(request)
        
    # 3. Redireciona para a página de login
    # Certifique-se de que sua URL de login tenha o nome 'login'
    return redirect('login')



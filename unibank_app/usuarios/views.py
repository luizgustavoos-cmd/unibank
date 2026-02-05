from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CadastroForm 
from django.contrib.auth import authenticate, login as auth_login,update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .forms import LoginForm 
from django.db import transaction
from .models import Transacao
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

# usuarios/views.py (Adicione esta nova importação, se ainda não tiver)
from django.contrib.auth import update_session_auth_hash 

# ... (outras views) ...

@login_required
@user_passes_test(is_admin, login_url='/auth/home_page/')
def adm_editar_usuario(request, user_id):
    try:
        user_to_edit = User.objects.get(pk=user_id)
        profile_to_edit = user_to_edit.profile
    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect('adm_inicio')

    if request.method == 'POST':
        # Assumindo que os dados vieram do modal com nomes de campo específicos
        username_novo = request.POST.get('username')
        email_novo = request.POST.get('email')
        telefone_novo = request.POST.get('telefone')
        saldo_novo = request.POST.get('saldo') # Novo campo
        senha_nova = request.POST.get('senha')
        
        # 1. Atualizar User
        user_to_edit.username = username_novo
        user_to_edit.email = email_novo
        
        # 2. Atualizar Senha (somente se uma nova senha for fornecida)
        if senha_nova:
            user_to_edit.set_password(senha_nova)
            # Se o admin edita a si mesmo, a sessão deve ser atualizada para evitar logout
            if user_to_edit == request.user:
                update_session_auth_hash(request, user_to_edit)
                
        user_to_edit.save()
        
        # 3. Atualizar Profile
        profile_to_edit.telefone = telefone_novo
        
        # Garante que o saldo seja tratado como float
        try:
            profile_to_edit.saldo = float(saldo_novo)
        except (ValueError, TypeError):
            # Tratar erro de saldo inválido, se necessário
            pass

        profile_to_edit.save()
        
        messages.success(request, f"Usuário {username_novo} atualizado com sucesso!")
        return redirect('adm_inicio')

    # Para GET, esta view não é usada (o modal é preenchido via JS/AJAX ou dados iniciais)
    # Mas é bom mantê-la como uma função de POST/redirect
    messages.error(request, "Acesso inválido.")
    return redirect('adm_inicio')


@login_required
@user_passes_test(is_admin, login_url='/auth/home_page/')
def adm_excluir_usuario(request, user_id):
    try:
        user_to_delete = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
        return redirect('adm_inicio')
    
    if user_to_delete == request.user:
        messages.error(request, "Você não pode excluir a sua própria conta de administrador.")
        return redirect('adm_inicio')

    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"Usuário '{username}' excluído permanentemente.")
        return redirect('adm_inicio')

    messages.error(request, "Acesso inválido.")
    return redirect('adm_inicio')

def transferir(request):
    if request.method == 'POST':
        username_destinatario = request.POST.get('destinatario')
        valor = float(request.POST.get('valor').replace(',', '.')) # Converte vírgula em ponto
        
        try:
            destinatario = User.objects.get(username=username_destinatario)
            remetente = request.user
            
            # Verificações de segurança
            if remetente == destinatario:
                messages.error(request, "Você não pode transferir para si mesmo.")
            elif remetente.profile.saldo >= valor:
                with transaction.atomic():
                    # 1. Tira do remetente
                    remetente.profile.saldo -= valor
                    remetente.profile.save()
                    
                    # 2. Adiciona ao destinatário
                    destinatario.profile.saldo += valor
                    destinatario.profile.save()
                    
                    # 3. Registra a transação
                    Transacao.objects.create(
                        remetente=remetente,
                        destinatario=destinatario,
                        valor=valor
                    )
                messages.success(request, f"Transferência de R$ {valor:.2f} realizada com sucesso!")
                return redirect('home_page')
            else:
                messages.error(request, "Saldo insuficiente.")
                
        except User.DoesNotExist:
            messages.error(request, "Usuário destinatário não encontrado.")
            
    return render(request, 'transferir.html')
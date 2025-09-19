from datetime import date, timedelta
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout

from .models import Colaborador, Insumo, ProdutoPronto, SaidaInsumo
from .forms import ColaboradorForm, InsumoForm, ProdutoProntoForm, SaidaInsumoForm

# ---------- DECORATOR DE PERMISSÃO ----------


def check_group(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser or request.user.groups.filter(name="Administrador").exists():
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, "Seu login não tem acesso a este recurso.")
            return redirect("home")
        return _wrapped_view
    return decorator

# ---------- LOGIN / LOGOUT ----------


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser or user.groups.filter(name="Administrador").exists():
                return redirect("home")
            elif user.groups.filter(name="RH").exists():
                return redirect("colaboradores_list")
            elif user.groups.filter(name="Insumos").exists():
                return redirect("insumos_list")
            elif user.groups.filter(name="Confeitaria").exists():
                return redirect("produtos_list")
            else:
                messages.error(request, "Usuário sem grupo definido.")
                return redirect("login")
        else:
            messages.error(request, "Usuário ou senha incorretos.")
            return redirect("login")
    users_exist = User.objects.exists()
    return render(request, "login.html", {"users_exist": users_exist})


def logout_view(request):
    logout(request)
    return redirect('login')

# ---------- HOME ----------


@login_required
def home(request):
    context = {
        "is_admin": request.user.is_superuser or request.user.groups.filter(name="Administrador").exists(),
        "is_rh": request.user.groups.filter(name="RH").exists() or request.user.is_superuser,
        "is_insumo": request.user.groups.filter(name="Insumos").exists() or request.user.is_superuser,
        "is_confeitaria": request.user.groups.filter(name="Confeitaria").exists() or request.user.is_superuser,
    }
    return render(request, "core/home.html", context)

# ---------- USUÁRIOS ----------


@login_required
def listar_usuarios(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()):
        messages.error(
            request, "Você não tem permissão para visualizar usuários.")
        return redirect("home")

    usuarios = User.objects.all().order_by("username")
    return render(request, "core/usuarios_list.html", {"usuarios": usuarios})


@login_required
def usuario_edit(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()):
        messages.error(request, "Você não tem permissão para editar usuários.")
        return redirect("home")

    usuario = get_object_or_404(User, id=id)

    if request.method == "POST":
        username = request.POST.get("username")
        grupo = request.POST.get("grupo")

        # Atualizar username
        if username != usuario.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Esse nome de usuário já está em uso.")
                return redirect("usuario_edit", id=usuario.id)
            usuario.username = username

        # Limpar grupos e adicionar novo grupo
        usuario.groups.clear()
        if grupo in ["RH", "Insumos", "Confeitaria"]:
            grupo_obj, _ = Group.objects.get_or_create(name=grupo)
            usuario.groups.add(grupo_obj)
            usuario.is_superuser = False
            usuario.is_staff = False
        elif grupo == "Administrador":
            usuario.is_superuser = True
            usuario.is_staff = True
        else:
            usuario.is_superuser = False
            usuario.is_staff = False

        usuario.save()
        messages.success(
            request, f"Usuário {usuario.username} atualizado com sucesso!")
        return redirect("listar_usuarios")

    grupo_atual = usuario.groups.first().name if usuario.groups.exists() else (
        "Administrador" if usuario.is_superuser else "")
    return render(request, "core/editar_usuario.html", {"usuario": usuario, "grupo_atual": grupo_atual})


@login_required
def usuario_delete(request, id):
    if not (request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()):
        messages.error(
            request, "Você não tem permissão para deletar usuários.")
        return redirect("home")

    usuario = get_object_or_404(User, id=id)

    # Impedir que o admin se exclua sozinho
    if usuario == request.user:
        messages.error(request, "Você não pode apagar seu próprio usuário.")
        return redirect("home")

    if request.method == "POST":
        usuario.delete()
        messages.success(
            request, f"Usuário {usuario.username} deletado com sucesso!")
        return redirect("listar_usuarios")

    return render(request, "core/delete.html", {"obj": usuario, "tipo": "usuário"})

# ---------- CRIAR USUÁRIO ----------


@login_required
def criar_usuario(request):
    if not request.user.is_superuser:
        messages.error(
            request, "Você não tem permissão para cadastrar usuários.")
        return redirect("home")

    users_exist = User.objects.exists()

    if request.method == "POST":
        username = request.POST.get("username")
        senha_nova = request.POST.get("senha_nova")
        senha_admin = request.POST.get("senha_admin")
        grupo = request.POST.get("grupo")

        if not request.user.check_password(senha_admin):
            messages.error(request, "Senha do administrador incorreta.")
            return render(request, "core/criar_usuario.html", {"users_exist": users_exist})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
        else:
            novo_usuario = User.objects.create_user(
                username=username, password=senha_nova, is_superuser=False)
            if grupo in ["RH", "Insumos", "Confeitaria"]:
                grupo_obj, _ = Group.objects.get_or_create(name=grupo)
                novo_usuario.groups.add(grupo_obj)
            elif grupo == "Administrador":
                novo_usuario.is_superuser = True
                novo_usuario.is_staff = True
                novo_usuario.save()
            messages.success(
                request, f"Usuário {username} criado com sucesso!")

        return render(request, "core/criar_usuario.html", {"users_exist": users_exist})

    return render(request, "core/criar_usuario.html", {"users_exist": users_exist})

# ---------- COLABORADORES ----------


@login_required
@check_group("RH")
def colaboradores_list(request):
    query = request.GET.get('q')
    if query:
        colaboradores = Colaborador.objects.filter(
            nome__icontains=query).order_by('nome')
    else:
        colaboradores = Colaborador.objects.all().order_by('nome')
    return render(request, "core/colaboradores_list.html", {"colaboradores": colaboradores})


@login_required
@check_group("RH")
def colaboradores_create(request):
    form = ColaboradorForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request, f"Colaborador {form.cleaned_data['nome']} cadastrado com sucesso!")
        return redirect("colaboradores_list")
    return render(request, "core/form_colaborador.html", {"form": form, "titulo": "Cadastrar Colaborador"})


@login_required
@check_group("RH")
def colaboradores_edit(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    form = ColaboradorForm(request.POST or None,
                           request.FILES or None, instance=colaborador)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request, f"Colaborador {form.cleaned_data['nome']} atualizado com sucesso!")
        return redirect("colaboradores_list")
    return render(request, "core/form_colaborador.html", {"form": form, "titulo": "Editar Colaborador"})


@login_required
@check_group("RH")
def colaboradores_delete(request, id):
    colaborador = get_object_or_404(Colaborador, id=id)
    if request.method == "POST":
        colaborador.delete()
        messages.success(
            request, f"Colaborador {colaborador.nome} deletado com sucesso!")
        return redirect("colaboradores_list")
    return render(request, "core/delete.html", {"obj": colaborador})

# ---------- INSUMOS ----------


@login_required
@check_group("Insumos")
def insumos_list(request):
    insumos = Insumo.objects.all()
    return render(request, "core/insumos_list.html", {"insumos": insumos})


@login_required
@check_group("Insumos")
def insumos_create(request):
    form = InsumoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("insumos_list")
    return render(request, "core/form.html", {"form": form, "titulo": "Cadastrar Insumo"})


@login_required
@check_group("Insumos")
def insumos_edit(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    form = InsumoForm(request.POST or None, instance=insumo)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("insumos_list")
    return render(request, "core/form.html", {"form": form, "titulo": "Editar Insumo"})


@login_required
@check_group("Insumos")
def insumos_delete(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    if request.method == "POST":
        insumo.delete()
        return redirect("insumos_list")
    return render(request, "core/delete.html", {"obj": insumo})

# ---------- SAÍDA DE INSUMOS ----------


@login_required
@check_group("Insumos")
def saida_insumo_list(request):
    saidas = SaidaInsumo.objects.all().order_by("-data")
    return render(request, "core/saida_insumo_list.html", {"saidas": saidas})


@login_required
@check_group("Insumos")
def saida_insumo_create(request):
    form = SaidaInsumoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            saida = form.save(commit=False)
            insumo = saida.insumo
            if saida.quantidade > insumo.quantidade:
                messages.error(
                    request,
                    f"A quantidade solicitada ({saida.quantidade} {insumo.unidade_base}) excede o estoque disponível ({insumo.quantidade} {insumo.unidade_base}) de {insumo.nome}."
                )
                return render(request, "core/form.html", {"form": form, "titulo": "Registrar Saída de Insumo"})
            insumo.quantidade -= saida.quantidade
            insumo.save()
            saida.save()
            messages.success(
                request, f"Saída de {saida.quantidade} {saida.get_unidade_display()} de {insumo.nome} registrada com sucesso."
            )
            return redirect("saida_insumo_list")
        else:
            messages.error(request, "Verifique os campos e tente novamente.")
    return render(request, "core/form.html", {"form": form, "titulo": "Registrar Saída de Insumo"})


@login_required
@check_group("Insumos")
def saida_insumo_delete(request, id):
    saida = get_object_or_404(SaidaInsumo, id=id)
    if request.method == "POST":
        insumo = saida.insumo
        insumo.quantidade += saida.quantidade
        insumo.save()
        saida.delete()
        messages.success(
            request, "Saída de insumo deletada e estoque atualizado.")
        return redirect("saida_insumo_list")
    return render(request, "core/delete.html", {"obj": saida})

# ---------- PRODUTOS PRONTOS ----------


@login_required
@check_group("Confeitaria")
def produtos_list(request):
    produtos = ProdutoPronto.objects.all()
    hoje = date.today()

    for p in produtos:
        validade = p.data_validade
        if validade is None:
            p.row_class = ""
            continue
        if hasattr(validade, 'date'):
            validade = validade.date()
        if validade < hoje:
            p.row_class = "produto-vencido"
        elif validade == hoje:
            p.row_class = "produto-hoje"
        elif validade <= hoje + timedelta(days=3):
            p.row_class = "produto-proximo"
        else:
            p.row_class = ""

    return render(request, "core/produtos_list.html", {"produtos": produtos})


@login_required
@check_group("Confeitaria")
def produtos_create(request):
    form = ProdutoProntoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("produtos_list")
    return render(request, "core/form.html", {"form": form, "titulo": "Cadastrar Produto Pronto"})


@login_required
@check_group("Confeitaria")
def produtos_edit(request, id):
    produto = get_object_or_404(ProdutoPronto, id=id)
    form = ProdutoProntoForm(request.POST or None, instance=produto)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("produtos_list")
    return render(request, "core/form.html", {"form": form, "titulo": "Editar Produto Pronto"})


@login_required
@check_group("Confeitaria")
def produtos_delete(request, id):
    produto = get_object_or_404(ProdutoPronto, id=id)
    if request.method == "POST":
        produto.delete()
        return redirect("produtos_list")
    return render(request, "core/delete.html", {"obj": produto})

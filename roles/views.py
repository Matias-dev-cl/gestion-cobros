from datetime import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from django.shortcuts import render, redirect

from roles.decorators import role_required
from usuarios.models import Usuario
from tarifas.models import Tarifa
from consumos.models import Consumo
from medidores.models import Medidor
from boletas.models import Boleta


@login_required
@role_required('operario')
def operario_dashboard(request):
    """
    Panel del operario.
    Enfocado en gestión de medidores y registros de consumo.
    """
    total_usuarios = Usuario.objects.count()
    medidores_activos = Medidor.objects.filter(estado="activo").count()

    context = {
        "titulo": "Panel de Gestión - Operario",
        "mensaje_bienvenida": (
            "Bienvenido al panel del operario. "
            "Aquí puedes gestionar consumos y medidores."
        ),
        "total_usuarios": total_usuarios,
        "medidores_activos": medidores_activos,
    }
    return render(request, "roles/operario_dashboard.html", context)


@login_required
@role_required('secretaria')
def secretaria_dashboard(request):
    """
    Dashboard de la secretaria.
    Permite supervisar usuarios, boletas y estado de pagos.
    """
    total_usuarios = Usuario.objects.count()
    boletas_pagadas = Boleta.objects.filter(pagado=True).count()
    boletas_pendientes = Boleta.objects.filter(pagado=False).count()
    medidores_activos = Medidor.objects.filter(estado="activo").count()

    context = {
        "titulo": "Panel de la Secretaria",
        "mensaje_bienvenida": (
            "Bienvenido al panel de gestión de la secretaria. "
            "Aquí puedes supervisar y gestionar usuarios, consumos y boletas."
        ),
        "total_usuarios": total_usuarios,
        "boletas_pagadas": boletas_pagadas,
        "boletas_pendientes": boletas_pendientes,
        "medidores_activos": medidores_activos,
    }
    return render(request, "roles/secretaria_dashboard.html", context)


@login_required
def redireccion_dashboard(request):
    """
    Redirige al usuario al dashboard correspondiente según su rol.
    """
    user = request.user

    if hasattr(user, "rol"):
        if user.rol == "admin":
            return redirect("roles:admin_dashboard")
        elif user.rol == "secretaria":
            return redirect("roles:secretaria_dashboard")
        elif user.rol == "operario":
            return redirect("roles:operario_dashboard")
        else:
            messages.error(request, "Rol inválido. Contacta al administrador.")
    else:
        messages.error(request, "No tienes un rol asignado. Contacta al administrador.")

    return redirect("login:home")


@login_required
@role_required('admin')
def admin_dashboard(request):
    from .dashboard import dashboard_context
    return render(request, "roles/admin_dashboard.html", dashboard_context())

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from sistema.models import Usuario


def login_view(request):
    if request.user.is_authenticated:
        if request.user.tipo == 'socio':
            return redirect('socio:home')
        if request.user.tipo == 'asistente':
            return redirect('asistente:home')
        if request.user.tipo == 'presidente':
            return redirect('presidente:home')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            user.save()
            if request.user.is_active:
                if request.user.tipo == 'socio':
                    return redirect('socio:home')
                elif request.user.tipo == 'administrador':
                    if request.user.is_superuser:
                        return redirect('sistema:home')
                    else:
                        messages.error(request, 'Usted no es superusuario')
                elif request.user.tipo == 'presidente':
                    return redirect('presidente:home')
                elif request.user.tipo == 'asistente':
                    return redirect('asistente:home')
            else:
                messages.error(request, 'El usuario esta desactivado.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'registration/login.html')


def cambiar_password(request):
    bandera = False
    if request.method == 'POST':
        if len(request.POST['new_password2']) < 8:
            bandera = False
            messages.warning(request, "La nueva contraseña debe tener minimo 8 caracteres")
        else:
            bandera = True
        indice = 0
        mayusculas = 0
        minusculas = 0
        while indice < len(request.POST['new_password2']):
            letra = request.POST['new_password2'][indice]
            if letra.isupper() == True:
                mayusculas += 1
            else:
                minusculas += 1
            indice += 1
        if mayusculas < 1:
            bandera = False
            messages.warning(request, "La nueva contraseña debe tener minimo una letra en mayuscula")

        else:
            bandera = True
        if minusculas < 1:
            bandera = False
            messages.warning(request, "La nueva contraseña debe tener minimo una letra en minuscula")

        else:
            bandera = True
        if request.POST['new_password1'] != request.POST['new_password2']:
            bandera = False
            messages.warning(request, "La nueva contraseña no coicide con la confirmacion")

        else:
            bandera = True
        if bandera is True:
            usuario = Usuario.objects.get(id=request.user.id)
            usuario.set_password(request.POST['new_password2'])
            usuario.save()
            messages.success(request, "Contraseña cambiada")
            login(request, usuario)
            return redirect('/')
    return render(request, 'registration/password_change_form.html')

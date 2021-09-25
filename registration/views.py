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

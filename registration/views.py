from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from sistema.models import Usuario


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if Usuario.objects.filter(username=username).exists():
            user = Usuario.objects.get(username=username)
            if user.is_active:
                if user is not None:
                    login(request, user)

                    user.save()

                    if user.tipo == 'socio':
                        return redirect('socio:home')
                    elif user.tipo == 'administrador':
                        return redirect('sistema:home')
                    elif user.tipo == 'presidente':
                        return redirect('presidente:home')
                    elif user.tipo == 'asistente':
                        return redirect('asistente:home')
                else:
                    messages.error(request, 'Usuario o contraseña incorrectos')
            else:
                messages.error(request, 'El usuario esta desactivado')
        else:
            messages.error(request, 'El usuario no existe')
    return render(request, 'registration/login.html')

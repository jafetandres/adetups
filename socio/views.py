from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import render, redirect
from socio.forms import SolicitudCreditoForm
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from sistema.models import SolicitudCredito, Socio, ClaseCredito, Credito, \
    Usuario


class SocioRequiredMixin(AccessMixin):
    """
    Este mixin de seguridad requiere que el usuario sea de tipo socio
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.tipo != 'socio':
            return redirect(reverse_lazy('registration:login'))
        return super(SocioRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomePageView(SocioRequiredMixin, TemplateView):
    template_name = "socio/index.html"

    def get_context_data(self, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.filter(socio_id=socio.id)
        return context


class SolicitudCreditoDetailView(SocioRequiredMixin, DetailView):
    model = SolicitudCredito
    template_name = 'socio/solicitudcredito_detail.html'


def diasHastaFecha(day1, month1, year1, day2, month2, year2):
    # Función para calcular si un año es bisiesto o no

    def esBisiesto(year):
        return year % 4 == 0 and year % 100 != 0 or year % 400 == 0

    # Caso de años diferentes

    if (year1 < year2):

        # Días restante primer año

        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        restoMes = diasMes[month1] - day1

        restoYear = 0
        i = month1 + 1

        while i <= 12:
            restoYear = restoYear + diasMes[i]
            i = i + 1

        primerYear = restoMes + restoYear

        # Suma de días de los años que hay en medio

        sumYear = year1 + 1
        totalDias = 0

        while (sumYear < year2):
            if esBisiesto(sumYear) == False:
                totalDias = totalDias + 365
                sumYear = sumYear + 1
            else:
                totalDias = totalDias + 366
                sumYear = sumYear + 1

        # Dias año actual

        if esBisiesto(year2) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        llevaYear = 0
        lastYear = 0
        i = 1

        while i < month2:
            llevaYear = llevaYear + diasMes[i]
            i = i + 1

        lastYear = day2 + llevaYear

        return totalDias + primerYear + lastYear

    # Si estamos en el mismo año

    else:

        if esBisiesto(year1) == False:
            diasMes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            diasMes = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        llevaYear = 0
        total = 0
        i = month1

        if i < month2:
            while i < month2:
                llevaYear = llevaYear + diasMes[i]
                i = i + 1
            total = day2 + llevaYear - 1
            return total
        else:
            total = day2 - day1
            return total


class SolicitudCreditoCreate(SocioRequiredMixin, CreateView):
    model = SolicitudCredito
    form_class = SolicitudCreditoForm
    template_name = 'socio/solicitudcredito_form.html'
    success_url = reverse_lazy('socio:home')

    def get(self, request, *args, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
            messages.error(request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        garantes = Socio.objects.filter(is_garante=False)
        context["clasecreditos"] = clasecreditos
        socio_usuario = Socio.objects.get(usuario_id=self.request.user.id)
        context["socio"] = socio_usuario
        context["garantes"] = garantes
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
            messages.error(self.request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
            return redirect('socio:solicitudcreditocreate')

        if socio.fecha_ingreso is None:
            messages.error(self.request,
                           'El socio no tiene informacion sobre su fecha de ingreso.El socio primero debe actualizar toda su informacion en Cuenta')
            return redirect('socio:solicitudcreditocreate')

        fecha_actual = date.today()
        num_anios = diasHastaFecha(socio.fecha_ingreso.day, socio.fecha_ingreso.month, socio.fecha_ingreso.year,
                                   fecha_actual.day,
                                   fecha_actual.month, fecha_actual.year) / 365
        if int(num_anios) < data['clasecredito'].tiempo_minimo_servicio:
            messages.error(self.request,
                           'El socio no cumple con el tiempo minimo de servicio para esta clase de prestamo')
            return redirect('socio:solicitudcreditocreate')

        form.instance.porcentaje_interes = data['clasecredito'].porcentaje_interes
        form.instance.socio = socio
        self.object = form.save()
        garante = data['garante']
        garante.is_garante = True
        garante.save()
        return super().form_valid(form)


def cuota_list(request):
    cuotas = []
    socio = Socio.objects.get(usuario_id=request.user.id)
    if Credito.objects.filter(socio_id=socio.id).exists():
        credito = Credito.objects.get(socio_id=socio.id)
        for cuota in credito.cuotas.all():
            cuotas.append(cuota)
    else:
        messages.error(request, 'El socio no mantiene ningún crédito', extra_tags='danger')
    return render(request, 'socio/cuotas_list.html', {'cuotas': cuotas, 'socio': socio})


def rubro_list(request):
    rubros = []
    socio = Socio.objects.get(usuario_id=request.user.id)
    for rubro in socio.rubros.all():
        rubros.append(rubro)
    return render(request, 'socio/consultar_rubros.html', {'rubros': rubros})


class UsuarioUpdate(SocioRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'socio/perfil.html'
    fields = ['nombres', 'apellidos', 'fecha_nacimiento']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = Socio.objects.get(usuario_id=self.request.user.id)
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        Socio.objects.update(
            direccion=self.request.POST.get('direccion', ''),
            telefono=self.request.POST.get('telefono', ''),
            celular=self.request.POST.get('celular', ''),
            cargo=self.request.POST.get('cargo', ''),
            area=self.request.POST.get('area', ''),
            fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Información actualizada correctamente")
        return reverse_lazy('socio:usuarioupdate', args=[self.object.id])


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
    return render(request, 'socio/cambiar_password.html')

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import render, redirect
from genericos.SolicitudCredito.SolicitudCreditoCreate import SolicitudCreditoCreate
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from sistema.models import SolicitudCredito, Socio, ClaseCredito, Credito, \
    Usuario, RestriccionClaseCredito


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


class SolicitudCreditoCreate(SocioRequiredMixin, SolicitudCreditoCreate, CreateView):
    template_name = 'socio/solicitudcredito_form.html'
    success_url = reverse_lazy('socio:home')


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


class SocioUpdate(SocioRequiredMixin, UpdateView):
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

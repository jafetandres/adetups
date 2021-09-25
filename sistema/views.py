import json
from django.contrib.auth import login
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import UsuarioForm
from .models import *


def cambiar_password(request):
    errores = []
    bandera = False
    if request.method == 'POST':
        if len(request.POST['new_password2']) < 8:
            errores.append("La nueva contraseña debe tener minimo 8 caracteres")
            bandera = False
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
            errores.append("La nueva contraseña debe tener minimo una letra en mayuscula")
            bandera = False
        else:
            bandera = True
        if minusculas < 1:
            errores.append("La nueva contraseña debe tener minimo una letra en minuscula")
            bandera = False
        else:
            bandera = True
        if request.POST['new_password1'] != request.POST['new_password2']:
            errores.append("La nueva contraseña no coicide con la confirmacion")
            bandera = False
        else:
            bandera = True
        if bandera is True:
            usuario = Usuario.objects.get(id=request.POST['usuario_id'])
            usuario.set_password(request.POST['new_password2'])
            usuario.save()
            login(request, usuario)

    json_dump = json.dumps(errores)
    return HttpResponse(json_dump, content_type='application/json')


class AdministradorRequiredMixin(AccessMixin):
    """
    Este mixin requerira que el usuario sea de tipo administrador
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.tipo != 'administrador':
            return redirect(reverse_lazy('registration:login'))
        if request.user.is_superuser is False:
            return redirect(reverse_lazy('registration:login'))
        return super(AdministradorRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomePageView(AdministradorRequiredMixin, TemplateView):
    template_name = "sistema/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios'] = Usuario.objects.all()
        return context


class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'sistema/usuario_detail.html'


class UsuarioListView(AdministradorRequiredMixin, ListView):
    model = Usuario


class UsuarioUpdate(AdministradorRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'sistema/perfil.html'
    fields = ['nombres', 'apellidos', 'fecha_nacimiento', 'email']

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado correctamente')
        return reverse_lazy('sistema:usuarioupdate', args=[self.object.id])


class AdministradorCreate(AdministradorRequiredMixin, CreateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'username', 'email', 'fecha_nacimiento', 'password']
    success_url = reverse_lazy('sistema:home')
    template_name = 'sistema/administrador_form.html'

    # def get(self, request, *args, **kwargs):
    #     if request.method == 'POST':
    #         if request.POST['tipo'] == 'socio':
    #             Socio.objects.create(usuario=self.object,
    #                                  direccion=request.POST['direccion'],  # ModelChoiceField in the form
    #                                  telefono=request.POST['telefono'],  # FloatField in the form, etc.
    #                                  celular=request.POST['celular'],
    #                                  cargo=request.POST['cargo'],
    #                                  area=request.POST['area'],
    #                                  fecha_ingreso=request.POST['fecha_ingreso']
    #                                  )
    #     return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        usuario = form.save(commit=False)
        usuario.set_password(data['password'])
        usuario.tipo = 'administrador'
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save()

        return super().form_valid(form)


class AdministradorUpdate(AdministradorRequiredMixin, UpdateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'email', 'fecha_nacimiento']
    template_name = 'sistema/administrador_form.html'

    def get_success_url(self):
        return reverse_lazy('sistema:administradorupdate', args=[self.object.id]) + '?ok'


class PresidenteCreate(AdministradorRequiredMixin, CreateView):
    model = Usuario
    success_url = reverse_lazy('sistema:home')
    template_name = 'sistema/presidente_form.html'
    form_class = UsuarioForm

    def form_valid(self, form):
        data = form.cleaned_data
        usuario = form.save(commit=False)
        usuario.set_password(data['password'])
        usuario.tipo = 'presidente'
        usuario.save()
        Socio.objects.create(usuario=usuario,
                             direccion=self.request.POST.get('direccion', ''),
                             telefono=self.request.POST.get('telefono', ''),
                             celular=self.request.POST.get('celular', ''),
                             cargo=self.request.POST.get('cargo', ''),
                             area=self.request.POST.get('area', ''),
                             fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
                             )

        return super().form_valid(form)


class PresidenteUpdate(AdministradorRequiredMixin, UpdateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'email', 'fecha_nacimiento']
    template_name = 'sistema/presidente_form.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = Socio.objects.get(usuario_id=self.object.id)
        return context

    def get_success_url(self):
        return reverse_lazy('sistema:presidenteupdate', args=[self.object.id]) + '?ok'


class AsistenteCreate(AdministradorRequiredMixin, CreateView):
    model = Usuario
    success_url = reverse_lazy('sistema:home')
    template_name = 'sistema/asistente_form.html'
    form_class = UsuarioForm

    def form_valid(self, form):
        data = form.cleaned_data
        usuario = form.save(commit=False)
        usuario.set_password(data['password'])
        usuario.tipo = 'asistente'
        usuario.save()
        Socio.objects.create(usuario=usuario,
                             direccion=self.request.POST.get('direccion', ''),
                             telefono=self.request.POST.get('telefono', ''),
                             celular=self.request.POST.get('celular', ''),
                             cargo=self.request.POST.get('cargo', ''),
                             area=self.request.POST.get('area', ''),
                             fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
                             )
        return super().form_valid(form)


class AsistenteUpdate(AdministradorRequiredMixin, UpdateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'email', 'fecha_nacimiento']
    template_name = 'sistema/asistente_form.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = Socio.objects.get(usuario_id=self.object.id)
        return context

    def get_success_url(self):
        return reverse_lazy('sistema:socioupdate', args=[self.object.id]) + '?ok'


class SocioCreate(AdministradorRequiredMixin, CreateView):
    model = Usuario
    template_name = 'sistema/socio_form.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('sistema:home')

    def form_valid(self, form):
        data = form.cleaned_data
        usuario = form.save(commit=False)
        usuario.set_password(data['password'])
        usuario.tipo = 'socio'
        usuario.save()
        Socio.objects.create(usuario=usuario,
                             direccion=self.request.POST.get('direccion', ''),
                             telefono=self.request.POST.get('telefono', ''),
                             celular=self.request.POST.get('celular', ''),
                             cargo=self.request.POST.get('cargo', ''),
                             area=self.request.POST.get('area', ''),
                             fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
                             )
        return super().form_valid(form)


class SocioUpdate(AdministradorRequiredMixin, UpdateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'email', 'fecha_nacimiento', 'tipo']
    template_name = 'sistema/socio_form.html'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = Socio.objects.get(usuario_id=self.object.id)
        return context

    def get_success_url(self):
        return reverse_lazy('sistema:socioupdate', args=[self.object.id]) + '?ok'


class UsuarioDelete(AdministradorRequiredMixin, DeleteView):
    model = Usuario

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(self.request, 'Registro eliminado correctamente')
        except IntegrityError:
            messages.error(request, 'No se puede borrar el registro ya que existen dependencias')
        return redirect('sistema:home')


class ClaseCreditoListView(AdministradorRequiredMixin, ListView):
    model = ClaseCredito


class ClaseCreditoDetailView(AdministradorRequiredMixin, DetailView):
    model = ClaseCredito


class ClaseCreditoCreate(AdministradorRequiredMixin, CreateView):
    model = ClaseCredito
    fields = ['descripcion', 'valdesde', 'valhasta', 'autorizacion', 'plazomax', 'garante', 'estado']
    success_url = reverse_lazy('sistema:clasecreditolist')

    def get_success_url(self):
        return reverse_lazy('sistema:clasecreditolist') + '?ok'


class ClaseCreditoUpdate(AdministradorRequiredMixin, UpdateView):
    model = ClaseCredito
    fields = ['descripcion', 'valdesde', 'valhasta', 'autorizacion', 'plazomax', 'garante', 'estado']

    def get_success_url(self):
        return reverse_lazy('sistema:clasecreditoupdate', args=[self.object.id]) + '?ok'


class ClaseCreditoDelete(AdministradorRequiredMixin, DeleteView):
    model = ClaseCredito

    # success_url = reverse_lazy('sistema:clascrelist')

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('sistema:clasecreditolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


#
# class ClaseSolicitudListView(AdministradorRequiredMixin, ListView):
#     model = ClaseSolicitud
#
#
# class ClaseSolicitudDetailView(LoginRequiredMixin, DetailView):
#     model = ClaseSolicitud
#

# class ClaseSolicitudCreate(LoginRequiredMixin, CreateView):
#     model = ClaseSolicitud
#     fields = ['descripcion', 'estado']
#     success_url = reverse_lazy('sistema:clasesolicitudlist')
#
#
# class ClaseSolicitudUpdate(UpdateView):
#     model = ClaseSolicitud
#     fields = ['descripcion', 'estado']
#
#     def get_success_url(self):
#         return reverse_lazy('sistema:clasesolicitudupdate', args=[self.object.id]) + '?ok'
#
#
# class ClaseSolicitudDelete(DeleteView):
#     model = ClaseSolicitud
#
#     # success_url = reverse_lazy('sistema:clascrelist')
#
#     def delete(self, request, *args, **kwargs):
#         """
#         Call the delete() method on the fetched object and then redirect to the
#         success URL. If the object is protected, send an error message.
#         """
#         self.object = self.get_object()
#         success_url = reverse_lazy('sistema:clasesolicitudlist')
#
#         try:
#             self.object.delete()
#         except IntegrityError:
#             messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
#         return HttpResponseRedirect(success_url)
#


# success_url = reverse_lazy('sistema:clascrelist')

class RestriccionClaseCreditoListView(ListView):
    model = ClaseCredito
    template_name = 'sistema/restriccionescredito_list.html'


class RestriccionClaseCreditoCreate(CreateView):
    model = RestriccionClaseCredito
    fields = ['clasecredito', 'tiempo_desde', 'tiempo_hasta', 'valhasta', 'estado']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        context["clasecreditos"] = clasecreditos
        return context

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse_lazy('sistema:restriccionclasecreditocreate')


def crear_restricciones_clase_credito(request):
    clasecreditos = []
    if ClaseCredito.objects.all():
        clasecreditos = ClaseCredito.objects.all()
    if request.method == 'POST':
        clasecredito = ClaseCredito.objects.get(id=request.POST['clasecredito'])
        restriccion = RestriccionClaseCredito()
        restriccion.plazo_max = request.POST['plazo_max']
        restriccion.val_max = request.POST['val_max']
        restriccion.tiempo_min = request.POST['tiempo_min']
        restriccion.save()
        clasecredito.restricciones.add(restriccion)
        clasecredito.save()
        return redirect('sistema:restriccionclasecreditolist')
    return render(request, 'sistema/restriccionescredito_form.html', {'clasecreditos': clasecreditos})


class RestriccionClaseCreditoUpdate(UpdateView):
    model = RestriccionClaseCredito
    fields = ['clasecredito', 'tiempo_desde', 'tiempo_hasta', 'valhasta', 'estado']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        context["clasecreditos"] = clasecreditos
        return context

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado correctamente')
        return reverse_lazy('sistema:restriccionclasecreditoupdate', args=[self.object.id])


class RestriccionClaseCreditoDelete(DeleteView):
    model = RestriccionClaseCredito

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('sistema:restriccionclasecreditolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class RubroListView(ListView):
    model = Rubro


class RubroDetailView(DetailView):
    model = Rubro


class RubroCreate(AdministradorRequiredMixin, CreateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse_lazy('sistema:rubrocreate')


class RubroUpdate(AdministradorRequiredMixin, UpdateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado correctamente')
        return reverse_lazy('sistema:rubroupdate', args=[self.object.id])


class RubroDelete(AdministradorRequiredMixin, DeleteView):
    model = Rubro

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('sistema:rubrolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


def cambiar_password(request):
    bandera = False
    if request.method == 'POST':
        if len(request.POST['new_password2']) < 8:
            bandera = False
            messages.warning(request, "La nueva contraseña debe tener minimo 8 caracteres")
            return redirect('sistema:cambiarpassword')
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
    return render(request, 'sistema/cambiar_password.html')

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, ListView
from sistema.forms import UsuarioForm
from sistema.models import SolicitudCredito, Usuario, Socio, ClaseCredito, RubroSocio
from django.shortcuts import redirect
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.utils.datastructures import MultiValueDictKeyError


class HomePageView(TemplateView):
    template_name = "asistente/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.all()
        return context


# class SolicitudCreditoDetailView(LoginRequiredMixin, DetailView):
#     model = SolicitudCredito
#     template_name = 'asistente/solicitudcredito_form.html'

# def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     context['socio'] = Socio.objects.filter(usuario_id=self.kwargs['pk'])
#     return context


class SolicitudCreditoUpdate(LoginRequiredMixin, UpdateView):
    model = SolicitudCredito
    fields = ['estado', 'observaciones']
    template_name = 'asistente/solicitudcredito_form.html'

    def get_success_url(self):
        return reverse_lazy('asistente:solicitudcreditoupdate', args=[self.object.id]) + '?ok'


class SolicitudCreditoCreate(LoginRequiredMixin, CreateView):
    model = SolicitudCredito
    fields = ['clasecredito', 'garante', 'monto', 'plazo']
    template_name = 'asistente/solicitudcredito_form.html'
    success_url = reverse_lazy('socio:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        socios = Socio.objects.filter(is_garante=False)
        context["clasecreditos"] = clasecreditos
        context["socios"] = socios
        return context

    def form_valid(self, form):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        data = form.cleaned_data
        # garante = Socio.objects.get(id=data['garante'])
        # solicitudcredito = form.save(commit=False)
        # solicitudcredito.garante = Socio.objects.get(id=data['garante'])
        form.instance.cuota = 10.00
        form.instance.interes = 10.00
        form.instance.porcinteres = 10.00
        form.instance.socio = socio
        # form.instance.garante = Socio.objects.get(id=data['garante'])
        # form.instance.clasecredito = ClaseCredito.objects.get(id=1)
        self.object = form.save()
        garante = data['garante']
        garante.is_garante = True
        garante.save()
        return super().form_valid(form)


class UsuarioDetailView(LoginRequiredMixin, DetailView):
    model = Usuario
    template_name = 'asistente/socio_detail.html'


class SocioCreate(LoginRequiredMixin, CreateView):
    model = Usuario
    template_name = 'asistente/socio_form.html'
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


# class RubroSocioPageView(TemplateView):
#     template_name = "asistente/rubrosocio.html"

rubros_generados = []


def cargar_rubros(request):
    if request.method == 'POST':
        if bool(request.FILES.get('archivo_rubros', False)):
            try:
                excel_file = request.FILES['archivo_rubros']
            except MultiValueDictKeyError:
                return redirect('asistente:home')
            if (str(excel_file).split('.')[-1] == "xls"):
                data = xls_get(excel_file, column_limit=13)
            elif (str(excel_file).split('.')[-1] == "xlsx"):
                data = xlsx_get(excel_file, column_limit=13)
                rubros = data["Hoja1"]
                size = len(rubros)
                index = 0
                for rubro in rubros:
                    index = index + 1
                    if index > 5 and index < size:
                        if len(rubro[2]) > 0 and rubro[12] > 0:
                            rubros_generados.append(rubro)
                        # rubro_socio=RubroSocio.objects.create(rubro=1,
                        #                                       descripcion='')
                # return render(request, 'asistente/rubrosocio_list.html', {'rubros_generados': rubros_generados})
                return redirect('asistente:guardarrubros')
            else:
                return redirect('asistente:home')
    return render(request, 'asistente/rubrosocio.html')


def guardar_rubros(request):
    if request.method == 'POST':
        print('entro guardar rubros')
        for rubro in rubros_generados:
            if Usuario.objects.filter(username=rubro[2]).exists():
                usuario = Usuario.objects.get(username=rubro[2])
                # if Socio.objects.filter(usuario_username=rubro[2]).exists():

                print("ceudla" + str(rubro[2]))
                rubro_generado = RubroSocio.objects.create(rubro_id=1,
                                                           descripcion='',
                                                           valor=rubro[12])

                socio = Socio.objects.get(usuario_id=usuario.id)
                socio.rubros.add(rubro_generado)
                socio.save()

    return render(request, 'asistente/rubrosocio_list.html', {'rubros_generados': rubros_generados})


# class RubroSocioCreate(LoginRequiredMixin, CreateView):
#     model = RubroSocio
#     template_name = 'asistente/rubrosocio.html'
#     success_url = reverse_lazy('sistema:home')
#
#     def form_valid(self, form):
#         data = form.cleaned_data
#         usuario = form.save(commit=False)
#         usuario.set_password(data['password'])
#         usuario.tipo = 'socio'
#         usuario.save()
#         Socio.objects.create(usuario=usuario,
#                              direccion=self.request.POST.get('direccion', ''),
#                              telefono=self.request.POST.get('telefono', ''),
#                              celular=self.request.POST.get('celular', ''),
#                              cargo=self.request.POST.get('cargo', ''),
#                              area=self.request.POST.get('area', ''),
#                              fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
#                              )
#         return super().form_valid(form)


class SocioUpdate(LoginRequiredMixin, UpdateView):
    model = Usuario
    fields = ['nombres', 'apellidos', 'email', 'fecha_nacimiento', 'tipo']
    template_name = 'asistente/socio_form.html'

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


class SocioListView(LoginRequiredMixin, ListView):
    model = Socio
    template_name = 'asistente/socio_list.html'


class SocioDetailView(LoginRequiredMixin, DetailView):
    model = Socio
    template_name = 'asistente/socio_detail.html'

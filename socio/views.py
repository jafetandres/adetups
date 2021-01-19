from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from sistema.models import Adtsolcre, Adtclascre, Adtsocios, Adtclasol, SolicitudCredito, Socio, ClaseCredito


#
# @login_required
# def index(request):
#     return render(request, "socio/index.html")
#


class HomePageView(LoginRequiredMixin,TemplateView):
    template_name = "socio/index.html"

    def get_context_data(self, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.filter(socio_id=socio.id)
        return context


class SolicitudCreditoListView(LoginRequiredMixin, ListView):
    model = SolicitudCredito


class SolicitudCreditoDetailView(LoginRequiredMixin, DetailView):
    model = SolicitudCredito


class SolicitudCreditoCreate(LoginRequiredMixin, CreateView):
    model = SolicitudCredito
    fields = ['clasecredito', 'garante', 'monto', 'plazo']
    template_name = 'socio/solicitudcredito_form.html'
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
#
# class AdtsolcreListView(ListView):
#     model = Adtsolcre
#     template_name = 'socio/index.html'
#
#
# class AdtsolcreCreateView(CreateView):
#     model = Adtsolcre
#     fields = ['clccodigo', 'solmonto', 'solplazo',
#                ]
#     template_name = 'socio/solicitudcredito_form.html'
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         clascres = Adtclascre.objects.all()
#         socios = Adtsocios.objects.all()
#         context["clascres"] = clascres
#         context["socios"] = socios
#         return context
#
#     def form_valid(self, form):
#         form.instance.solcuota = 10.00
#         form.instance.solintere = 10.00
#         form.instance.solporint = 10.00
#         form.instance.soccodigo=Adtsocios.objects.get(soccodigo=1)
#         form.instance.csocodigo = Adtclasol.objects.get(csocodigo=1)
#         self.object = form.save()
#         return super().form_valid(form)

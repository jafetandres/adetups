from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, UpdateView

from sistema.models import SolicitudCredito


class HomePageView(TemplateView):
    template_name = "presidente/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.all()
        return context


class SolicitudCreditoUpdate(LoginRequiredMixin, UpdateView):
    model = SolicitudCredito
    fields = ['estado', 'observaciones']
    template_name = 'presidente/solicitudcredito_update.html'

    def get_success_url(self):
        return reverse_lazy('presidente:solicitudcreditoupdate', args=[self.object.id]) + '?ok'

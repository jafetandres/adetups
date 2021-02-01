import decimal

import numpy as np
import numpy_financial as npf
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from sistema.models import SolicitudCredito, Credito, Cuota


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

    def form_valid(self, form):
        data = form.cleaned_data
        # usuario = form.save(commit=False)
        if data["estado"] == 'aprobada':
            print("monto1", self.object.monto)
            monto = float(self.object.monto)
            print("monto2", monto)
            per = np.arange(1 * self.object.plazo) + 1
            ipmt = npf.ipmt(0.09 / 12, per, 1 * self.object.plazo, monto)
            ppmt = npf.ppmt(0.09 / 12, per, 1 * self.object.plazo, monto)
            pmt = npf.pmt(0.09 / 12, 1 * self.object.plazo, monto)
            np.allclose(ipmt + ppmt, pmt)
            fmt = '{0:2d} {1:8.2f} {2:8.2f} {3:8.2f}'
            cuotas = []
            for payment in per:
                index = payment - 1
                monto = monto + ppmt[index]
                cuotas.append(Cuota.objects.create(capital=abs(round(ppmt[index], 2)),
                                                   interes=abs(round(ipmt[index], 2)),
                                                   saldo_capital=abs(round(monto, 2)),
                                                   orden=payment,
                                                   valor_cuota=abs(round(ppmt[index], 2)) + abs(round(ipmt[index], 2))))
            # print(abs(round(payment, 2)), abs(round(ppmt[index], 2)), abs(round(ipmt[index], 2)),
            #       abs(round(principal, 2)))
            credito = Credito()
            credito.solicitud = self.object
            credito.socio = self.object.socio
            credito.monto = self.object.monto
            credito.porcentaje_interes = self.object.porcentaje_interes
            credito.plazo = self.object.plazo
            credito.estado = 'aprobado'
            credito.save()
            for cuota in cuotas:
                credito.cuotas.add(cuota.id)
            # credito.cuotas.set(cuotas)

            # Credito.objects.create(solicitud_id=self.object.id,
            #                        socio=self.object.socio,
            #                        monto=self.object.monto,
            #                        porcentaje_interes=self.object.porcentaje_interes,
            #                        plazo=self.object.plazo,
            #                        estado='aprobado',
            #
            #                        )
        else:
            return redirect('presidente:home')
        return super().form_valid(form)

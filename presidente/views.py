import numpy as np
import numpy_financial as npf
import datetime
from django.contrib import messages
from dateutil import relativedelta
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, ListView, DetailView, CreateView, DeleteView
from sistema.models import SolicitudCredito, Credito, Cuota, Socio, Usuario, RubroSocio, ClaseCredito, \
    RestriccionClaseCredito, Rubro, LiquidacionCredito


class PresidenteRequiredMixin(AccessMixin):
    """
    Este mixin requerira que el usuario sea de tipo presidente
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.tipo != 'presidente':
            return redirect(reverse_lazy('registration:login'))
        return super(PresidenteRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomePageView(PresidenteRequiredMixin, TemplateView):
    template_name = "presidente/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.all()
        return context


class SolicitudCreditoList(PresidenteRequiredMixin, ListView):
    model = SolicitudCredito
    template_name = 'presidente/solicitudcredito_list.html'


class SolicitudCreditoUpdate(PresidenteRequiredMixin, UpdateView):
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
                                                   fecha_pago=datetime.date.today() + relativedelta.relativedelta(
                                                       months=payment),
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


class SocioListView(PresidenteRequiredMixin, ListView):
    model = Socio
    template_name = 'presidente/socio_list.html'


class SocioDetailView(PresidenteRequiredMixin, DetailView):
    model = Socio
    template_name = 'presidente/socio_detail.html'


class SocioDelete(PresidenteRequiredMixin, DeleteView):
    model = Socio

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('presidente:sociolist')

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
    return render(request, 'presidente/cambiar_password.html')


class UsuarioUpdate(PresidenteRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'presidente/perfil.html'
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
        return reverse_lazy('presidente:usuarioupdate', args=[self.object.id])


def consultar_rubros(request):
    rubros = []
    socio = None
    max_year = RubroSocio.objects.latest('fecha_ingreso').fecha_ingreso.year
    min_year = RubroSocio.objects.latest('-fecha_ingreso').fecha_ingreso.year
    anios = []
    i = min_year
    while i <= max_year:
        anios.append(i)
        i += 1
    mesActual = None
    anioActual = None
    if request.method == 'POST':
        # mesActual = request.POST['mes']
        # anioActual = request.POST['anio']

        try:
            anioActual = int(request.POST['anio'])
            print(anioActual)
        except ValueError:
            anioActual = request.POST['anio']
            print(anioActual)

        try:
            mesActual = int(request.POST['mes'])
            print(mesActual)
        except ValueError:
            mesActual = request.POST['mes']
            print(mesActual)
        username = request.POST['username']
        if Usuario.objects.filter(username=username).exists():
            usuario = Usuario.objects.get(username=username)
            if Socio.objects.filter(usuario_id=usuario.id).exists():
                socio = Socio.objects.get(usuario_id=usuario.id)
                if request.POST['anio'] == 'todos' and request.POST['mes'] == 'todos':
                    for rubro in socio.rubros.all():
                        rubros.append(rubro)
                elif request.POST['anio'] != 'todos' and request.POST['mes'] == 'todos':
                    for rubro in socio.rubros.filter(fecha_ingreso__year=request.POST['anio']):
                        rubros.append(rubro)

                elif request.POST['anio'] == 'todos' and request.POST['mes'] != 'todos':
                    for rubro in socio.rubros.filter(fecha_ingreso__month=request.POST['mes']):
                        rubros.append(rubro)
                elif request.POST['anio'] != 'todos' and request.POST['mes'] != 'todos':
                    for rubro in socio.rubros.filter(fecha_ingreso__month=request.POST['mes'],
                                                     fecha_ingreso__year=request.POST['anio']):
                        rubros.append(rubro)

                # if Credito.objects.filter(socio_id=socio.id).exists():
                #     credito = Credito.objects.get(socio_id=socio.id)
                #     for cuota in credito.cuotas.all():
                #         cuotas.append(cuota)
                # else:
                #     messages.error(request, 'El socio no mantiene ningun credito')
        else:
            messages.error(request, 'El socio no existe', extra_tags='danger')
        # return redirect('asistente:consultarcuotas')
    return render(request, 'presidente/consultar_rubros.html',
                  {'rubros': rubros, 'socio': socio, 'anios': anios, 'mesActual': mesActual, 'anioActual': anioActual})


class ClaseCreditoListView(PresidenteRequiredMixin, ListView):
    model = ClaseCredito
    template_name = 'presidente/clasecredito_list.html'


class ClaseCreditoDetailView(PresidenteRequiredMixin, DetailView):
    model = ClaseCredito
    template_name = 'presidente/clasesolicitud_detail.html'


class ClaseCreditoCreate(PresidenteRequiredMixin, CreateView):
    model = ClaseCredito
    fields = ['descripcion', 'valdesde', 'valhasta', 'autorizacion', 'plazomax', 'garante', 'estado']
    template_name = 'presidente/clasecredito_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Registro creado exitosamente')
        return reverse_lazy('presidente:clasecreditolist')


class ClaseCreditoUpdate(PresidenteRequiredMixin, UpdateView):
    model = ClaseCredito
    fields = ['descripcion', 'valdesde', 'valhasta', 'autorizacion', 'plazomax', 'garante', 'estado']
    template_name = 'presidente/clasecredito_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado exitosamente')
        return reverse_lazy('presidente:clasecreditoupdate', args=[self.object.id])


class ClaseCreditoDelete(PresidenteRequiredMixin, DeleteView):
    model = ClaseCredito

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('presidente:clasecreditolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class RestriccionClaseCreditoListView(ListView):
    model = RestriccionClaseCredito
    template_name = 'presidente/restriccionclasecredito_list.html'


class RestriccionClaseCreditoCreate(CreateView):
    model = RestriccionClaseCredito
    fields = ['clasecredito', 'tiempo_desde', 'tiempo_hasta', 'valhasta', 'estado']
    template_name = 'presidente/restriccionclasecredito_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        context["clasecreditos"] = clasecreditos
        return context

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse_lazy('presidente:restriccionclasecreditocreate')


class RestriccionClaseCreditoUpdate(UpdateView):
    model = RestriccionClaseCredito
    fields = ['clasecredito', 'tiempo_desde', 'tiempo_hasta', 'valhasta', 'estado']
    template_name = 'presidente/restriccionclasecredito_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        context["clasecreditos"] = clasecreditos
        return context

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado correctamente')
        return reverse_lazy('presidente:restriccionclasecreditoupdate', args=[self.object.id])


class RestriccionClaseCreditoDelete(DeleteView):
    model = RestriccionClaseCredito

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('presidente:restriccionclasecreditolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class RubroListView(ListView):
    model = Rubro
    template_name = 'presidente/rubro_list.html'


class RubroDetailView(DetailView):
    model = Rubro
    template_name = 'presidente/rubro_detail.html'


class RubroCreate(PresidenteRequiredMixin, CreateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']
    template_name = 'presidente/rubro_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Registro creado correctamente')
        return reverse_lazy('presidente:rubrocreate')


class RubroUpdate(PresidenteRequiredMixin, UpdateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']
    template_name = 'presidente/rubro_form.html'

    def get_success_url(self):
        messages.success(self.request, 'Registro actualizado correctamente')
        return reverse_lazy('presidente:rubroupdate', args=[self.object.id])


class RubroDelete(PresidenteRequiredMixin, DeleteView):
    model = Rubro

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('presidente:rubrolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class CreditoListView(PresidenteRequiredMixin, ListView):
    model = Credito
    template_name = 'presidente/credito_list.html'


class CreditoDetail(PresidenteRequiredMixin, DetailView):
    model = Credito
    template_name = 'presidente/credito_detail.html'


class LicquidacionCreditoCreate(PresidenteRequiredMixin, CreateView):
    model = LiquidacionCredito
    template_name = 'presidente/credito_liquidar.html'
    fields = ['valor', 'observacion']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credito = Credito.objects.get(id=self.kwargs['credito_id'])
        valor_pendiente = 0
        for cuota in credito.cuotas.all():
            if cuota.estado == False:
                valor_pendiente = cuota.valor_cuota + valor_pendiente

        context['valor_pendiente'] = valor_pendiente
        context['credito'] = credito
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        credito = Credito.objects.get(id=self.kwargs['credito_id'])
        valor = data["valor"]
        liquidacioncredito = form.save(commit=False)
        liquidacioncredito.credito = credito
        liquidacioncredito.save()
        # liquidacioncredito=LiquidacionCredito()
        # liquidacioncredito.credito=credito
        # liquidacioncredito.valor=valor
        # liquidacioncredito.observacion=data["observacion"]
        # liquidacioncredito.save()
        # LiquidacionCredito.objects.create(
        #     credito_id=credito.id,
        #     valor=valor,
        #     observacion=data["observacion"]
        # )

        for cuota in credito.cuotas.all().order_by('orden'):
            if cuota.estado == False:
                print("valor1 ", valor)
                valor_anterior = cuota.valor_cuota
                print("valor anterior", valor_anterior)
                valor_actual = valor_anterior - valor
                print("valor actual1", valor_actual)
                valor = abs(valor_actual)
                if valor_actual <= 0:
                    print("valor actual2", valor_actual)
                    cuota.estado = True
                    cuota.save()
                    print(cuota.estado)

                if valor > 0 and cuota.estado == False:
                    print("valor 2", valor)
                    cuota.valor_cuota = valor_actual
                    cuota.save()
                    if valor > 0:
                        valor = 0
        return super().form_valid(form)

    def get_success_url(self):
        credito = Credito.objects.get(id=self.kwargs['credito_id'])
        return reverse_lazy('asistente:creditodetail', args=[credito.id]) + '?ok'

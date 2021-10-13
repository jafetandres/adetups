from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import CreateView
from adetups.utils import calcular_tiempo_servicio
from sistema.models import SolicitudCredito, Socio, ClaseCredito, Credito, RestriccionClaseCredito


class SolicitudCreditoCreate(CreateView):
    model = SolicitudCredito
    fields = '__all__'

    def get_socio(self):
        try:
            usuario_id = self.kwargs['usuario_id']
        except:
            usuario_id = False
        if usuario_id:
            return Socio.objects.get(usuario_id=usuario_id)
        else:
            return Socio.objects.get(usuario_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        if Credito.objects.filter(socio=self.get_socio(), estado='aprobado').exists():
            messages.error(request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = []
        for clasecredito in ClaseCredito.objects.all():
            if clasecredito.estado == 'ACT':
                if RestriccionClaseCredito.objects.filter(clasecredito=clasecredito.id):
                    clasecreditos.append(clasecredito)

        context["clasecreditos"] = clasecreditos
        garantes = Socio.objects.filter(is_garante=False).filter(~Q(id=self.get_socio().id))
        context["clasecreditos"] = clasecreditos
        socio_usuario = self.get_socio()
        context["socio"] = socio_usuario
        context["garantes"] = garantes
        if self.get_socio().fecha_ingreso is not None:
            num_anios = calcular_tiempo_servicio(self.get_socio().fecha_ingreso)
        else:
            num_anios = 0
            messages.error(self.request, 'El socio no tiene fecha de ingreso actualize sus datos')
        context["anios_servicio"] = int(num_anios)
        return context

    def form_valid(self, form):
        socio = self.get_socio()
        if socio.fecha_ingreso is None:
            messages.error(self.request,
                           'El socio no tiene informacion sobre su fecha de ingreso.El socio primero debe actualizar toda su informacion en Cuenta')
            return redirect('socio:solicitudcreditocreate')
        from operator import attrgetter
        data = form.cleaned_data
        monto = data["monto"]
        plazo_max = data["plazo"]
        num_anios = calcular_tiempo_servicio(socio.fecha_ingreso)
        clasecredito = data['clasecredito']
        restricciones = clasecredito.restricciones.all().order_by('-tiempo_min')
        m = min(restricciones, key=attrgetter("tiempo_min"))
        if num_anios < m.tiempo_min:
            messages.error(self.request, 'Verifique su tiempo de servicio')
            return redirect('socio:solicitudcreditocreate')

        restriccion = min(restricciones, key=lambda x: int(attrgetter("tiempo_min")(x)) - num_anios > 0)

        if monto > restriccion.val_max:
            messages.error(self.request, 'Error el monto solicitado excede el limite de la restriccion del prestamo.')
            return redirect('socio:solicitudcreditocreate')
        if plazo_max > restriccion.plazo_max:
            messages.error(self.request, 'Error el plazo  excede el limite de la restriccion del prestamo')
            return redirect('socio:solicitudcreditocreate')
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
            messages.error(self.request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
            return redirect('socio:solicitudcreditocreate')

        form.instance.porcentaje_interes = data['clasecredito'].porcentaje_interes
        form.instance.socio = socio
        self.object = form.save()
        garante = data['garante']
        garante.is_garante = True
        garante.save()
        return super().form_valid(form)

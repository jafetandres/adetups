import json
from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, ListView, DeleteView
from asistente.forms import SolicitudCreditoForm
from sistema.forms import UsuarioForm
from sistema.models import SolicitudCredito, Usuario, Socio, ClaseCredito, RubroSocio, Credito, Parametro, Rubro, Cuota, \
    LiquidacionCredito
from django.shortcuts import redirect
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.utils.datastructures import MultiValueDictKeyError


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


class HomePageView(TemplateView, LoginRequiredMixin):
    template_name = "asistente/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.all()
        return context


class EscogerArchivoPageView(TemplateView, LoginRequiredMixin):
    template_name = "asistente/escoger_archivo.html"


class SolicitudCreditoUpdate(LoginRequiredMixin, UpdateView):
    model = SolicitudCredito
    fields = ['estado', 'observaciones']
    template_name = 'asistente/solicitudcredito_update.html'

    def get_success_url(self):
        return reverse_lazy('asistente:solicitudcreditoupdate', args=[self.object.id]) + '?ok'


class SolicitudCreditoCreate(LoginRequiredMixin, CreateView):
    model = SolicitudCredito
    form_class = SolicitudCreditoForm
    template_name = 'asistente/solicitudcredito_form.html'
    success_url = reverse_lazy('asistente:home')

    def get(self, request, *args, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if self.kwargs['usuario_id']:
            socio = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        if Credito.objects.filter(socio=socio).exists():
            messages.error(request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clasecreditos = ClaseCredito.objects.all()
        garantes = Socio.objects.filter(is_garante=False)
        context["clasecreditos"] = clasecreditos
        socio_usuario = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        context["socio"] = socio_usuario
        context["garantes"] = garantes
        return context

    def form_valid(self, form):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if self.kwargs['usuario_id']:
            socio = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        data = form.cleaned_data
        if Credito.objects.filter(socio=socio).exists():
            messages.error(self.request, 'El socio ya tiene un prestamo activo y no puede solicitar otro')
            return redirect('asistente:solicitudcreditocreate', socio.usuario.id)

        if socio.fecha_ingreso is None:
            messages.error(self.request,
                           'El socio no tiene informacion sobre su fecha de ingreso.El socio primero debe actualizar toda su informacion en Cuenta')
            return redirect('asistente:solicitudcreditocreate', socio.usuario.id)

        fecha_actual = date.today()
        num_anios = diasHastaFecha(socio.fecha_ingreso.day, socio.fecha_ingreso.month, socio.fecha_ingreso.year,
                                   fecha_actual.day,
                                   fecha_actual.month, fecha_actual.year) / 365
        if int(num_anios) < data['clasecredito'].tiempo_minimo_servicio:
            messages.error(self.request,
                           'El socio no cumple con el tiempo minimo de servicio para esta clase de prestamo')
            return redirect('asistente:solicitudcreditocreate', socio.usuario.id)

        # garante = Socio.objects.get(id=data['garante'])
        # solicitudcredito = form.save(commit=False)
        # solicitudcredito.garante = Socio.objects.get(id=data['garante'])
        # print(data['clasecredito'].)
        # form.instance.cuota = 10.00
        # form.instance.interes = 10.00
        # para
        form.instance.porcentaje_interes = data['clasecredito'].porcentaje_interes
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


rubros_generados_moviestar = []


def cargar_rubros_moviestar(request):
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
                            if Usuario.objects.filter(username=rubro[2]).exists():
                                usuario = Usuario.objects.get(username=rubro[2])
                                if Socio.objects.filter(usuario_id=usuario.id).exists():
                                    rubros_generados_moviestar.append(rubro)
                return redirect('asistente:guardarrubrosmoviestar')
            else:
                return redirect('asistente:home')
    return render(request, 'asistente/rubro_subirarchivo.html')


clases_rubros = []
rubros_generados_general = []


def cargar_rubros_general(request):
    if request.method == 'POST':
        if bool(request.FILES.get('archivo_rubros', False)):
            try:
                excel_file = request.FILES['archivo_rubros']
            except MultiValueDictKeyError:
                return redirect('asistente:home')
            if (str(excel_file).split('.')[-1] == "xls"):
                data = xls_get(excel_file, column_limit=26)
            elif (str(excel_file).split('.')[-1] == "xlsx"):
                data = xlsx_get(excel_file, column_limit=26)
                rubros = data["Hoja1"]
                size = len(rubros)
                for i in range(len(rubros)):
                    if i == 4:

                        for j in range(len(rubros[i])):
                            abreviatura = rubros[i][j]
                            if Rubro.objects.filter(abreviatura=abreviatura.strip(' ')).exists():
                                aux = Rubro.objects.get(abreviatura=abreviatura.strip(' ')), j
                                clases_rubros.append(aux)

                    if i > 4:
                        #     if rubros[i][pos_movi] != '':
                        #         rubros[i].append('MOVI')
                        #     if rubros[i][pos_claro] != '':
                        #         rubros[i].append('CLARO')
                        rubros_generados_general.append(rubros[i])

                # return render(request, 'asistente/rubrosocioexcelmoviestar_list.html', {'rubros_generados': rubros_generados})
                return redirect('asistente:guardarrubrosgeneral')
            else:
                return redirect('asistente:home')
    return render(request, 'asistente/rubro_subirarchivo.html')


def guardar_rubros_moviestar(request):
    global rubros_generados_moviestar
    if request.method == 'POST':
        for rubro in rubros_generados_moviestar:
            if Usuario.objects.filter(username=rubro[2]).exists():
                usuario = Usuario.objects.get(username=rubro[2])
                rubro_generado = RubroSocio.objects.create(rubro_id=1,
                                                           descripcion=rubro[10],
                                                           valor=rubro[12])

                socio = Socio.objects.get(usuario_id=usuario.id)
                socio.rubros.add(rubro_generado)
                socio.save()
        rubros_generados_moviestar = []
    return render(request, 'asistente/rubrosocioexcelmoviestar_list.html',
                  {'rubros_generados': rubros_generados_moviestar})


def guardar_rubros_general(request):
    global rubros_generados_general
    global clases_rubros
    if request.method == 'POST':
        for rubro in rubros_generados_general:
            print(rubro)
            if Usuario.objects.filter(username=rubro[2]).exists():
                usuario = Usuario.objects.get(username=rubro[2])
                if Socio.objects.filter(usuario_id=usuario.id).exists():
                    socio = Socio.objects.get(usuario_id=usuario.id)
                    for num, rubro_aux in enumerate(rubro, start=0):
                        if num > 3:
                            if isinstance(rubro_aux, float) or isinstance(rubro_aux, int):
                                if rubro_aux > 0:
                                    for clase in clases_rubros:
                                        if num == clase[1]:
                                            rubro_generado = RubroSocio.objects.create(rubro_id=clase[0].id,
                                                                                       descripcion=clase[0].descripcion,
                                                                                       valor=rubro_aux)

                                            socio.rubros.add(rubro_generado)
                                            socio.save()

        messages.success(request, 'Rubros generados correctamente')
        rubros_generados_general = []
        clases_rubros = []
        return redirect('asistente:cargarrubrosgeneral')
    return render(request, 'asistente/rubrosocioexcelgeneral_list.html',
                  {'rubros_generados_general': rubros_generados_general})


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


def escoger_socio(request):
    if request.method == 'POST':
        cedula = request.POST['cedula']
        if Usuario.objects.filter(username=cedula).exists():
            usuario = Usuario.objects.get(username=cedula)
            if Socio.objects.filter(usuario=usuario).exists():
                socio = Socio.objects.get(usuario=usuario)
                if Credito.objects.filter(socio=socio).exists():
                    messages.error(request, 'El socio ya tiene un crédito aprobado')
                else:
                    return redirect('asistente:solicitudcreditocreate', usuario_id=socio.usuario.id)
            else:
                messages.error(request, 'El socio no exsiste')
        else:
            messages.error(request, 'El socio no exsiste')
    return render(request, 'asistente/escoger_socio.html')


class ClaseCreditoListView(LoginRequiredMixin, ListView):
    model = ClaseCredito
    template_name = 'asistente/clasecredito_list.html'


class ClaseCreditoDetailView(LoginRequiredMixin, DetailView):
    model = ClaseCredito
    template_name = 'asistente/clasecredito_detail.html'


class ParametroListView(ListView):
    model = Parametro
    template_name = 'asistente/parametro_list.html'


class ParametroDetailView(DetailView):
    model = Parametro
    template_name = 'asistente/parametro_detail.html'


class RubroListView(ListView):
    model = Rubro
    template_name = 'asistente/rubro_list.html'


class RubroDetailView(DetailView):
    model = Rubro
    template_name = 'asistente/rubro_detail.html'


class RubroCreate(LoginRequiredMixin, CreateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']
    success_url = reverse_lazy('asistente:rubrolist')
    template_name = 'asistente/rubro_form.html'


class RubroUpdate(LoginRequiredMixin, UpdateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']
    template_name = 'asistente/rubro_form.html'

    def get_success_url(self):
        return reverse_lazy('asistente:rubroupdate', args=[self.object.id]) + '?ok'


class RubroDelete(LoginRequiredMixin, DeleteView):
    model = Rubro

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('asistente:rubrolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class RubroSocioListView(TemplateView):
    template_name = 'asistente/rubrosocio_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['socios'] = Socio.objects.all()

        return context


class RubroSocioCreate(LoginRequiredMixin, CreateView):
    model = RubroSocio
    fields = ['rubro', 'descripcion', 'servicio', 'valor']
    success_url = reverse_lazy('asistente:rubrosociolist')
    template_name = 'asistente/rubrosocio_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['rubros'] = Rubro.objects.all()
        context['socios'] = Socio.objects.all()

        return context

    def form_valid(self, form):
        data = form.cleaned_data
        # rubrosocio = form.save(commit=False)
        id = 0
        if self.request.POST.get('socio') == '':
            print('esta vacio')
            id = 0
        else:
            id = self.request.POST.get('socio')
        if Socio.objects.filter(id=id).exists():
            socio = Socio.objects.get(id=self.request.POST.get('socio', ''))
            form.save()
            socio.rubros.add(form.instance)
        else:
            messages.error(self.request, 'El socio no existe')
            return redirect('asistente:rubrosociocreate')

        return super().form_valid(form)


class RubroSocioDelete(LoginRequiredMixin, DeleteView):
    model = RubroSocio

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL. If the object is protected, send an error message.
        """
        self.object = self.get_object()
        success_url = reverse_lazy('asistente:rubrosociolist')

        try:
            self.object.delete()
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'No se puede borrar el registro ya que existen dependencias')
        return HttpResponseRedirect(success_url)


class UsuarioUpdate(LoginRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'asistente/perfil.html'
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
        return reverse_lazy('asistente:usuarioupdate', args=[self.object.id]) + '?ok'


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
    return render(request, 'asistente/cambiar_password.html')


class CreditoListView(LoginRequiredMixin, ListView):
    model = Credito
    template_name = 'asistente/credito_list.html'


class CreditoDetail(LoginRequiredMixin, DetailView):
    model = Credito
    template_name = 'asistente/credito_detail.html'


class LicquidacionCreditoCreate(LoginRequiredMixin, CreateView):
    model = LiquidacionCredito
    template_name = 'asistente/credito_liquidar.html'
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
        liquidacioncredito.credito=credito
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


# class CreditoUpdate(LoginRequiredMixin, UpdateView):
#     model = Credito
#     template_name = 'asistente/credito_liquidar.html'
#     fields = ['estado']
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         credito = self.object
#         valor_pendiente = 0
#         for cuota in credito.cuotas.all():
#             if cuota.estado == False:
#                 valor_pendiente = cuota.valor_cuota + valor_pendiente
#
#         context['valor_pendiente'] = valor_pendiente
#
#         return context
#
#     def form_valid(self, form):
#         data = form.cleaned_data
#         if data["estado"] == 'liquidado':
#             LiquidacionCredito.objects.create(
#                 credito=self.object,
#                 direccion=self.request.POST.get('valor', ''),
#                 observacion=self.request.POST.get('observacion', '')
#             )
#
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('asistente:creditoupdate', args=[self.object.id]) + '?ok'


def consultar_cuotas(request):
    cuotas = []
    socio = None
    if request.method == 'POST':
        username = request.POST['username']
        if Usuario.objects.filter(username=username).exists():
            usuario = Usuario.objects.get(username=username)
            if Socio.objects.filter(usuario_id=usuario.id).exists():
                socio = Socio.objects.get(usuario_id=usuario.id)
                if Credito.objects.filter(socio_id=socio.id).exists():
                    credito = Credito.objects.get(socio_id=socio.id)
                    for cuota in credito.cuotas.all():
                        cuotas.append(cuota)
                else:
                    messages.error(request, 'El socio no mantiene ningun credito')
        else:
            messages.error(request, 'El socio no existe')
        # return redirect('asistente:consultarcuotas')
    return render(request, 'asistente/consultar_cuotas.html', {'cuotas': cuotas, 'socio': socio})
    # data = []
    # print(request.GET['username'])
    # print(request.is_ajax)
    # if request.method == 'GET':
    #     username = request.GET['username']
    #     if Usuario.objects.filter(username=username).exists():
    #         usuario = Usuario.objects.get(username=username)
    #         if Socio.objects.filter(usuario_id=usuario.id).exists():
    #             socio = Socio.objects.get(usuario_id=usuario.id)
    #             if Credito.objects.filter(socio_id=socio.id).exists():
    #                 credito = Credito.objects.get(socio_id=socio.id)
    #                 for cuota in credito.cuotas:
    #                     data.append(cuota)
    #
    #     json_dump = json.dumps(data)
    #     return HttpResponse(json_dump, content_type='application/json')

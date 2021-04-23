import io
import datetime
import numpy as np
import numpy_financial as npf
from dateutil import relativedelta
from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, ListView, DeleteView
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from asistente.forms import SolicitudCreditoForm
from sistema.forms import UsuarioForm
from sistema.models import SolicitudCredito, Usuario, Socio, ClaseCredito, RubroSocio, Credito, Parametro, Rubro, Cuota, \
    LiquidacionCredito, RestriccionClaseCredito
from django.shortcuts import redirect
from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from braces.views import JSONResponseMixin


class TableAsJSON(JSONResponseMixin, generic.View):
    model = SolicitudCredito

    def get(self, request, *args, **kwargs):
        col_name_map = {
            '0': 'socio',
            '1': 'fecha_ingreso',
            '2': 'garante',
            '3': 'monto',
            '4': 'clasecredito',
            '5': 'estado',
            '6': 'acciones',
        }
        object_list = self.model.objects.all()
        search_text = request.GET.get('sSearch', '').lower()
        start = int(request.GET.get('iDisplayStart', 0))
        delta = int(request.GET.get('iDisplayLength', 50))
        sort_dir = request.GET.get('sSortDir_0', 'asc')
        sort_col = int(request.GET.get('iSortCol_0', 0))
        sort_col_name = request.GET.get('mDataProp_%s' % sort_col, '1')
        sort_dir_prefix = (sort_dir == 'desc' and '-' or '')

        if sort_col_name in col_name_map:
            sort_col = col_name_map[sort_col_name]
            object_list = object_list.order_by('%s%s' % (sort_dir_prefix, sort_col))

        filtered_object_list = object_list
        if len(search_text) > 0:
            filtered_object_list = object_list.filter_on_search(search_text)

        json = {
            "iTotalRecords": object_list.count(),
            "iTotalDisplayRecords": filtered_object_list.count(),
            "sEcho": request.GET.get('sEcho', 1),
            "aaData": [obj.as_list() for obj in filtered_object_list[start:(start + delta)]]
        }
        return self.render_json_response(json)


class AsistenteRequiredMixin(AccessMixin):
    """
    Este mixin de seguridad requiere que el usuario sea de tipo asistente
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            print('entro')
            return self.handle_no_permission()
        if request.user.tipo != 'asistente':
            return redirect(reverse_lazy('registration:login'))
        return super(AsistenteRequiredMixin, self).dispatch(request, *args, **kwargs)


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


class HomePageView(AsistenteRequiredMixin, TemplateView):
    """
    Home o index del portal del asistente
    """
    template_name = "asistente/index.html"  # archivo html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudescredito'] = SolicitudCredito.objects.all()
        return context


class EscogerArchivoPageView(AsistenteRequiredMixin, TemplateView):
    template_name = "asistente/escoger_archivo.html"


class SolicitudCreditoUpdate(AsistenteRequiredMixin, UpdateView):
    model = SolicitudCredito
    fields = ['estado', 'observaciones']
    template_name = 'asistente/solicitudcredito_update.html'

    def form_valid(self, form):
        data = form.cleaned_data
        if data["estado"] == 'revisada':
            form.instance.revisada_por = Usuario.objects.get(id=self.request.user.id)
        if data["estado"] == 'aprobada':
            form.instance.aprobada_por = Usuario.objects.get(id=self.request.user.id)
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

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Estado de solicitud actualizado correctamente")
        return reverse_lazy('asistente:solicitudcreditoupdate', args=[self.object.id])


class SolicitudCreditoCreate(AsistenteRequiredMixin, CreateView):
    model = SolicitudCredito
    form_class = SolicitudCreditoForm
    template_name = 'asistente/solicitudcredito_form.html'
    success_url = reverse_lazy('asistente:home')

    def get(self, request, *args, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if self.kwargs['usuario_id']:
            socio = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
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
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if self.kwargs['usuario_id']:
            socio = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        fecha_actual = date.today()
        if socio.fecha_ingreso is not None:
            num_anios = diasHastaFecha(socio.fecha_ingreso.day, socio.fecha_ingreso.month, socio.fecha_ingreso.year,
                                       fecha_actual.day,
                                       fecha_actual.month, fecha_actual.year) / 365
        else:
            num_anios = 0
            messages.error(self.request, 'El socio no tiene fecha de ingreso actualize sus datos')
        context["anios_servicio"] = int(num_anios)
        return context

    def form_valid(self, form):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if self.kwargs['usuario_id']:
            socio = Socio.objects.get(usuario_id=self.kwargs['usuario_id'])
        data = form.cleaned_data
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
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
        # if int(num_anios) < data['clasecredito'].tiempo_minimo_servicio:
        #     messages.error(self.request,
        #                    'El socio no cumple con el tiempo minimo de servicio para esta clase de prestamo')
        #     return redirect('asistente:solicitudcreditocreate', socio.usuario.id)

        for restriccion in data['clasecredito'].restricciones.all():
            if int(num_anios) >= restriccion.tiempo_min:
                if data['monto'] < restriccion.val_min or data['monto'] > restriccion.val_max:
                    messages.error(self.request,
                                   'Por favor  revise que el monto ingresado respete la restriccion del credito')
                    return redirect('asistente:solicitudcreditocreate', socio.usuario.id)

                if data['plazo'] > restriccion.plazo_max:
                    messages.error(self.request,
                                   'Por favor  revise que el plazo ingresado respete la restriccion del credito')
                    return redirect('asistente:solicitudcreditocreate', socio.usuario.id)
            else:
                messages.error(self.request,
                               'Por favor  revise su tiempo de servicio')
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


class SocioCreate(AsistenteRequiredMixin, CreateView):
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
    titulo = ' Rubros Moviestar unicamente'
    global rubros_generados_moviestar
    rubros_generados_moviestar = []
    if request.method == 'POST':
        if bool(request.FILES.get('archivo_rubros', False)):
            try:
                excel_file = request.FILES['archivo_rubros']

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

            except MultiValueDictKeyError:
                return redirect('asistente:home')
            except IndexError:
                messages.error(request, "Error al cargar el archivo pueda que no cumpla con el formato establecido.")
            except TypeError:
                messages.error(request, "Error al cargar el archivo pueda que no cumpla con el formato establecido.")
            else:
                return redirect('asistente:home')
    return render(request, 'asistente/rubro_subirarchivo.html', {'titulo': titulo})


clases_rubros = []
rubros_generados_general = []
colum_name = []


def cargar_rubros_general(request):
    global rubros_generados_general
    global clases_rubros
    clases_rubros = []
    rubros_generados_general = []
    titulo = 'Rubros en general'
    abreviaturas = []
    aux1 = []
    aux = []
    contador = 0
    rubroexistente = []
    if request.method == 'POST':
        if bool(request.FILES.get('archivo_rubros', False)):
            try:
                excel_file = request.FILES['archivo_rubros']
                if (str(excel_file).split('.')[-1] == "xls"):
                    data = xls_get(excel_file, column_limit=26)
                elif (str(excel_file).split('.')[-1] == "xlsx"):
                    data = xlsx_get(excel_file, column_limit=26)
                    rubros = data["Hoja1"]
                    size = len(rubros)
                    for num1, rubrosfilas in enumerate(rubros, start=0):
                        for num2, rubroscolum in enumerate(rubrosfilas, start=0):
                            if num1 == 4:
                                abreviaturas.append(rubros[num1][num2])
                        if num1 == 4:
                            for num3, abreviatura in enumerate(abreviaturas, start=0):
                                if abreviatura.strip(' ') != 'MOVI':
                                    if Rubro.objects.filter(abreviatura=abreviatura.strip(' ')).exists():
                                        rubroexistente = Rubro.objects.get(abreviatura=abreviatura.strip(' ')), num3
                                        clases_rubros.append(rubroexistente)
                                    # print(rubroexistente[0],rubroexistente[1])

                        if num1 > 3 and num1 < len(rubros) - 1:
                            for num2, rubroscolum in enumerate(rubrosfilas, start=0):
                                if contador == 0:
                                    if num2 == 0:
                                        aux.append("Nº")
                                    if num2 == 1:
                                        aux.append("Nombres")
                                    if num2 == 2:
                                        aux.append("Cédula")
                                    for rubroexis in clases_rubros:
                                        # print(rubroexis[1])
                                        if num2 == rubroexis[1]:
                                            aux.append(rubroscolum)

                            if contador == 0:
                                rubros_generados_general.append(aux)
                                aux = []
                            contador += 1
                            if Usuario.objects.filter(username=rubrosfilas[2]).exists():
                                usuario = Usuario.objects.get(username=rubrosfilas[2])
                                if Socio.objects.filter(usuario_id=usuario.id).exists():
                                    socio = Socio.objects.get(usuario_id=usuario.id)
                                    for num2, rubroscolum in enumerate(rubrosfilas, start=0):
                                        if contador > 0:
                                            if num2 >= 0 and num2 < 3:
                                                aux.append(rubroscolum)
                                            if num2 >= 4:
                                                for rubroexis in clases_rubros:
                                                    if num2 == rubroexis[1]:
                                                        aux.append(rubroscolum)

                                    rubros_generados_general.append(aux)
                                    aux = []
                    return redirect('asistente:guardarrubrosgeneral')
            except MultiValueDictKeyError:
                return redirect('asistente:home')
            except IndexError:
                messages.error(request, "Error al cargar el archivo pueda que no cumpla con el formato establecido.")
            except TypeError:
                messages.error(request, "Error al cargar el archivo pueda que no cumpla con el formato establecido.")
            else:
                return redirect('asistente:home')
    return render(request, 'asistente/rubro_subirarchivo.html', {'titulo': titulo})


def guardar_rubros_moviestar(request):
    global rubros_generados_moviestar
    if request.method == 'POST':
        for rubro in rubros_generados_moviestar:
            if Usuario.objects.filter(username=rubro[2]).exists():
                usuario = Usuario.objects.get(username=rubro[2])
                rubro_generado = RubroSocio.objects.create(rubro_id=1,
                                                           descripcion=rubro[3],
                                                           valor=rubro[12])

                socio = Socio.objects.get(usuario_id=usuario.id)
                socio.rubros.add(rubro_generado)
                socio.save()
        rubros_generados_moviestar = []
    return render(request, 'asistente/rubrosocioexcelmoviestar_list.html',
                  {'rubros_generados': rubros_generados_moviestar})


def guardar_rubros_general(request):
    global rubros_generados_general
    clases_rubros = []
    clases_rubros1 = []
    global colum_name
    if request.method == 'POST':
        for num1, rubrosfilas in enumerate(rubros_generados_general, start=0):
            if num1 == 0:
                for num2, rubroscolum in enumerate(rubrosfilas, start=0):
                    if num2 > 2:
                        rubroexistente = rubroscolum, num2
                        clases_rubros1.append(rubroexistente)
            if num1 > 0:
                for num2, rubroscolum in enumerate(rubrosfilas, start=0):
                    if num2 == 2:
                        usuario = Usuario.objects.get(username=rubroscolum)
                        socio = Socio.objects.get(usuario_id=usuario.id)
                    if num2 > 2:
                        if isinstance(rubroscolum, float) or isinstance(rubroscolum, int):
                            if rubroscolum > 0:
                                for clase in clases_rubros1:
                                    if num2 == clase[1]:
                                        print(clase[0])
                                        if clase[0] == 'PRESTAMO':
                                            if Credito.objects.filter(socio=socio).exists():
                                                print(socio.usuario.nombres)
                                                credito = Credito.objects.get(socio=socio, estado='aprobado')
                                                print(credito)
                                                valor_rubro = rubroscolum
                                                for cuota in credito.cuotas.all().order_by('orden'):
                                                    if cuota.estado == False:
                                                        print("valor1 ", rubroscolum)
                                                        print(type(rubroscolum))
                                                        valor_anterior = cuota.valor_cuota

                                                        valor_actual = float(valor_anterior) - rubroscolum
                                                        print("valor actual1", valor_actual)
                                                        rubroscolum = abs(valor_actual)
                                                        if valor_actual <= 0:
                                                            print("valor actual2", valor_actual)
                                                            cuota.estado = True
                                                            cuota.save()
                                                            print(cuota.estado)
                                                        if rubroscolum > 0 and cuota.estado == False:
                                                            print("valor 2", rubroscolum)
                                                            cuota.valor_cuota = valor_actual
                                                            cuota.save()
                                                            if rubroscolum > 0:
                                                                rubroscolum = 0

                                                rubro_generado = RubroSocio.objects.create(
                                                    rubro=Rubro.objects.get(
                                                        abreviatura=clase[0].strip(' ')),
                                                    descripcion=clase[0], valor=valor_rubro
                                                )
                                                socio.rubros.add(rubro_generado)
                                                socio.save()

                                        else:
                                            rubro_generado = RubroSocio.objects.create(
                                                rubro=Rubro.objects.get(abreviatura=clase[0].strip(' ')),
                                                descripcion=clase[0], valor=rubroscolum
                                            )
                                            socio.rubros.add(rubro_generado)
                                            socio.save()
        # for num1, rubrosfilas in enumerate(rubros_generados_general, start=0):
        #     if num1 == 0:
        #         for num2, rubroscolum in enumerate(rubrosfilas, start=0):
        #             if num2 > 2:
        #                 rubroexistente = rubroscolum, num2
        #                 clases_rubros.append(rubroexistente)
        #     if num1 > 0:
        #         for num2, rubroscolum in enumerate(rubrosfilas, start=0):
        #             if num2 == 2:
        #                 usuario = Usuario.objects.get(username=rubrosfilas[2])
        #                 socio = Socio.objects.get(usuario_id=usuario.id)
        #             if num2 > 2:
        #                 if isinstance(rubroscolum, float) or isinstance(rubroscolum, int):
        #                     if rubroscolum > 0:
        #                         for clase in clases_rubros:
        #                             if num2 == clase[1]:
        #                                 print(clase[0])
        #                                 rubro_generado = RubroSocio.objects.create(
        #                                     rubro=Rubro.objects.get(abreviatura=clase[0]),
        #                                     descripcion=clase[0]
        #                                 )
        #
        #                                 socio.rubros.add(rubro_generado)
        #                                 socio.save()

        messages.success(request, 'Rubros generados correctamente')
        rubros_generados_general = []
        clases_rubros = []
        return redirect('asistente:cargarrubrosgeneral')
    return render(request, 'asistente/rubrosocioexcelgeneral_list.html',
                  {'rubros_generados_general': rubros_generados_general, 'colum_name': colum_name})


class SocioUpdate(AsistenteRequiredMixin, UpdateView):
    model = Socio
    fields = ['fecha_ingreso', 'direccion', 'telefono', 'celular', 'cargo', 'area']
    template_name = 'asistente/socio_form.html'

    # def form_valid(self, form):
    #     data = form.cleaned_data
    #     Socio.objects.update(
    #         direccion=self.request.POST.get('direccion', ''),
    #         telefono=self.request.POST.get('telefono', ''),
    #         celular=self.request.POST.get('celular', ''),
    #         cargo=self.request.POST.get('cargo', ''),
    #         area=self.request.POST.get('area', ''),
    #         fecha_ingreso=self.request.POST.get('fecha_ingreso', None)
    #     )
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['socio'] = Socio.objects.get(usuario_id=self.object.id)

        context['is_asistente'] = True
        return context

    def get_success_url(self):
        messages.success(self.request, "Registro actualizado correctamente")
        return reverse_lazy('asistente:socioupdate', args=[self.object.id])


class SocioListView(AsistenteRequiredMixin, TemplateView):
    template_name = 'asistente/socio_list.html'


class TableSocioAsJSON(JSONResponseMixin, generic.View):
    model = Socio

    def get(self, request, *args, **kwargs):
        col_name_map = {
            '0': 'usuario',
            '1': 'usuario',
            '2': 'usuario',
            '3': 'usuario',
            '4': 'acciones',
        }
        object_list = self.model.objects.all()
        search_text = request.GET.get('sSearch', '').lower()
        start = int(request.GET.get('iDisplayStart', 0))
        delta = int(request.GET.get('iDisplayLength', 50))
        sort_dir = request.GET.get('sSortDir_0', 'asc')
        sort_col = int(request.GET.get('iSortCol_0', 0))
        sort_col_name = request.GET.get('mDataProp_%s' % sort_col, '1')
        sort_dir_prefix = (sort_dir == 'desc' and '-' or '')
        print(sort_col_name)
        print(col_name_map)

        if sort_col_name in col_name_map:
            sort_col = col_name_map[sort_col_name]
            print(sort_col)
            object_list = object_list.order_by('%s%s' % (sort_dir_prefix, sort_col))

        filtered_object_list = object_list
        if len(search_text) > 0:
            filtered_object_list = object_list.filter_on_search(search_text)

        json = {
            "iTotalRecords": object_list.count(),
            "iTotalDisplayRecords": filtered_object_list.count(),
            "sEcho": request.GET.get('sEcho', 1),
            "aaData": [obj.as_list() for obj in filtered_object_list[start:(start + delta)]]
        }
        return self.render_json_response(json)


class SocioDetailView(AsistenteRequiredMixin, DetailView):
    model = Socio
    template_name = 'asistente/socio_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = '/asistente/' + self.kwargs['back_url']
        context['back_url'] = back_url
        print(self.kwargs['back_url'])

        return context


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


class ClaseCreditoListView(AsistenteRequiredMixin, ListView):
    model = ClaseCredito
    template_name = 'asistente/clasecredito_list.html'


class ClaseCreditoDetailView(AsistenteRequiredMixin, DetailView):
    model = ClaseCredito
    template_name = 'asistente/clasecredito_detail.html'


class ClaseCreditoCreate(AsistenteRequiredMixin, CreateView):
    model = ClaseCredito
    fields = ['descripcion', 'garante', 'estado']
    template_name = 'asistente/clasecredito_form.html'

    def get_success_url(self):
        messages.success(self.request, "Registro creado exitosamente")
        return reverse_lazy('asistente:clasecreditolist')


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


class RubroCreate(AsistenteRequiredMixin, CreateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'abreviatura']
    success_url = reverse_lazy('asistente:rubrolist')
    template_name = 'asistente/rubro_form.html'


class RubroUpdate(AsistenteRequiredMixin, UpdateView):
    model = Rubro
    fields = ['descripcion', 'tipo', 'estado', 'valor', 'abreviatura']
    template_name = 'asistente/rubro_form.html'

    def get_success_url(self):
        return reverse_lazy('asistente:rubroupdate', args=[self.object.id]) + '?ok'


class RubroDelete(AsistenteRequiredMixin, DeleteView):
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


class RubroSocioCreate(AsistenteRequiredMixin, CreateView):
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


class RubroSocioDelete(AsistenteRequiredMixin, DeleteView):
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


class UsuarioUpdate(AsistenteRequiredMixin, UpdateView):
    model = Usuario
    template_name = 'asistente/perfil.html'
    fields = ['nombres', 'apellidos', 'fecha_nacimiento']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['socio'] = Socio.objects.get(usuario_id=self.request.user.id)
        return context

    def form_valid(self, form):
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


class CreditoListView(AsistenteRequiredMixin, ListView):
    model = Credito
    template_name = 'asistente/credito_list.html'


class CreditoDetail(AsistenteRequiredMixin, DetailView):
    model = Credito
    template_name = 'asistente/credito_detail.html'


class LicquidacionCreditoCreate(AsistenteRequiredMixin, CreateView):
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


def consultar_rubros(request):
    rubros = []
    socio = None
    if request.method == 'POST':
        username = request.POST['username']
        if Usuario.objects.filter(username=username).exists():
            usuario = Usuario.objects.get(username=username)
            if Socio.objects.filter(usuario_id=usuario.id).exists():
                socio = Socio.objects.get(usuario_id=usuario.id)
                for rubro in socio.rubros.all():
                    rubros.append(rubro)
                # if Credito.objects.filter(socio_id=socio.id).exists():
                #     credito = Credito.objects.get(socio_id=socio.id)
                #     for cuota in credito.cuotas.all():
                #         cuotas.append(cuota)
                # else:
                #     messages.error(request, 'El socio no mantiene ningun credito')
        else:
            messages.error(request, 'El socio no existe')
        # return redirect('asistente:consultarcuotas')
    return render(request, 'asistente/consultar_rubros.html', {'rubros': rubros, 'socio': socio})


class RestriccionClaseCreditoList(AsistenteRequiredMixin, TemplateView):
    template_name = 'asistente/restriccionclasecredito_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clasecreditos'] = ClaseCredito.objects.all()
        return context


# class RestriccionClaseCreditoList(AsistenteRequiredMixin, Tem):
#     model = RestriccionClaseCredito
#     template_name = 'asistente/restriccionclasecredito_list.html'

class RestriccionClaseCreditoDetail(AsistenteRequiredMixin, DetailView):
    model = RestriccionClaseCredito
    template_name = 'asistente/restriccionclasecredito_detail.html'


class RestriccionClaseCreditoCreate(AsistenteRequiredMixin, CreateView):
    model = RestriccionClaseCredito
    fields = ['tiempo_min', 'val_max', 'val_min', 'plazo_max', 'estado']
    template_name = 'asistente/restriccionclasecredito_form.html'

    def form_valid(self, form):
        clasecredito = ClaseCredito.objects.get(id=self.request.POST['clasecredito'])
        restriccionclasecredito = form.save(commit=False)
        restriccionclasecredito.save()
        clasecredito.restricciones.add(restriccionclasecredito)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clasecreditos'] = ClaseCredito.objects.all()
        return context

    def get_success_url(self):
        messages.success(self.request, "Registro creado exitosamente")
        return reverse_lazy('asistente:restriccionclasecreditolist')


PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
styles = getSampleStyleSheet()

pk_solicitudcredito = None


def generar_solicitud_pdf(request, pk):
    global pk_solicitudcredito
    pk_solicitudcredito = pk
    solicitudcredito = SolicitudCredito.objects.get(id=pk)
    buffer = io.BytesIO()
    firma_estilo = ParagraphStyle(
        name='firma_estilo',
        fontName="Times-Roman",
        alignment=TA_CENTER)
    doc = SimpleDocTemplate(buffer)
    story = [Spacer(0, 80)]
    linkStyle = ParagraphStyle(
        name='liknstyle',
        alignment=TA_CENTER,
        fontSize=18,

    )
    fecha_ingreso = Paragraph('<b>Fecha de ingreso: </b>' + str(solicitudcredito.fecha_ingreso))
    clase_nombre = Paragraph('<b>Clase de Crédito: </b>' + str(solicitudcredito.clasecredito.descripcion.title()))
    if solicitudcredito.revisada_por is not None:
        revisada_por = Paragraph('<b>Revisada por: </b>' + str(solicitudcredito.revisada_por.nombres.title()) + str(
            solicitudcredito.revisada_por.apellidos.title()))
    else:
        revisada_por = ''
    if solicitudcredito.aprobada_por is not None:
        aprobada_por = Paragraph('<b>Aprobada por: </b>' + str(solicitudcredito.aprobada_por.nombres.title()) + str(
            solicitudcredito.aprobada_por.apellidos.title()))
    else:
        aprobada_por = ''
    data = [[fecha_ingreso, clase_nombre], [revisada_por, aprobada_por]]
    t = Table(data)
    story.append(t)

    caja_subtitulo_estilo = ParagraphStyle(
        name='caja_subtitulo_estilo',
        fontName="Times-Roman",
        fontSize=12,
        leading=20,
        borderPadding=(5, 3, 2),
        backColor='#ededed',
        borderColor='#000000')
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph('INFORMACIÓN DEL SOCIO', caja_subtitulo_estilo))
    story.append(Spacer(1, 0.2 * inch))
    nombres_socio = Paragraph(str(solicitudcredito.socio.usuario.nombres.title()) + ' ' + str(
        solicitudcredito.socio.usuario.apellidos.title()))
    cedula_socio = Paragraph(str(solicitudcredito.socio.usuario.username))
    direccion_socio = Paragraph(str(solicitudcredito.socio.direccion))
    telefono_socio = Paragraph(str(solicitudcredito.socio.telefono))

    data1 = [[Paragraph('<b>Nombres y Apellidos:</b>'), nombres_socio],
             [Paragraph('<b>Cédula:</b>'), cedula_socio],
             [Paragraph('<b>Dirección:</b>'), direccion_socio],
             [Paragraph('<b>Teléfono:</b>'), telefono_socio],
             ]
    t1 = Table(data1)
    story.append(t1)
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph('DEPARTAMENTO Y/O FUNCIÓN DEL SOCIO', caja_subtitulo_estilo))
    story.append(Spacer(1, 0.2 * inch))
    fecha_actual = date.today()

    if solicitudcredito.socio.fecha_ingreso is not None:
        num_anios = diasHastaFecha(solicitudcredito.socio.fecha_ingreso.day, solicitudcredito.socio.fecha_ingreso.month,
                                   solicitudcredito.socio.fecha_ingreso.year,
                                   fecha_actual.day,
                                   fecha_actual.month, fecha_actual.year) / 365
    else:
        num_anios = ''
    data3 = [[Paragraph('<b>Departamento/Carrera:</b>'), Paragraph(str(solicitudcredito.socio.area))],
             [Paragraph('<b>Cargo:</b>'), Paragraph(str(solicitudcredito.socio.cargo))],
             [Paragraph('<b>Tiempo de servicio:</b>'), int(num_anios)],
             ]
    t3 = Table(data3)
    story.append(t3)
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph('MONTO DE CREDITO Y PERIODO DE PAGO', caja_subtitulo_estilo))
    story.append(Spacer(1, 0.2 * inch))
    data4 = [[Paragraph('<b>Cantidad solicitada:</b>'), Paragraph('$ ' + str(solicitudcredito.monto))],
             [Paragraph('<b>Plazo de pago:</b>'), Paragraph(str(solicitudcredito.plazo) + ' meses')],
             ]
    t4 = Table(data4)
    story.append(t4)
    story.append(Spacer(1, 2 * inch))
    d = Drawing(100, 1)
    d.add(Line(0, 0, 100, 0))
    data2 = [
        [[d, Paragraph('Firma del solicitante', firma_estilo)], [d, Paragraph('Firma de recepción', firma_estilo)]]]

    t2 = Table(data2)
    t2.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

    ]))
    story.append(t2)
    story.append(PageBreak())
    story.append(Paragraph('Cuotas',linkStyle))
    story.append(Spacer(1, 0.2 * inch))
    monto = float(solicitudcredito.monto)
    per = np.arange(1 * solicitudcredito.plazo) + 1
    ipmt = npf.ipmt(0.09 / 12, per, 1 * solicitudcredito.plazo, monto)
    ppmt = npf.ppmt(0.09 / 12, per, 1 * solicitudcredito.plazo, monto)
    pmt = npf.pmt(0.09 / 12, 1 * solicitudcredito.plazo, monto)
    np.allclose(ipmt + ppmt, pmt)
    fmt = '{0:2d} {1:8.2f} {2:8.2f} {3:8.2f}'
    cuotas = []
    cuotas.append(['N°', 'Capital', 'Interés', 'Saldo Capital', 'Valor cuota'])
    for payment in per:
        index = payment - 1
        monto = monto + ppmt[index]
        cuotas.append([payment, abs(round(ppmt[index], 2)), abs(round(ipmt[index], 2)), abs(round(monto, 2)),
                       round(abs(round(ppmt[index], 2)) + abs(round(ipmt[index], 2)), 2)])

    # data1 = [[Paragraph('<b>Nombres y Apellidos:</b>'), nombres_socio],
    #          [Paragraph('<b>Cédula:</b>'), cedula_socio],
    #          [Paragraph('<b>Dirección:</b>'), direccion_socio],
    #          [Paragraph('<b>Teléfono:</b>'), telefono_socio],
    #          ]
    tabla_cuotas = Table(cuotas)

    tabla_cuotas.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                      ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

    story.append(tabla_cuotas)
    doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='adetups_solicitudcredito.pdf')


# Definimos las caracteristicas fijas de la primera página
def myFirstPage(canvas, doc):
    global pk_solicitudcredito
    canvas.saveState()
    canvas.setTitle("Adetups_reportcredito")
    titulo = 'Solicitud de Crédito'
    archivo_imagen = 'asistente/static/img/logo_adetups.png'
    canvas.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True, mask='auto')
    canvas.setFont('Times-Roman', 18)
    canvas.drawString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, titulo)
    canvas.setFont('Times-Roman', 9)
    canvas.line(doc.leftMargin, PAGE_HEIGHT - 125, doc.width, PAGE_HEIGHT - 125)
    canvas.drawString(inch, 0.75 * inch, "Página %s" % (doc.page))
    canvas.restoreState()


# Definimos disposiciones alternas para las caracteristicas de las otras páginas
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Página %d" % (doc.page))
    canvas.restoreState()


def reportes_creditos(request):
    if request.method == 'POST':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        story = [Spacer(0, 80)]
        fecha_actual = Paragraph('<b>Fecha: </b>' + str(date.today()))
        clase_nombre = Paragraph('')
        data = [[fecha_actual, clase_nombre]]
        t = Table(data)
        story.append(t)
        story.append(Spacer(1, 0.4 * inch))
        datos = []
        datos.append([Paragraph('<b>Socio</b>'), Paragraph('<b>Monto</b>'), Paragraph('<b>Plazo</b>')])
        if request.POST['estado'] is not None:
            estado = request.POST['estado']
            if estado == 'pendiente':
                estado = 'PND'
            creditos = Credito.objects.filter(estado=estado)
            for credito in creditos:
                datos.append(
                    [credito.socio.usuario.nombres.title() + ' ' + credito.socio.usuario.apellidos.title(),
                     '$ ' + str(credito.monto), str(credito.plazo) + ' meses'])
        t = Table(datos)
        t.setStyle(TableStyle([

            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            # ('TEXTCOLOR', (1, 1), (-1, -1), colors.blue),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            # ('TEXTCOLOR', (0, 0), (2, 0), colors.green),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ]))
        story.append(t)
        doc.build(story, onFirstPage=primera_pagina_reportescreditos, onLaterPages=myLaterPages)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='adetups_reporte_creditos.pdf')
    return render(request, 'asistente/reportes_creditos.html')


def primera_pagina_reportescreditos(canvas, doc):
    global pk_solicitudcredito
    canvas.saveState()
    canvas.setTitle("Adetups_reportecredito")
    titulo = 'Créditos Adetups'
    archivo_imagen = 'asistente/static/img/logo_adetups.png'
    canvas.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True, mask='auto')
    canvas.setFont('Times-Roman', 18)
    canvas.drawString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, titulo)
    canvas.setFont('Times-Roman', 9)
    canvas.line(doc.leftMargin, PAGE_HEIGHT - 125, doc.width, PAGE_HEIGHT - 125)
    canvas.drawString(inch, 0.75 * inch, "Página %s" % (doc.page))
    canvas.restoreState()

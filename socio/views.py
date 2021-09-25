import io
from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import AccessMixin
from django.http import FileResponse
from django.shortcuts import render, redirect
from socio.forms import SolicitudCreditoForm
from django.urls import reverse_lazy
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib import colors
from django.db.models import Q
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
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


def calcular_tiempo_servicio(fecha_ingreso):
    return int(diasHastaFecha(fecha_ingreso.day, fecha_ingreso.month, fecha_ingreso.year,
                              date.today().day,
                              date.today().month, date.today().year) / 365)


class SolicitudCreditoCreate(SocioRequiredMixin, CreateView):
    model = SolicitudCredito
    form_class = SolicitudCreditoForm
    template_name = 'socio/solicitudcredito_form.html'
    success_url = reverse_lazy('socio:home')

    def get(self, request, *args, **kwargs):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        if Credito.objects.filter(socio=socio, estado='aprobado').exists():
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
        socio = Socio.objects.get(usuario_id=self.request.user.id)
        garantes = Socio.objects.filter(is_garante=False).filter(~Q(id=socio.id))
        context["socio"] = socio
        context["garantes"] = garantes
        num_anios = 0
        if socio.fecha_ingreso is not None:
            num_anios = calcular_tiempo_servicio(socio.fecha_ingreso)
        else:
            messages.error(self.request, 'El socio no tiene fecha de ingreso actualize sus datos por favor.')
        context["anios_servicio"] = num_anios
        return context

    def form_valid(self, form):
        socio = Socio.objects.get(usuario_id=self.request.user.id)
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


class UsuarioUpdate(SocioRequiredMixin, UpdateView):
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
        'link',
        textColor='#3366BB'
    )
    fecha_ingreso = Paragraph('<b>Fecha de ingreso: </b>' + str(solicitudcredito.fecha_ingreso))
    clase_nombre = Paragraph('<b>Clase de Crédito: </b>' + str(solicitudcredito.clasecredito.descripcion.title()))
    data = [[fecha_ingreso, clase_nombre]]
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
             [Paragraph('<b>Tiempo de servicio:</b>'), num_anios],
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
    doc.build(story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='adetups_solicitudcredito.pdf')


# Definimos las caracteristicas fijas de la primera página
def myFirstPage(canvas, doc):
    global pk_solicitudcredito
    canvas.saveState()
    canvas.setTitle("Adetups_reportcredito")
    titulo = 'Solicitud de Crédito Nro. ' + str(pk_solicitudcredito)
    archivo_imagen = 'asistente/static/img/logo_adetups.png'
    #canvas.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True, mask='auto')
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

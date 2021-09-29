import io
import numpy as np
import numpy_financial as npf
from datetime import date
from adetups.utils import contar_dias
from sistema.models import SolicitudCredito
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib import colors
from django.http import FileResponse
from reportes.models import *

PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
styles = getSampleStyleSheet()
linkStyle = ParagraphStyle(
    name='liknstyle',
    alignment=TA_CENTER,
    fontSize=18,

)


def crear_tabla_cuotas(story, solicitudcredito):
    story.append(Paragraph('Cuotas', linkStyle))
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

    tabla_cuotas = Table(cuotas)
    tabla_cuotas.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                      ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))
    story.append(tabla_cuotas)


def generar_reporte_solicitudcredito(request, id):
    # Definimos las caracteristicas fijas de la primera página
    def primera_pagina(canvas, doc):
        canvas.saveState()
        canvas.setTitle("Adetups_reportcredito")
        titulo = 'Solicitud de Crédito Nro. ' + str(id)
        reporte_configuracion = ReporteConfiguracion.objects.get(nombre='SOLICITUD_CREDITO')
        canvas.drawImage(reporte_configuracion.logo.path, 40, 750, 120, 90, preserveAspectRatio=True, mask='auto')
        canvas.setFont('Times-Roman', 18)
        canvas.drawString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, titulo)
        canvas.setFont('Times-Roman', 9)
        canvas.line(doc.leftMargin, PAGE_HEIGHT - 125, doc.width, PAGE_HEIGHT - 125)
        canvas.drawString(inch, 0.75 * inch, "Página %s" % (doc.page))
        canvas.restoreState()

    # Definimos disposiciones alternas para las caracteristicas de las otras páginas
    def paginas_restantes(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch, "Página %d" % (doc.page))
        canvas.restoreState()

    solicitudcredito = SolicitudCredito.objects.get(id=id)
    buffer = io.BytesIO()
    firma_estilo = ParagraphStyle(
        name='firma_estilo',
        fontName="Times-Roman",
        alignment=TA_CENTER)
    doc = SimpleDocTemplate(buffer)
    story = [Spacer(0, 80)]

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
        num_anios = int(contar_dias(solicitudcredito.socio.fecha_ingreso.day,
                                    solicitudcredito.socio.fecha_ingreso.month,
                                    solicitudcredito.socio.fecha_ingreso.year,
                                    fecha_actual.day,
                                    fecha_actual.month, fecha_actual.year) / 365)
    else:
        num_anios = ''
    data3 = [[Paragraph('<b>Departamento/Carrera:</b>'), Paragraph(str(solicitudcredito.socio.area))],
             [Paragraph('<b>Cargo:</b>'), Paragraph(str(solicitudcredito.socio.cargo))],
             [Paragraph('<b>Tiempo de servicio:</b>'), str(num_anios) + ' años'],
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
    crear_tabla_cuotas(story, solicitudcredito)
    doc.build(story, onFirstPage=primera_pagina, onLaterPages=paginas_restantes)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='adetups_solicitudcredito.pdf')

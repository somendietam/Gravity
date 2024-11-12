import openpyxl
from abc import ABC, abstractmethod
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

#Definición de interfaz ReporteGenerator
class ReporteGenerator(ABC):
    @abstractmethod
    def generar_factura(self, pedido):
        """Genera una factura para el pedido dado"""
        pass

class PDFReporteGenerator(ReporteGenerator):
    def generar_factura(self, pedido):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pedido.id}.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, f"Factura #{pedido.id}")
        p.drawString(100, 730, f"Fecha: {pedido.fecha}")
        p.drawString(100, 710, f"Método de Pago: {pedido.metodoPago}")
        p.drawString(100, 690, f"Dirección de Entrega: {pedido.direccionEntrega}")
        p.drawString(100, 670, f"Total a Pagar: ${pedido.totalPagar}")

        p.drawString(100, 640, "Productos:")
        y = 620
        for detalle in pedido.pedidoproducto_set.all():
            p.drawString(100, y, f"{detalle.producto.nombre} - Cantidad: {detalle.cantidad} - Total: ${detalle.total}")
            y -= 20  # Mueve hacia abajo para el siguiente producto

        p.showPage()
        p.save()
        return response
    
class ExcelReporteGenerator(ReporteGenerator):
    def generar_factura(self, pedido):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = f"Factura #{pedido.id}"

        # Información general del pedido
        sheet["A1"] = f"Factura #{pedido.id}"
        sheet["A2"] = f"Fecha: {pedido.fecha}"
        sheet["A3"] = f"Método de Pago: {pedido.metodoPago}"
        sheet["A4"] = f"Dirección de Entrega: {pedido.direccionEntrega}"
        sheet["A5"] = f"Total a Pagar: ${pedido.totalPagar}"

        # Detalle de productos
        sheet["A7"] = "Productos:"
        row = 8
        for detalle in pedido.pedidoproducto_set.all():
            sheet[f"A{row}"] = detalle.producto.nombre
            sheet[f"B{row}"] = f"Cantidad: {detalle.cantidad}"
            sheet[f"C{row}"] = f"Total: ${detalle.total}"
            row += 1

        # Guardar el archivo en memoria y devolverlo
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="factura_{pedido.id}.xlsx"'
        return response
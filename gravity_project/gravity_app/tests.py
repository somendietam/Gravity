from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Producto, Cliente, CarritoCompras, Categoria, Pedido
from datetime import datetime

class ProductoEnStockTest(TestCase):
    def setUp(self):
        # Crear una categoría por defecto para los productos
        self.categoria = Categoria.objects.create(nombre="Categoría Test")
        
        # Crear algunos productos con la categoría asignada
        Producto.objects.create(nombre="Producto1", descripcion="Desc1", precio=10.0, stock=5, categoria=self.categoria)
        Producto.objects.create(nombre="Producto2", descripcion="Desc2", precio=15.0, stock=0, categoria=self.categoria)  # Sin stock

    def test_productos_en_stock_endpoint(self):
        url = reverse('productos_en_stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Verificar que la respuesta es 200
        data = response.json()
        self.assertIn("productos", data)  # Verificar que existe la clave "productos" en la respuesta
        # Verificar que solo se devuelven productos con stock
        self.assertTrue(all(producto['stock'] > 0 for producto in data['productos']))

class FacturaGenerationTests(TestCase):
    def setUp(self):
        # Configuración de un usuario y un pedido de prueba
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.cliente = Cliente.objects.create(user=self.user, direccion="Test Address")
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            metodoPago="Tarjeta",
            totalPagar=100.00,
            fecha=datetime.now()  # Asigna la fecha actual
        )
        self.client.login(username='testuser', password='testpassword')  # Autenticación del usuario

    def test_generar_factura_pdf(self):
        """Prueba la generación de la factura en formato PDF."""
        url = reverse('generar_factura', args=[self.pedido.id]) + '?formato=pdf'
        response = self.client.get(url)

        # Verificar que la respuesta sea exitosa y tenga el tipo de contenido esperado
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(b'%PDF', response.content[:10], "El archivo generado no parece ser un PDF válido.")

    def test_generar_factura_excel(self):
        """Prueba la generación de la factura en formato Excel."""
        url = reverse('generar_factura', args=[self.pedido.id]) + '?formato=excel'
        response = self.client.get(url)

        # Verificar que la respuesta sea exitosa y tenga el tipo de contenido esperado
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(response.content, "El archivo generado no parece ser un archivo Excel válido.")
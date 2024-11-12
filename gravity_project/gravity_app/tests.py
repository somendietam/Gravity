from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Producto, Cliente, CarritoCompras, Categoria

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


import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    def verCategoria(self):
        return self.nombre
    
    @classmethod
    def listarCategorias(cls):
        return cls.objects.all()

class Producto(models.Model):
    id = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    stock = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def verDetallesProducto(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': str(self.precio),  # Convertir a string si es necesario
            'descripcion': self.descripcion,
            'stock': self.stock,
            'categoria': self.categoria.verCategoria()  # Usar el método de Categoria
        }

    def save(self, *args, **kwargs):
        if self.stock < 0:
            raise ValueError('El stock no puede ser negativo')
        super().save(*args, **kwargs)


class CarritoCompras(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, null=True, related_name='carrito_compra')
    numeroProductos = models.IntegerField(default=0)
    productos = models.ManyToManyField(Producto)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    def verCarritoCompras(self):
        return self.productos.all()

    def agregarProducto(self, producto, cantidad):
        # Agrega el producto y actualiza el total
        self.productos.add(producto)
        self.numeroProductos += cantidad
        self.total += producto.precio * cantidad
        producto.stock -= cantidad
        producto.save()  # Actualiza el stock del producto
        self.save()  # Guarda el carrito actualizado

    def eliminarProducto(self, producto, cantidad):
        self.productos.remove(producto)
        self.numeroProductos -= cantidad
        self.total -= producto.precio * cantidad
        producto.stock += cantidad
        producto.save()
        self.save()
    
class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    carrito = models.OneToOneField(CarritoCompras, on_delete=models.CASCADE, null=True, related_name='cliente_compra')
    pedido = models.ManyToManyField('Pedido', related_name='clientes')

    def anadirAlCarrito(self, producto, cantidad):
        if producto.stock < cantidad:
            raise ValueError(f"No hay suficiente stock de {producto.nombre}")
        else:
            self.carrito.agregarProducto(producto, cantidad)

    def removerDelCarrito(self, producto, cantidad):
        if producto not in self.carrito.productos.all():
            raise ValueError(f"El producto {producto.nombre} no está en el carrito.")

        elif cantidad > self.carrito.productos.filter(id=producto.id).count():
            raise ValueError(f"Estás intentando eliminar más {producto.nombre} de los que hay en el carrito.")
    
        else:
            self.carrito.eliminarProducto(producto, cantidad)

    def buscarProducto(self, nombre):
        producto = Producto.objects.filter(nombre__icontains=nombre)  # Búsqueda insensible a mayúsculas
        return producto

    def pagarPedido(self, metodo_pago, direccion_entrega):
        if not self.carrito.productos.exists():
            raise ValueError("No hay productos en el carrito para realizar el pedido.")

        # Crear un nuevo pedido
        pedido = Pedido(
            cliente=self,
            fecha=datetime.date.today(),
            metodoPago=metodo_pago,
            direccionEntrega=direccion_entrega,
            totalPagar=self.carrito.total
        )
        pedido.save()

        # Crear detalles del pedido a través de PedidoProducto
        for producto in self.carrito.productos.all():
            cantidad = self.carrito.productos.filter(id=producto.id).count()
            total = producto.precio * cantidad
            PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, total=total)

        # Vaciar el carrito
        self.carrito.productos.clear()
        self.carrito.total = 0
        self.carrito.numeroProductos = 0
        self.carrito.save()

        return pedido  # Retorna el pedido creado

class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    metodoPago = models.CharField(max_length=50)
    numGuia = models.CharField(max_length=50, null=True)
    direccionEntrega = models.CharField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    productos = models.ManyToManyField(Producto, through='PedidoProducto')  # Relación con productos
    totalPagar = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def verPedido(self):
        return f'Pedido {self.id}: {self.metodoPago}, Total: {self.totalPagar}'

class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'
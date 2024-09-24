import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

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
    numeroProductos = models.IntegerField()
    productos = models.ManyToManyField(Producto)
    total = models.DecimalField(max_digits=10, decimal_places=2)

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
    carrito = models.OneToOneField(CarritoCompras, on_delete=models.CASCADE, null=True)
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

        # Crear detalles del pedido
        for producto in self.carrito.productos.all():
            cantidad = self.carrito.productos.filter(id=producto.id).count()
            detalle = DetallePedido(
                pedido=pedido,
                item=producto.nombre,
                cantidad=cantidad,
                total=producto.precio * cantidad
            )
            detalle.save()

        # Llamar al método pagar del pedido
        pedido.pagar()

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
    numGuia = models.CharField(max_length=50)
    direccionEntrega = models.CharField(max_length=255)
    detalles = models.ManyToManyField('DetallePedido', related_name='pedidos')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    totalPagar = models.DecimalField(max_digits=10, decimal_places=2)

    def verPedido(self):
        return f'Pedido {self.id}: {self.metodoPago}'
    
    def pagar(self):
        print(f"Pedido {self.id} pagado exitosamente.")

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def verDetallePedido(self):
        return f'Item: {self.item}, Cantidad: {self.cantidad}, Total: {self.total}'
from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=100)

    def registrar(self):
        # Lógica para registrar el usuario
        pass

    def ingresar(self, correo, contrasena):
        # Lógica para autenticar el usuario
        pass

class Producto(models.Model):
    id = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    stock = models.IntegerField()

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

    def generarOrden(self):
        # Lógica para generar la orden
        pass

    def agregar_producto(self, producto, cantidad):
        # Agrega el producto y actualiza el total
        self.productos.add(producto)
        self.numeroProductos += cantidad
        self.total += producto.precio * cantidad
        producto.stock -= cantidad
        producto.save()  # Actualiza el stock del producto
        self.save()  # Guarda el carrito actualizado

class Cliente(Usuario):
    direccion = models.CharField(max_length=255)
    carrito = models.OneToOneField(CarritoCompras, on_delete=models.CASCADE, null=True)

    def anadirAlCarrito(self, producto, cantidad):
        if producto.stock < cantidad:
            raise ValueError(f"No hay suficiente stock de {producto.nombre}")
        else:
            self.carrito.agregar_producto(producto, cantidad)

class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField()
    metodoPago = models.CharField(max_length=50)
    numGuia = models.CharField(max_length=50)
    direccionEntrega = models.CharField(max_length=255)
    detalles = models.ManyToManyField('DetallePedido')

    def verPedido(self):
        return f'Pedido {self.id}: {self.metodoPago}'

class DetallePedido(models.Model):
    item = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def verDetallePedido(self):
        return f'Item: {self.item}, Cantidad: {self.cantidad}, Total: {self.total}'


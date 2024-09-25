from django.shortcuts import render, redirect, get_object_or_404    
from django.contrib.auth.decorators import login_required
from .models import Producto, CarritoCompras, Cliente, ProductoEnCarrito, Pedido, PedidoProducto, Categoria
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProductoForm

def index(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'gravity_app/index.html', context)

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            cliente = Cliente(user=user, direccion="") # Crear un cliente asociado al nuevo usuario
            cliente.save()
            carrito = CarritoCompras(cliente=cliente) # Crear un carrito y asociarlo al cliente
            carrito.save()
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect("login")
    return render(request, "gravity_app/register.html")

# Vista para el login
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "gravity_app/login.html")

# Vista para cerrar sesión
def user_logout(request):
    logout(request)
    return redirect("index")

@staff_member_required
def admin_panel(request):
    productos = Producto.objects.all()
    return render(request, "gravity_app/admin_panel.html", {"productos": productos})

@staff_member_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)  # Si tienes campos de imagen
        if form.is_valid():
            form.save()  # Guarda el nuevo producto
            return redirect('admin_panel')  # Redirige a la vista de administración
    else:
        form = ProductoForm()

    return render(request, 'gravity_app/crear_producto.html', {'form': form})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    cliente = Cliente.objects.get(user=request.user)

    if not cliente.carrito:
        carrito = CarritoCompras(cliente=cliente)
        carrito.save()
        cliente.carrito = carrito  # Asignar el carrito al cliente
        cliente.save()

    cliente.anadirAlCarrito(producto, 1)  # Agregar 1 producto al carrito
    return redirect('index')  # Redirigir de nuevo a la página de inicio

@login_required
def eliminar_del_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    cliente = Cliente.objects.get(user=request.user)

    if not cliente.carrito:
        messages.error(request, "No tienes un carrito activo.")
        return redirect('tu_carrito')

    try:
        # Aquí se especifica que solo se elimina 1 unidad
        cliente.carrito.eliminarProducto(producto, 1)
        messages.success(request, f"Se eliminó 1 unidad de {producto.nombre} del carrito.")
    except ProductoEnCarrito.DoesNotExist:
        messages.error(request, "El producto no está en el carrito.")

    return redirect('tu_carrito')


@login_required
def ver_carrito(request):
    cliente = Cliente.objects.get(user=request.user)
    return render(request, 'gravity_app/carrito.html', {'carrito': cliente.carrito})

def buscar_productos(request):
    query = request.GET.get('q', '')
    categoria_nombre = request.GET.get('categoria', None)  # Capture the category name from URL parameters
    productos = Producto.objects.all()  # Start by fetching all products

    # Filter by category if provided
    if categoria_nombre:
        productos = productos.filter(categoria__nombre__iexact=categoria_nombre)  # Filter by exact category name

    # Tokenize and filter by query if provided
    if query:
        tokens = query.split()  # Split the query into tokens
        # Search for productos matching any of the tokens
        productos = productos.filter(nombre__icontains=tokens[0])  # Start filtering with the first token
        for token in tokens[1:]:
            productos = productos | Producto.objects.filter(nombre__icontains=token)

    context = {
        'productos': productos,
        'query': query,
        'categoria_nombre': categoria_nombre  # Pass the selected category name to the template
    }

    return render(request, 'gravity_app/buscar.html', context)

@login_required
def pagar_pedido(request):
    cliente = request.user.cliente
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        direccion_entrega = request.POST.get('direccion_entrega')

        try:
            # Intentar realizar el pago del pedido
            pedido = cliente.pagarPedido(metodo_pago, direccion_entrega)
            messages.success(request, f'Pedido realizado con éxito. Pedido ID: {pedido.id}')
            return redirect('detalle_pedido', pedido_id=pedido.id)

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('ver_carrito')

    return render(request, 'gravity_app/pagar_pedido.html', {
        'carrito': cliente.carrito
    })

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user.cliente)
    return render(request, 'gravity_app/detalle_pedido.html', {'pedido': pedido})

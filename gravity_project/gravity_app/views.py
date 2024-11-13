#AUTOR: Todos.

from django.shortcuts import render, redirect, get_object_or_404    
from django.contrib.auth.decorators import login_required
from .models import Producto, CarritoCompras, Cliente, ProductoEnCarrito, Pedido, PedidoProducto, Categoria
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProductoForm
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .forms import ProductoForm, CategoriaForm
from .reportes import PDFReporteGenerator, ExcelReporteGenerator
from dotenv import load_dotenv
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import os

load_dotenv()

apikey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apikey)

def ai_clothes_suggestion(request):
    if request.method == "POST":
        user_suggestion = request.POST.get("sugerencia")

        # Fetch products and format prompt (same as before)
        products = Producto.objects.all()
        product_list = "\n".join([f"- Nombre: {product.nombre} / Descripcion: {product.descripcion} / id: {product.id}" for product in products])
        
        prompt = (
            f"Here is a list of available clothing items:\n{product_list}\n\n"
            f"Based on the following suggestion by the user, generate an outfit with THE 'id' of the items selected separated by a ';'. Nothing else, no funny text or anything like that, just the numbers separated so I can format them. Example: 543;53156;854. If there are no good clothes to suggest just give a random outfit (Pants and top and accesories if there is any).\n"
            f"User suggestion: {user_suggestion}"
        )

        # Call OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Process AI's response and extract IDs
        ai_suggestion = completion.choices[0].message.content
        print("Outfit Sugerido:", ai_suggestion)

        # Split AI's response by ';' to get individual product IDs
        product_ids = ai_suggestion.split(';')
        
        # Build the query parameter string with IDs
        ids_query = ",".join(product_ids)

        buscar_url = f"{reverse('buscar_productos')}?ids={ids_query}&suggestion={user_suggestion}"
        return redirect(buscar_url)


    return JsonResponse({"error": "Método no permitido"}, status=405)

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
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = CategoriaForm()
    return render(request, 'gravity_app/crear_categoria.html', {'form': form})

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


@staff_member_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()  # Guarda el producto editado
            return redirect('admin_panel')  # Redirige a la vista del panel de admin
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'gravity_app/editar_producto.html', {'form': form, 'producto': producto})

@staff_member_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('admin_panel')

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
    categoria_nombre = request.GET.get('categoria', '')
    orden = request.GET.get('orden', None)
    
    # Obtener el parámetro 'ids' de la URL
    id_lista = request.GET.get('ids', '')
    productos = Producto.objects.all()  # Iniciar con todos los productos

    # Si 'ids' está presente, filtrar los productos
    if id_lista:
        # Separar los IDs por coma y convertirlos a enteros
        id_lista = [int(id.strip()) for id in id_lista.split(',') if id.strip()]
        print("ID_LISTA", id_lista)  # Imprimir la lista para depuración
        productos = productos.filter(id__in=id_lista)  # Filtrar por los IDs

    # Filtrar por categoría si se proporciona
    if categoria_nombre:
        productos = productos.filter(categoria__nombre__iexact=categoria_nombre)

    # Filtrar por consulta si se proporciona
    if query:
        tokens = query.split()
        productos = productos.filter(nombre__icontains=tokens[0])
        for token in tokens[1:]:
            productos = productos | Producto.objects.filter(nombre__icontains=token)

    # Aplicar ordenación según el filtro seleccionado
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'stock_asc':
        productos = productos.order_by('stock')

    # Aquí pasamos el prompt de IA si está disponible
    suggestion = request.GET.get('suggestion', '')  # Este es el prompt que usó el usuario

    context = {
        'productos': productos,
        'query': query,
        'categoria_nombre': categoria_nombre,
        'orden': orden,
        'suggestion': suggestion,
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

@login_required
def generar_factura(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    
    formato = request.GET.get('formato', 'pdf') 
    if formato == 'excel':
        reporte_generator = ExcelReporteGenerator()
    else:
        reporte_generator = PDFReporteGenerator()

    return reporte_generator.generar_factura(pedido)
   
def productos_en_stock(request):
    productos = Producto.objects.filter(stock__gt=0)  # Filtra productos con stock disponible
    data = {
        "productos": [
            {
                "id": producto.id,
                "nombre": producto.nombre,
                "descripcion": producto.descripcion,
                "precio": str(producto.precio),  # Convertir a string para evitar errores de serialización
                "stock": producto.stock
            }
            for producto in productos
        ]
    }
    return JsonResponse(data)

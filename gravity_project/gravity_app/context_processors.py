from .models import Categoria

def categorias(request):
    categorias = Categoria.objects.all()  # Fetch all categories
    return {
        'categorias': categorias  # Return as part of context
    }
from django import forms
from .models import Producto, Categoria # Asegúrate de que tengas un modelo de Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'stock', 'categoria', 'imagen']  # Los campos de tu modelo Producto

    # Sobrescribimos la representación de la categoría en el dropdown
    categoria = forms.ModelChoiceField(
        queryset=Categoria.listarCategorias(),
        label='Categoría',
        to_field_name='id'
    )

    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields['categoria'].label_from_instance = lambda obj: obj.verCategoria()
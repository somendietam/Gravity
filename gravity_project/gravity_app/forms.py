from django import forms
from .models import Producto, Categoria # Asegúrate de que tengas un modelo de Producto
from .models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

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

        # Si el producto ya existe (es una edición), se elimina el campo 'imagen'
        if self.instance and self.instance.pk:
            self.fields.pop('imagen')
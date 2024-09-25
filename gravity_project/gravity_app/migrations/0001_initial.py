# Generated by Django 5.1 on 2024-09-25 05:16

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CarritoCompras',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numeroProductos', models.IntegerField(default=0)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=255)),
                ('carrito', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cliente_compra', to='gravity_app.carritocompras')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='carritocompras',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carrito_compra', to='gravity_app.cliente'),
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('metodoPago', models.CharField(max_length=50)),
                ('numGuia', models.CharField(max_length=50, null=True)),
                ('direccionEntrega', models.CharField(max_length=255)),
                ('totalPagar', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='gravity_app.cliente')),
            ],
        ),
        migrations.AddField(
            model_name='cliente',
            name='pedido',
            field=models.ManyToManyField(related_name='clientes', to='gravity_app.pedido'),
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.TextField()),
                ('stock', models.IntegerField()),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gravity_app.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='PedidoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gravity_app.pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gravity_app.producto')),
            ],
        ),
        migrations.AddField(
            model_name='pedido',
            name='productos',
            field=models.ManyToManyField(through='gravity_app.PedidoProducto', to='gravity_app.producto'),
        ),
        migrations.CreateModel(
            name='ProductoEnCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(default=1)),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_en_carrito', to='gravity_app.carritocompras')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gravity_app.producto')),
            ],
        ),
    ]

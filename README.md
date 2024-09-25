## Configuración del Entorno Virtual e Instalación de Dependencias

### 1. Crear un entorno virtual
```bash
python3 -m venv env
```

### 2. Activar el entorno virtual

- En Linux/Mac:
  ```bash
  source env/bin/activate
  ```
  
- En Windows:
  ```bash
  .\env\Scripts\activate
  ```

### 3. Instalar las dependencias

Con el entorno virtual activado, ejecuta el siguiente comando para instalar Django y ReportLab:

```bash
pip install django reportlab
```

### 4. Ejecutar la aplicación

Con todas las dependencias instaladas, puedes ejecutar el servidor de desarrollo de Django:

```bash
python manage.py runserver
```
#Despliegue
```bash
http://3.212.242.247:8000/
```

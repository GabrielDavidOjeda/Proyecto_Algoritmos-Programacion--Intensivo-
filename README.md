[README.md](https://github.com/user-attachments/files/21691222/README.md)
# Sistema de Catálogo del Museo Metropolitano de Arte

Una aplicación Python desarrollada con Programación Orientada a Objetos (POO) que permite explorar la colección del Metropolitan Museum of Art a través de su API oficial.

## 📋 Descripción

Este sistema permite a los usuarios buscar y visualizar obras de arte utilizando diferentes criterios:
- **Búsqueda por departamento**: Explora colecciones organizadas por área temática
- **Búsqueda por nacionalidad**: Encuentra obras de artistas de culturas específicas  
- **Búsqueda por artista**: Localiza trabajos de artistas específicos
- **Visualización detallada**: Ve información completa e imágenes de las obras

## 🚀 Características

- ✅ Interfaz de usuario intuitiva por consola
- ✅ Integración con la API oficial del Metropolitan Museum
- ✅ Visualización de imágenes en ventanas separadas
- ✅ Manejo robusto de errores y excepciones
- ✅ Arquitectura modular basada en POO
- ✅ Validación automática de recursos del sistema
- ✅ Modo debug para desarrollo y troubleshooting

## 📦 Requisitos del Sistema

### Software Requerido
- **Python 3.7 o superior**
- **Conexión a internet** (para acceder a la API del museo)

### Dependencias de Python
- `requests` - Comunicación HTTP con la API
- `Pillow` - Procesamiento de imágenes
- `tkinter` - Interfaz gráfica (incluido con Python estándar)

### Archivos de Recursos
- `nacionalidades.txt` - Lista de nacionalidades disponibles para búsqueda

## 🔧 Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <url-del-repositorio>
cd museo-catalogo-arte
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv .venv

# En Windows
.venv\Scripts\activate

# En Linux/macOS
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar instalación
```bash
python main.py --check-resources
```

## 🎯 Uso

### Ejecución Básica
```bash
python main.py
```

### Opciones de Línea de Comandos

```bash
# Mostrar ayuda
python main.py --help

# Mostrar versión
python main.py --version

# Verificar recursos sin iniciar la aplicación
python main.py --check-resources

# Usar archivo de nacionalidades personalizado
python main.py --nacionalidades mi_archivo.txt

# Activar modo debug
python main.py --debug
```

### Navegación en la Aplicación

1. **Menú Principal**: Selecciona el tipo de búsqueda deseada
2. **Búsqueda por Departamento**: 
   - Selecciona un departamento de la lista
   - Ve las obras disponibles
3. **Búsqueda por Nacionalidad**:
   - Selecciona una nacionalidad de la lista
   - Explora obras de artistas de esa nacionalidad
4. **Búsqueda por Artista**:
   - Ingresa el nombre del artista (búsqueda parcial soportada)
   - Ve las obras encontradas
5. **Detalles de Obra**:
   - Ingresa el ID de una obra para ver información completa
   - Opción de visualizar imagen en ventana separada

### Ejemplos de Uso Detallados

#### Ejemplo 1: Búsqueda por Departamento
```
$ python main.py

=== SISTEMA DE CATÁLOGO DEL MUSEO METROPOLITANO DE ARTE ===

Menú Principal:
1. Buscar por departamento
2. Buscar por nacionalidad del artista
3. Buscar por nombre del artista
4. Ver detalles de una obra específica
5. Salir

Seleccione una opción (1-5): 1

Departamentos disponibles:
1. American Decorative Arts
2. Ancient Near Eastern Art
3. European Paintings
...

Seleccione un departamento (1-21): 3

Obras encontradas en European Paintings:
ID: 436535 | Título: The Harvesters | Artista: Pieter Bruegel the Elder
ID: 437853 | Título: The Starry Night | Artista: Vincent van Gogh
...

¿Desea ver detalles de alguna obra? (s/n): s
Ingrese el ID de la obra: 436535
```

#### Ejemplo 2: Búsqueda por Nacionalidad
```
Seleccione una opción (1-5): 2

Nacionalidades disponibles:
1. American
2. Dutch
3. French
4. Italian
...

Seleccione una nacionalidad (1-50): 2

Obras de artistas Dutch:
ID: 436535 | Título: The Harvesters | Artista: Pieter Bruegel the Elder
ID: 437853 | Título: The Starry Night | Artista: Vincent van Gogh
...
```

#### Ejemplo 3: Búsqueda por Artista
```
Seleccione una opción (1-5): 3

Ingrese el nombre del artista (puede ser parcial): Van Gogh

Obras encontradas para "Van Gogh":
ID: 437853 | Título: The Starry Night | Artista: Vincent van Gogh
ID: 437854 | Título: Sunflowers | Artista: Vincent van Gogh
...
```

#### Ejemplo 4: Ver Detalles de Obra
```
Seleccione una opción (1-5): 4

Ingrese el ID de la obra: 436535

=== DETALLES DE LA OBRA ===
ID: 436535
Título: The Harvesters
Artista: Pieter Bruegel the Elder
Nacionalidad del artista: Netherlandish
Fecha de nacimiento: 1525
Fecha de muerte: 1569
Clasificación: Paintings
Año de creación: 1565
Departamento: European Paintings

¿Desea ver la imagen de esta obra? (s/n): s
[Se abre ventana con la imagen]
```

## 📁 Estructura del Proyecto

```
museo-catalogo-arte/
├── main.py                     # Punto de entrada principal
├── controlador_principal.py    # Controlador principal de la aplicación
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación
├── nacionalidades.txt          # Archivo de nacionalidades
│
├── models/                     # Modelos de datos
│   ├── __init__.py
│   ├── artista.py             # Clase Artista
│   ├── obra_arte.py           # Clase ObraArte
│   └── departamento.py        # Clase Departamento
│
├── services/                   # Servicios de negocio
│   ├── __init__.py
│   ├── cliente_api_met_museum.py    # Cliente API del museo
│   ├── servicio_busqueda.py         # Lógica de búsqueda
│   └── servicio_obras.py            # Gestión de obras
│
├── ui/                        # Interfaz de usuario
│   ├── __init__.py
│   ├── interfaz_usuario.py    # Interfaz de consola
│   └── visualizador_imagenes.py     # Visualización de imágenes
│
├── utils/                     # Utilidades
│   ├── __init__.py
│   └── gestor_nacionalidades.py    # Gestión de nacionalidades
│
└── tests/                     # Tests unitarios e integración
    ├── __init__.py
    ├── test_*.py             # Tests unitarios
    └── test_integracion_*.py # Tests de integración
```

## 🔍 Troubleshooting

### Problemas Comunes

#### Error: "Archivo de nacionalidades no encontrado"
```bash
# Verificar que el archivo existe
ls nacionalidades.txt

# Usar archivo personalizado
python main.py --nacionalidades ruta/a/mi/archivo.txt
```

#### Error: "No se puede conectar con la API"
```bash
# Verificar conexión a internet
ping google.com

# Verificar recursos del sistema
python main.py --check-resources
```

#### Error: "Dependencia no encontrada"
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# En Ubuntu/Debian para tkinter
sudo apt-get install python3-tk
```

#### Problemas con imágenes
- Verificar que Pillow está instalado: `pip show Pillow`
- En algunos sistemas puede requerir dependencias adicionales para tkinter

#### Error: "ModuleNotFoundError: No module named 'tkinter'"
```bash
# En Ubuntu/Debian
sudo apt-get install python3-tk

# En CentOS/RHEL/Fedora
sudo yum install tkinter
# o
sudo dnf install python3-tkinter

# En macOS con Homebrew
brew install python-tk
```

#### Error: "SSL Certificate verification failed"
```bash
# Actualizar certificados (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# En Linux, actualizar ca-certificates
sudo apt-get update && sudo apt-get install ca-certificates
```

#### Problemas de rendimiento lento
- El sistema incluye cache automático para mejorar rendimiento
- Las primeras búsquedas pueden ser más lentas
- Usar `python main.py --debug` para monitorear el cache

#### Error: "Request timeout"
- Verificar conexión a internet estable
- La API del museo puede estar temporalmente no disponible
- Reintentar después de unos minutos

#### Problemas con caracteres especiales
- Asegurar que la terminal soporte UTF-8
- En Windows, usar `chcp 65001` antes de ejecutar

### Modo Debug

Para obtener información detallada sobre el funcionamiento:
```bash
python main.py --debug
```

Esto creará un archivo `museo_catalogo_debug.log` con información detallada que incluye:
- Inicialización de componentes
- Consultas a la API del museo
- Operaciones de cache
- Errores detallados con stack traces
- Estadísticas de rendimiento

### Logs de Sistema

El sistema genera logs automáticamente cuando se ejecuta en modo debug:

- **Archivo de log**: `museo_catalogo_debug.log`
- **Formato**: Timestamp - Componente - Nivel - Mensaje
- **Niveles**: INFO, WARNING, ERROR, DEBUG
- **Rotación**: El archivo se sobrescribe en cada ejecución

#### Componentes con Logging Detallado

- **ClienteAPIMetMuseum**: Consultas a la API, timeouts, errores de conexión
- **ServicioBusqueda**: Operaciones de búsqueda, uso de cache, conversión de datos
- **ControladorPrincipal**: Flujo de aplicación, inicialización de componentes
- **GestorNacionalidades**: Carga de archivo, validación de nacionalidades
- **main.py**: Configuración del sistema, validación de recursos

#### Ejemplo de Log
```
2024-12-08 10:30:15,123 - services.cliente_api_met_museum - INFO - Obteniendo departamentos desde https://collectionapi.metmuseum.org/public/collection/v1/departments
2024-12-08 10:30:16,456 - services.cliente_api_met_museum - INFO - Obtenidos 21 departamentos exitosamente
2024-12-08 10:30:16,457 - services.servicio_busqueda - INFO - Iniciando búsqueda por departamento ID: 11
2024-12-08 10:30:16,458 - services.servicio_busqueda - INFO - Departamento 11 no encontrado en cache, consultando API
2024-12-08 10:30:18,789 - utils.gestor_nacionalidades - INFO - Nacionalidades cargadas exitosamente: 195 elementos
```

### Verificación de Integridad

Para verificar que todos los componentes funcionan correctamente:
```bash
# Verificar recursos del sistema
python main.py --check-resources

# Ejecutar tests básicos
python -m pytest tests/test_artista.py -v

# Verificar conectividad con la API
python -c "from services.cliente_api_met_museum import ClienteAPIMetMuseum; print('API OK' if ClienteAPIMetMuseum().obtener_departamentos() else 'API Error')"
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python -m pytest tests/

# Tests específicos
python -m pytest tests/test_artista.py

# Tests con cobertura
python -m pytest --cov=. tests/
```

### Tipos de Tests
- **Tests Unitarios**: Validan componentes individuales
- **Tests de Integración**: Verifican interacción entre componentes
- **Tests de API**: Validan comunicación con el Metropolitan Museum API

## 🏗️ Arquitectura

### Patrón de Diseño
La aplicación sigue el patrón **MVC (Model-View-Controller)** adaptado para consola:

- **Models**: Representan entidades del dominio (Artista, ObraArte, Departamento)
- **Views**: Interfaz de usuario por consola
- **Controllers**: Coordinan la lógica de negocio y flujo de la aplicación

### Principios de POO Aplicados
- **Encapsulación**: Propiedades privadas con métodos de acceso
- **Herencia**: Jerarquía de excepciones personalizadas
- **Polimorfismo**: Interfaces comunes para diferentes tipos de búsqueda
- **Abstracción**: Separación clara entre capas de la aplicación

## 📚 API del Metropolitan Museum

La aplicación utiliza la [API oficial del Metropolitan Museum](https://metmuseum.github.io/):

- **Base URL**: `https://collectionapi.metmuseum.org/public/collection/v1`
- **Endpoints utilizados**:
  - `/departments` - Lista de departamentos
  - `/search` - Búsqueda de obras
  - `/objects/{id}` - Detalles de obra específica

## 🤝 Contribución

### Desarrollo Local
1. Fork del repositorio
2. Crear rama para nueva funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Realizar cambios y tests
4. Commit: `git commit -m "Agregar nueva funcionalidad"`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Crear Pull Request

### Estándares de Código
- Seguir PEP 8 para estilo de código Python
- Documentar funciones y clases con docstrings
- Incluir tests para nueva funcionalidad
- Mantener cobertura de tests > 80%

## 📄 Licencia

Este proyecto es desarrollado con fines educativos y de demostración.

## 👥 Autores

- **Sistema de Catálogo del Museo** - Desarrollo inicial

## 🔗 Enlaces Útiles

- [API del Metropolitan Museum](https://metmuseum.github.io/)
- [Documentación de Python](https://docs.python.org/3/)
- [Guía de PEP 8](https://pep8.org/)
- [Documentación de Requests](https://docs.python-requests.org/)
- [Documentación de Pillow](https://pillow.readthedocs.io/)

---

**Versión**: 1.0.0  
**Última actualización**: 2024

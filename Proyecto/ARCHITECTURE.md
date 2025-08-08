# Arquitectura del Sistema de Catálogo del Museo

## Visión General

El Sistema de Catálogo del Museo Metropolitano de Arte está diseñado siguiendo principios de Programación Orientada a Objetos (POO) y arquitectura en capas. 

## Principios de Diseño

### 1. Separación de Responsabilidades
- **Modelos**: Representan las entidades del dominio
- **Servicios**: Contienen la lógica de negocio
- **Controladores**: Coordinan el flujo de la aplicación
- **Interfaz de Usuario**: Maneja la interacción con el usuario
- **Utilidades**: Proporcionan funcionalidades auxiliares

### 2. Inyección de Dependencias
- Los servicios reciben sus dependencias a través del constructor
- Facilita el testing mediante mocks
- Permite intercambiar implementaciones fácilmente

### 3. Manejo de Errores Centralizado
- Jerarquía de excepciones personalizadas
- Manejo consistente de errores en todas las capas
- Logging detallado para debugging

### 4. Cache y Optimización
- Sistema de cache integrado para mejorar rendimiento
- Almacenamiento temporal de consultas frecuentes
- Estrategias de invalidación de cache

## Arquitectura de Capas

```
┌─────────────────────────────────────────────────────────┐
│                    Capa de Presentación                 │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ InterfazUsuario │  │    VisualizadorImagenes        │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                   Capa de Control                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            ControladorPrincipal                     │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                  Capa de Servicios                      │
│  ┌─────────────────┐  ┌─────────────────────────────────┐ │
│  │ ServicioBusqueda│  │        ServicioObras           │ │
│  └─────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                 Capa de Acceso a Datos                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           ClienteAPIMetMuseum                       │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    API Externa                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │      Metropolitan Museum API                       │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Componentes Principales

### Modelos de Datos

#### Artista
```python
class Artista:
    - _nombre: str
    - _nacionalidad: str
    - _fecha_nacimiento: str
    - _fecha_muerte: str
    
    + propiedades de acceso (getters/setters)
    + validación de datos
    + representación string
```

#### ObraArte
```python
class ObraArte:
    - _id_obra: int
    - _titulo: str
    - _artista: Artista
    - _clasificacion: str
    - _fecha_creacion: str
    - _url_imagen: str
    - _departamento: str
    
    + mostrar_resumen()
    + mostrar_detalles_completos()
    + validación de datos
```

#### Departamento
```python
class Departamento:
    - _id_departamento: int
    - _nombre: str
    
    + propiedades de acceso
    + validación de ID
```

### Servicios de Negocio

#### ServicioBusqueda
- **Responsabilidad**: Coordinar búsquedas de obras
- **Dependencias**: ClienteAPIMetMuseum, GestorNacionalidades, AlmacenDatos
- **Métodos principales**:
  - `buscar_por_departamento()`
  - `buscar_por_nacionalidad()`
  - `buscar_por_nombre_artista()`
  - `obtener_departamentos_disponibles()`

#### ServicioObras
- **Responsabilidad**: Gestionar detalles de obras individuales
- **Dependencias**: ClienteAPIMetMuseum, VisualizadorImagenes, AlmacenDatos
- **Métodos principales**:
  - `obtener_detalles_obra()`
  - `mostrar_imagen_obra()`

### Cliente API

#### ClienteAPIMetMuseum
- **Responsabilidad**: Comunicación con la API del museo
- **Características**:
  - Manejo de timeouts y reintentos
  - Validación de respuestas
  - Rate limiting
  - Manejo de errores HTTP

### Utilidades

#### GestorNacionalidades
- **Responsabilidad**: Cargar y validar nacionalidades
- **Funcionalidades**:
  - Carga desde archivo de texto
  - Validación de nacionalidades disponibles
  - Cache de nacionalidades en memoria

#### AlmacenDatos
- **Responsabilidad**: Sistema de cache para optimización
- **Funcionalidades**:
  - Cache de IDs de obras por departamento
  - Cache de detalles de obras
  - Estrategias de invalidación

#### VisualizadorImagenes
- **Responsabilidad**: Mostrar imágenes de obras
- **Funcionalidades**:
  - Descarga temporal de imágenes
  - Apertura en ventana separada
  - Limpieza automática de archivos temporales

## Flujo de Datos

### Búsqueda por Departamento
```
Usuario → InterfazUsuario → ControladorPrincipal → ServicioBusqueda
    ↓
AlmacenDatos (cache) ← → ClienteAPIMetMuseum → API Met Museum
    ↓
Conversión a objetos ObraArte → Presentación al usuario
```

### Visualización de Detalles
```
Usuario (ID obra) → ControladorPrincipal → ServicioObras
    ↓
AlmacenDatos (cache) ← → ClienteAPIMetMuseum → API Met Museum
    ↓
Creación objeto ObraArte → InterfazUsuario → Usuario
    ↓ (opcional)
VisualizadorImagenes → Descarga imagen → Ventana separada
```

## Manejo de Errores

### Jerarquía de Excepciones

```
Exception
├── ExcepcionesAPIMetMuseum
│   ├── ErrorAPIMetMuseum (base)
│   ├── ErrorConexionAPI
│   ├── ErrorDatosIncompletos
│   ├── ErrorRecursoNoEncontrado
│   └── ErrorRateLimitAPI
├── ExcepcionesServicioBusqueda
│   ├── ErrorServicioBusqueda (base)
│   ├── ErrorDepartamentoInvalido
│   └── ErrorNacionalidadInvalida
└── ErrorArchivoNacionalidades
```

### Estrategia de Manejo
1. **Captura específica**: Cada capa maneja sus errores específicos
2. **Propagación controlada**: Los errores se propagan con contexto adicional
3. **Logging detallado**: Todos los errores se registran con información de contexto
4. **Mensajes amigables**: Los errores se traducen a mensajes comprensibles para el usuario

## Sistema de Logging

### Configuración
- **Nivel**: DEBUG en modo debug, INFO en producción
- **Formato**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Salidas**: Consola y archivo `museo_catalogo_debug.log`

### Componentes con Logging
- `ClienteAPIMetMuseum`: Consultas a API, errores de conexión
- `ServicioBusqueda`: Operaciones de búsqueda, uso de cache
- `ControladorPrincipal`: Flujo de aplicación, inicialización
- `main.py`: Configuración, validación de recursos

## Optimizaciones de Rendimiento

### Sistema de Cache
- **Cache de IDs por departamento**: Evita consultas repetidas a la API
- **Cache de detalles de obras**: Almacena obras consultadas frecuentemente
- **Invalidación inteligente**: Cache se invalida después de tiempo configurable

### Estrategias de Red
- **Timeouts configurables**: Evita bloqueos indefinidos
- **Reintentos automáticos**: Manejo de fallos temporales de red
- **Rate limiting**: Respeta límites de la API del museo

## Testing

### Estrategia de Testing
- **Tests unitarios**: Cada clase y método individual
- **Tests de integración**: Interacción entre componentes
- **Tests end-to-end**: Flujos completos de usuario
- **Mocking**: Simulación de API externa para tests confiables

### Cobertura
- **Modelos**: 100% cobertura de métodos públicos
- **Servicios**: Cobertura de casos normales y de error
- **Controlador**: Tests de flujos principales
- **Utilidades**: Validación de funcionalidades auxiliares

## Extensibilidad

### Puntos de Extensión
1. **Nuevos tipos de búsqueda**: Agregar métodos a `ServicioBusqueda`
2. **Diferentes fuentes de datos**: Implementar nuevos clientes API
3. **Formatos de salida**: Extender `InterfazUsuario` para otros formatos
4. **Sistemas de cache**: Implementar diferentes estrategias de almacenamiento

### Principios para Extensión
- **Interfaces claras**: Definir contratos bien documentados
- **Inyección de dependencias**: Facilitar intercambio de implementaciones
- **Configuración externa**: Permitir personalización sin cambios de código
- **Backward compatibility**: Mantener compatibilidad con versiones anteriores

## Consideraciones de Seguridad

### Validación de Entrada
- Validación de IDs de obra (enteros positivos)
- Sanitización de nombres de artistas
- Validación de rutas de archivos

### Manejo de Datos Sensibles
- No almacenamiento de credenciales
- Uso de HTTPS para comunicaciones
- Limpieza de archivos temporales

### Rate Limiting
- Respeto a límites de la API externa
- Implementación de delays entre consultas
- Manejo graceful de errores de límite

## Deployment y Configuración

### Requisitos del Sistema
- Python 3.7+
- Conexión a internet estable
- Dependencias especificadas en `requirements.txt`

### Configuración
- Archivo de nacionalidades configurable
- Timeouts y reintentos configurables
- Niveles de logging ajustables

### Monitoreo
- Logs detallados para debugging
- Métricas de rendimiento en modo debug
- Validación automática de recursos del sistema
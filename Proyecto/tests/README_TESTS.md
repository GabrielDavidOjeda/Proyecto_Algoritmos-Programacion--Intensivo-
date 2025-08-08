# Documentación de Tests del Sistema de Catálogo del Museo

## Estructura de Tests

El proyecto incluye una suite completa de tests organizados en tres niveles:

### 1. Tests Unitarios
- **Ubicación**: `test_*.py` (excluyendo `test_integracion_*` y `test_end_to_end.py`)
- **Propósito**: Validar componentes individuales de forma aislada
- **Características**: Rápidos, sin dependencias externas, usan mocks extensivamente

**Archivos incluidos**:
- `test_artista.py` - Tests del modelo Artista
- `test_obra_arte.py` - Tests del modelo ObraArte  
- `test_departamento.py` - Tests del modelo Departamento
- `test_cliente_api_met_museum.py` - Tests del cliente API (con mocks)
- `test_servicio_busqueda.py` - Tests del servicio de búsqueda (con mocks)
- `test_servicio_obras.py` - Tests del servicio de obras (con mocks)
- `test_gestor_nacionalidades.py` - Tests del gestor de nacionalidades
- `test_visualizador_imagenes.py` - Tests del visualizador de imágenes
- `test_interfaz_usuario.py` - Tests de la interfaz de usuario
- `test_controlador_principal.py` - Tests del controlador principal (con mocks)

### 2. Tests de Integración
- **Ubicación**: `test_integracion_*.py`
- **Propósito**: Validar interacción entre componentes reales
- **Características**: Pueden usar APIs reales, archivos reales, más lentos

**Archivos incluidos**:
- `test_integracion_api_met_museum.py` - Integración con API real del museo
- `test_integracion_servicio_busqueda.py` - Servicios con API real
- `test_integracion_servicio_obras.py` - Servicio de obras con API real
- `test_integracion_controlador_principal.py` - Controlador con componentes reales
- `test_integracion_visualizador_imagenes.py` - Visualización con imágenes reales
- `test_integracion_visualizacion_imagenes.py` - Tests de visualización completa

### 3. Tests End-to-End
- **Ubicación**: `test_end_to_end.py`
- **Propósito**: Validar flujos completos de usuario desde entrada hasta salida
- **Características**: Simulan interacción completa del usuario, validan casos edge

**Clases de test incluidas**:
- `TestEndToEndBusquedaDepartamento` - Flujos completos de búsqueda por departamento
- `TestEndToEndBusquedaNacionalidad` - Flujos completos de búsqueda por nacionalidad
- `TestEndToEndBusquedaArtista` - Flujos completos de búsqueda por artista
- `TestEndToEndVisualizacionDetalles` - Flujos completos de visualización de detalles
- `TestEndToEndManejoErroresAPI` - Manejo de errores de API y conectividad
- `TestEndToEndSuiteRegresion` - Suite de tests de regresión

## Ejecución de Tests

### Comandos Básicos

```bash
# Ejecutar todos los tests (unitarios + integración)
python run_tests.py

# Ejecutar todos los tests incluyendo end-to-end
python run_tests.py --include-e2e

# Ejecutar solo tests unitarios
python run_tests.py --unit-only

# Ejecutar solo tests de integración
python run_tests.py --integration-only

# Ejecutar solo tests end-to-end
python run_tests.py --e2e-only

# Ejecución silenciosa
python run_tests.py --quiet
```

### Tests End-to-End Específicos

```bash
# Ejecutar todos los tests end-to-end
python tests/run_end_to_end_tests.py

# Ejecutar solo tests de búsqueda por departamento
python tests/run_end_to_end_tests.py --category busqueda_departamento

# Ejecutar solo tests de búsqueda por nacionalidad
python tests/run_end_to_end_tests.py --category busqueda_nacionalidad

# Ejecutar solo tests de búsqueda por artista
python tests/run_end_to_end_tests.py --category busqueda_artista

# Ejecutar solo tests de visualización de detalles
python tests/run_end_to_end_tests.py --category visualizacion_detalles

# Ejecutar solo tests de manejo de errores API
python tests/run_end_to_end_tests.py --category manejo_errores_api

# Ejecutar solo suite de regresión
python tests/run_end_to_end_tests.py --category suite_regresion
# o
python tests/run_end_to_end_tests.py --regression-only
```

### Tests con Pytest (para tests marcados como 'slow')

```bash
# Ejecutar tests de integración con API real (marcados como @pytest.mark.slow)
pytest tests/test_integracion_api_met_museum.py -v -m slow

# Ejecutar tests de integración de servicios
pytest tests/test_integracion_servicio_busqueda.py -v -m slow
```

## Cobertura de Tests End-to-End

### Flujos de Búsqueda por Departamento
- ✅ Flujo exitoso completo con visualización de imagen
- ✅ Departamento sin obras disponibles
- ✅ Error de departamento inválido
- ✅ Manejo de errores de API durante búsqueda

### Flujos de Búsqueda por Nacionalidad
- ✅ Búsqueda exitosa con archivo real de nacionalidades
- ✅ Error cuando nacionalidad no existe en archivo
- ✅ Manejo de archivo de nacionalidades corrupto
- ✅ Validación de nacionalidades disponibles

### Flujos de Búsqueda por Artista
- ✅ Búsqueda por nombre parcial de artista
- ✅ Búsqueda con caracteres especiales
- ✅ Búsqueda con nombre vacío o solo espacios
- ✅ Casos edge de entrada de usuario

### Visualización de Detalles
- ✅ Visualización completa con imagen disponible
- ✅ Visualización sin imagen disponible
- ✅ Error cuando obra no existe
- ✅ Manejo de datos incompletos

### Manejo de Errores de API
- ✅ Error de conexión con API
- ✅ Error de límite de consultas (rate limit)
- ✅ Datos corruptos de la API
- ✅ Recursos no encontrados

### Suite de Regresión
- ✅ Inicialización completa del sistema
- ✅ Todos los tipos de búsqueda funcionan
- ✅ Manejo consistente de errores
- ✅ Integridad del archivo de nacionalidades

## Casos Edge Cubiertos

### Entrada de Usuario
- Nombres de artista con caracteres especiales
- Búsquedas con texto vacío o solo espacios
- Selecciones fuera de rango
- IDs de obra inválidos

### Datos de API
- Obras sin imagen disponible
- Datos incompletos o corruptos
- Respuestas vacías de la API
- Errores de conectividad

### Archivos del Sistema
- Archivo de nacionalidades vacío
- Archivo de nacionalidades corrupto
- Archivo de nacionalidades inexistente
- Nacionalidades duplicadas

### Errores de Red
- Timeout de conexión
- Errores HTTP (404, 500, etc.)
- Rate limiting de API
- Respuestas malformadas

## Métricas de Tests

### Tiempo de Ejecución Estimado
- **Tests Unitarios**: ~10-15 segundos
- **Tests de Integración**: ~30-60 segundos (depende de conectividad)
- **Tests End-to-End**: ~45-90 segundos
- **Suite Completa**: ~2-3 minutos

### Cobertura Funcional
- **Modelos de Datos**: 100% de métodos públicos
- **Servicios de Negocio**: 95% de flujos principales
- **Cliente API**: 90% de endpoints y errores
- **Controlador Principal**: 95% de flujos de usuario
- **Interfaz de Usuario**: 85% de métodos de presentación
- **Manejo de Errores**: 90% de tipos de error

## Configuración de Entorno para Tests

### Archivos de Test Requeridos
Los tests end-to-end crean automáticamente archivos temporales:
- `test_nacionalidades_e2e.txt` - Archivo temporal de nacionalidades
- `test_nacionalidades_corrupto.txt` - Para tests de error

### Variables de Entorno
No se requieren variables de entorno especiales. Los tests usan:
- API pública del Metropolitan Museum (sin autenticación)
- Archivos locales temporales
- Mocks para componentes externos

### Dependencias Adicionales
Para ejecutar todos los tests se requiere:
- `unittest` (incluido en Python estándar)
- `pytest` (para tests marcados como 'slow')
- `requests` (para cliente API)
- `PIL/Pillow` (para visualización de imágenes)
- `tkinter` (incluido en Python estándar)

## Interpretación de Resultados

### Códigos de Salida
- `0`: Todos los tests pasaron exitosamente
- `1`: Algunos tests fallaron o hubo errores

### Tipos de Fallos
- **FAIL**: Assertion falló, comportamiento inesperado
- **ERROR**: Excepción no manejada durante el test
- **SKIP**: Test omitido (ej. por falta de conectividad)

### Reportes Detallados
El runner de tests end-to-end proporciona:
- Tiempo de ejecución por test
- Tests más lentos
- Resumen de errores y fallos
- Métricas de rendimiento

## Mantenimiento de Tests

### Actualización de Tests
- Revisar tests cuando se modifiquen APIs
- Actualizar mocks cuando cambien interfaces
- Agregar tests para nuevas funcionalidades
- Mantener datos de test actualizados

### Debugging de Tests
- Usar `--verbosity 2` para output detallado
- Ejecutar tests individuales para debugging
- Revisar logs de API para tests de integración
- Verificar archivos temporales en caso de fallos

### Mejores Prácticas
- Mantener tests independientes entre sí
- Limpiar recursos después de cada test
- Usar mocks apropiados para dependencias externas
- Documentar casos edge específicos
- Mantener tiempos de ejecución razonables
"""
Tests de integración para el sistema de cache con los servicios.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from services.servicio_busqueda import ServicioBusqueda
from services.servicio_obras import ServicioObras
from services.cliente_api_met_museum import ClienteAPIMetMuseum
from utils.gestor_nacionalidades import GestorNacionalidades
from utils.almacen_datos import AlmacenDatos
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestIntegracionCacheServicioBusqueda(unittest.TestCase):
    """Tests de integración del cache con ServicioBusqueda"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.almacen_datos = AlmacenDatos()
        
        self.servicio = ServicioBusqueda(
            self.mock_cliente_api,
            self.mock_gestor_nacionalidades,
            self.almacen_datos
        )
        
        # Datos de prueba
        self.artista_test = Artista("Van Gogh", "Dutch", "1853", "1890")
        self.obra_test = ObraArte(123, "Starry Night", self.artista_test, "Paintings")
        self.departamentos_test = [
            Departamento(1, "European Paintings"),
            Departamento(2, "American Art")
        ]
    
    def test_busqueda_departamento_con_cache_miss_y_hit(self):
        """Test de búsqueda por departamento con miss y hit de cache"""
        # Configurar mocks
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = [123]
        self.mock_cliente_api.obtener_detalles_obra.return_value = {
            'objectID': 123,
            'title': 'Starry Night',
            'artistDisplayName': 'Van Gogh',
            'artistNationality': 'Dutch',
            'artistBeginDate': '1853',
            'artistEndDate': '1890',
            'classification': 'Paintings'
        }
        
        # Primera búsqueda (cache miss)
        obras1 = self.servicio.buscar_por_departamento(1)
        
        # Verificar que se llamó a la API
        self.mock_cliente_api.obtener_obras_por_departamento.assert_called_once_with(1)
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(123)
        
        # Verificar resultado
        self.assertEqual(len(obras1), 1)
        self.assertEqual(obras1[0].id_obra, 123)
        
        # Reset mocks para segunda llamada
        self.mock_cliente_api.reset_mock()
        
        # Segunda búsqueda (cache hit)
        obras2 = self.servicio.buscar_por_departamento(1)
        
        # Verificar que NO se llamó a la API para obtener detalles (cache hit)
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
        # Pero sí para obtener IDs (cache hit también)
        self.mock_cliente_api.obtener_obras_por_departamento.assert_not_called()
        
        # Verificar que el resultado es el mismo
        self.assertEqual(len(obras2), 1)
        self.assertEqual(obras2[0].id_obra, 123)
    
    def test_obtener_departamentos_con_cache(self):
        """Test de obtención de departamentos con cache"""
        # Configurar mock
        self.mock_cliente_api.obtener_departamentos.return_value = self.departamentos_test
        
        # Primera llamada (cache miss)
        departamentos1 = self.servicio.obtener_departamentos_disponibles()
        
        # Verificar que se llamó a la API
        self.mock_cliente_api.obtener_departamentos.assert_called_once()
        self.assertEqual(len(departamentos1), 2)
        
        # Reset mock
        self.mock_cliente_api.reset_mock()
        
        # Segunda llamada (cache hit)
        departamentos2 = self.servicio.obtener_departamentos_disponibles()
        
        # Verificar que NO se llamó a la API
        self.mock_cliente_api.obtener_departamentos.assert_not_called()
        
        # Verificar que el resultado es el mismo
        self.assertEqual(len(departamentos2), 2)
        self.assertEqual(departamentos1[0].nombre, departamentos2[0].nombre)
    
    def test_busqueda_nacionalidad_con_cache(self):
        """Test de búsqueda por nacionalidad con cache"""
        # Configurar mocks
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = [123]
        self.mock_cliente_api.obtener_detalles_obra.return_value = {
            'objectID': 123,
            'title': 'Starry Night',
            'artistDisplayName': 'Van Gogh',
            'artistNationality': 'Dutch',
            'artistBeginDate': '1853',
            'artistEndDate': '1890'
        }
        
        # Primera búsqueda (cache miss)
        obras1 = self.servicio.buscar_por_nacionalidad("Dutch")
        
        # Verificar llamadas a la API
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Dutch")
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(123)
        
        # Reset mocks
        self.mock_cliente_api.reset_mock()
        
        # Segunda búsqueda (cache hit)
        obras2 = self.servicio.buscar_por_nacionalidad("Dutch")
        
        # Verificar que NO se llamó a la API
        self.mock_cliente_api.buscar_obras_por_query.assert_not_called()
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
        
        # Verificar resultados
        self.assertEqual(len(obras1), 1)
        self.assertEqual(len(obras2), 1)
    
    def test_busqueda_artista_con_cache(self):
        """Test de búsqueda por artista con cache"""
        # Configurar mock
        self.mock_cliente_api.buscar_obras_por_query.return_value = [123]
        self.mock_cliente_api.obtener_detalles_obra.return_value = {
            'objectID': 123,
            'title': 'Starry Night',
            'artistDisplayName': 'Van Gogh',
            'artistNationality': 'Dutch'
        }
        
        # Primera búsqueda (cache miss)
        obras1 = self.servicio.buscar_por_nombre_artista("Van Gogh")
        
        # Verificar llamadas
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once()
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(123)
        
        # Reset mocks
        self.mock_cliente_api.reset_mock()
        
        # Segunda búsqueda (cache hit)
        obras2 = self.servicio.buscar_por_nombre_artista("Van Gogh")
        
        # Verificar que NO se llamó a la API
        self.mock_cliente_api.buscar_obras_por_query.assert_not_called()
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
        
        # Verificar resultados
        self.assertEqual(len(obras1), 1)
        self.assertEqual(len(obras2), 1)


class TestIntegracionCacheServicioObras(unittest.TestCase):
    """Tests de integración del cache con ServicioObras"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_visualizador = Mock()
        self.almacen_datos = AlmacenDatos()
        
        self.servicio = ServicioObras(
            self.mock_cliente_api,
            self.mock_visualizador,
            self.almacen_datos
        )
    
    def test_obtener_detalles_obra_con_cache(self):
        """Test de obtención de detalles con cache"""
        # Configurar mock
        datos_api = {
            'objectID': 123,
            'title': 'Starry Night',
            'artistDisplayName': 'Van Gogh',
            'artistNationality': 'Dutch',
            'artistBeginDate': '1853',
            'artistEndDate': '1890',
            'classification': 'Paintings'
        }
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_api
        
        # Primera llamada (cache miss)
        obra1 = self.servicio.obtener_detalles_obra(123)
        
        # Verificar que se llamó a la API
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(123)
        self.assertEqual(obra1.id_obra, 123)
        self.assertEqual(obra1.titulo, 'Starry Night')
        
        # Reset mock
        self.mock_cliente_api.reset_mock()
        
        # Segunda llamada (cache hit)
        obra2 = self.servicio.obtener_detalles_obra(123)
        
        # Verificar que NO se llamó a la API
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
        
        # Verificar que el resultado es el mismo
        self.assertEqual(obra2.id_obra, 123)
        self.assertEqual(obra2.titulo, 'Starry Night')
        self.assertEqual(obra1.artista.nombre, obra2.artista.nombre)


class TestIntegracionCacheCompleta(unittest.TestCase):
    """Tests de integración completa del sistema de cache"""
    
    def setUp(self):
        """Configuración inicial para tests de integración completa"""
        self.almacen_datos = AlmacenDatos()
        
        # Crear mocks
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.mock_visualizador = Mock()
        
        # Crear servicios con cache compartido
        self.servicio_busqueda = ServicioBusqueda(
            self.mock_cliente_api,
            self.mock_gestor_nacionalidades,
            self.almacen_datos
        )
        
        self.servicio_obras = ServicioObras(
            self.mock_cliente_api,
            self.mock_visualizador,
            self.almacen_datos
        )
    
    def test_cache_compartido_entre_servicios(self):
        """Test de cache compartido entre servicios"""
        # Configurar mocks
        datos_api = {
            'objectID': 123,
            'title': 'Starry Night',
            'artistDisplayName': 'Van Gogh',
            'artistNationality': 'Dutch',
            'classification': 'Paintings'
        }
        
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = [123]
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_api
        
        # Buscar por departamento (llena el cache de obras)
        obras = self.servicio_busqueda.buscar_por_departamento(1)
        self.assertEqual(len(obras), 1)
        
        # Verificar que se llamó a la API
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(123)
        
        # Reset mock
        self.mock_cliente_api.reset_mock()
        
        # Obtener detalles de la misma obra usando el otro servicio
        # Debería usar el cache compartido
        obra_detalles = self.servicio_obras.obtener_detalles_obra(123)
        
        # Verificar que NO se llamó a la API (cache hit)
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
        
        # Verificar que los datos son consistentes
        self.assertEqual(obra_detalles.id_obra, 123)
        self.assertEqual(obra_detalles.titulo, 'Starry Night')
    
    def test_estadisticas_cache_integradas(self):
        """Test de estadísticas de cache con múltiples servicios"""
        # Configurar mocks
        self.mock_cliente_api.obtener_departamentos.return_value = [
            Departamento(1, "European Paintings")
        ]
        
        datos_obra = {
            'objectID': 123,
            'title': 'Test Obra',
            'artistDisplayName': 'Test Artist'
        }
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_obra
        
        # Realizar operaciones que generen hits y misses
        
        # 1. Obtener departamentos (miss)
        self.servicio_busqueda.obtener_departamentos_disponibles()
        
        # 2. Obtener departamentos otra vez (hit)
        self.servicio_busqueda.obtener_departamentos_disponibles()
        
        # 3. Obtener obra (miss)
        self.servicio_obras.obtener_detalles_obra(123)
        
        # 4. Obtener obra otra vez (hit)
        self.servicio_obras.obtener_detalles_obra(123)
        
        # 5. Intentar obtener obra inexistente (miss)
        try:
            self.almacen_datos.obtener_obra(999)
        except:
            pass
        
        # Verificar estadísticas
        estadisticas = self.almacen_datos.obtener_estadisticas_cache()
        
        self.assertEqual(estadisticas['hits_departamentos'], 1)
        self.assertEqual(estadisticas['misses_departamentos'], 1)
        self.assertEqual(estadisticas['hits_obras'], 1)
        self.assertGreaterEqual(estadisticas['misses_obras'], 1)
        
        # Verificar ratios
        self.assertEqual(estadisticas['hit_ratio_departamentos'], 0.5)
        self.assertLessEqual(estadisticas['hit_ratio_obras'], 0.5)
    
    def test_limpieza_cache_con_servicios_activos(self):
        """Test de limpieza de cache con servicios activos"""
        # Llenar cache con datos
        self.mock_cliente_api.obtener_departamentos.return_value = [
            Departamento(1, "Test Department")
        ]
        
        datos_obra = {
            'objectID': 123,
            'title': 'Test Obra',
            'artistDisplayName': 'Test Artist'
        }
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_obra
        
        # Llenar cache
        self.servicio_busqueda.obtener_departamentos_disponibles()
        self.servicio_obras.obtener_detalles_obra(123)
        
        # Verificar que el cache tiene datos
        estadisticas_antes = self.almacen_datos.obtener_estadisticas_cache()
        self.assertGreater(estadisticas_antes['obras_en_cache'], 0)
        self.assertGreater(estadisticas_antes['departamentos_en_cache'], 0)
        
        # Limpiar cache
        self.almacen_datos.invalidar_todo_cache()
        
        # Verificar que el cache está vacío
        estadisticas_despues = self.almacen_datos.obtener_estadisticas_cache()
        self.assertEqual(estadisticas_despues['obras_en_cache'], 0)
        self.assertEqual(estadisticas_despues['departamentos_en_cache'], 0)
        
        # Verificar que los servicios siguen funcionando (van a la API)
        self.mock_cliente_api.reset_mock()
        
        departamentos = self.servicio_busqueda.obtener_departamentos_disponibles()
        obra = self.servicio_obras.obtener_detalles_obra(123)
        
        # Verificar que se llamó a la API nuevamente
        self.mock_cliente_api.obtener_departamentos.assert_called_once()
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once()


class TestRendimientoIntegracionCache(unittest.TestCase):
    """Tests de rendimiento para la integración del cache"""
    
    def setUp(self):
        """Configuración para tests de rendimiento"""
        self.almacen_datos = AlmacenDatos()
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        
        self.servicio_busqueda = ServicioBusqueda(
            self.mock_cliente_api,
            self.mock_gestor_nacionalidades,
            self.almacen_datos
        )
    
    def test_rendimiento_busquedas_repetidas(self):
        """Test de rendimiento con búsquedas repetidas"""
        import time
        
        # Configurar mock para simular respuesta lenta de API
        def mock_api_lenta(*args, **kwargs):
            time.sleep(0.01)  # Simular 10ms de latencia
            return [123, 456, 789]
        
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = mock_api_lenta
        
        # Configurar mock para detalles de obra
        def mock_detalles_obra(id_obra):
            time.sleep(0.005)  # Simular 5ms de latencia
            return {
                'objectID': id_obra,
                'title': f'Obra {id_obra}',
                'artistDisplayName': 'Test Artist'
            }
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = mock_detalles_obra
        
        # Primera búsqueda (sin cache)
        inicio = time.time()
        obras1 = self.servicio_busqueda.buscar_por_departamento(1)
        tiempo_sin_cache = time.time() - inicio
        
        # Segunda búsqueda (con cache)
        inicio = time.time()
        obras2 = self.servicio_busqueda.buscar_por_departamento(1)
        tiempo_con_cache = time.time() - inicio
        
        # Verificar que el cache mejora significativamente el rendimiento
        self.assertLess(tiempo_con_cache, tiempo_sin_cache * 0.1)  # Al menos 10x más rápido
        
        # Verificar que los resultados son iguales
        self.assertEqual(len(obras1), len(obras2))
        self.assertEqual(obras1[0].id_obra, obras2[0].id_obra)
    
    def test_memoria_cache_bajo_carga(self):
        """Test de uso de memoria del cache bajo carga"""
        # Configurar mock para generar muchas obras
        def mock_muchas_obras(*args, **kwargs):
            return list(range(1, 101))  # 100 obras
        
        def mock_detalles_obra(id_obra):
            return {
                'objectID': id_obra,
                'title': f'Obra {id_obra}',
                'artistDisplayName': f'Artist {id_obra}',
                'classification': 'Paintings'
            }
        
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = mock_muchas_obras
        self.mock_cliente_api.obtener_detalles_obra.side_effect = mock_detalles_obra
        
        # Realizar búsqueda que llene el cache
        obras = self.servicio_busqueda.buscar_por_departamento(1)
        
        # Verificar estadísticas de memoria
        estadisticas = self.almacen_datos.obtener_estadisticas_cache()
        
        # Verificar que el uso de memoria es razonable (menos de 1MB)
        self.assertLess(estadisticas['memoria_estimada_kb'], 1024)
        
        # Verificar que se almacenaron las obras esperadas
        self.assertGreater(estadisticas['obras_en_cache'], 0)
        self.assertLessEqual(estadisticas['obras_en_cache'], 20)  # Limitado por el servicio


if __name__ == '__main__':
    unittest.main()
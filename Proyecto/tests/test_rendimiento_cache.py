"""
Tests de rendimiento específicos para el sistema de cache.
Mide la efectividad del cache en escenarios reales de uso.
"""

import unittest
import time
import statistics
from unittest.mock import Mock, patch
from services.servicio_busqueda import ServicioBusqueda
from services.servicio_obras import ServicioObras
from services.cliente_api_met_museum import ClienteAPIMetMuseum
from utils.gestor_nacionalidades import GestorNacionalidades
from utils.almacen_datos import AlmacenDatos
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestRendimientoCache(unittest.TestCase):
    """Tests de rendimiento para el sistema de cache"""
    
    def setUp(self):
        """Configuración inicial para tests de rendimiento"""
        self.almacen_datos = AlmacenDatos()
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.mock_visualizador = Mock()
        
        # Crear servicios
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
        
        # Configurar mocks con latencia simulada
        self._configurar_mocks_con_latencia()
    
    def _configurar_mocks_con_latencia(self):
        """Configura mocks que simulan latencia de red"""
        
        def mock_obtener_departamentos():
            time.sleep(0.1)  # Simular 100ms de latencia
            return [
                Departamento(1, "European Paintings"),
                Departamento(2, "American Art"),
                Departamento(3, "Asian Art")
            ]
        
        def mock_obtener_obras_departamento(id_dept):
            time.sleep(0.05)  # Simular 50ms de latencia
            return list(range(1, 21))  # 20 obras por departamento
        
        def mock_obtener_detalles_obra(id_obra):
            time.sleep(0.02)  # Simular 20ms de latencia
            return {
                'objectID': id_obra,
                'title': f'Obra {id_obra}',
                'artistDisplayName': f'Artist {id_obra}',
                'artistNationality': 'Test Nationality',
                'classification': 'Paintings',
                'objectDate': '2000'
            }
        
        def mock_buscar_obras_query(query):
            time.sleep(0.08)  # Simular 80ms de latencia
            return list(range(1, 16))  # 15 obras por búsqueda
        
        self.mock_cliente_api.obtener_departamentos.side_effect = mock_obtener_departamentos
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = mock_obtener_obras_departamento
        self.mock_cliente_api.obtener_detalles_obra.side_effect = mock_obtener_detalles_obra
        self.mock_cliente_api.buscar_obras_por_query.side_effect = mock_buscar_obras_query
        
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
    
    def test_rendimiento_busqueda_departamento_sin_cache(self):
        """Test de rendimiento de búsqueda por departamento sin cache"""
        # Medir tiempo sin cache
        tiempos = []
        
        for _ in range(5):
            # Limpiar cache antes de cada medición
            self.almacen_datos.invalidar_todo_cache()
            
            inicio = time.time()
            obras = self.servicio_busqueda.buscar_por_departamento(1)
            tiempo = time.time() - inicio
            tiempos.append(tiempo)
        
        tiempo_promedio_sin_cache = statistics.mean(tiempos)
        
        # Verificar que se obtuvieron obras
        self.assertGreater(len(obras), 0)
        
        # El tiempo sin cache debería ser significativo (>100ms debido a latencia simulada)
        self.assertGreater(tiempo_promedio_sin_cache, 0.1)
        
        print(f"Tiempo promedio sin cache: {tiempo_promedio_sin_cache:.3f}s")
        return tiempo_promedio_sin_cache
    
    def test_rendimiento_busqueda_departamento_con_cache(self):
        """Test de rendimiento de búsqueda por departamento con cache"""
        # Primera búsqueda para llenar el cache
        self.servicio_busqueda.buscar_por_departamento(1)
        
        # Medir tiempo con cache
        tiempos = []
        
        for _ in range(5):
            inicio = time.time()
            obras = self.servicio_busqueda.buscar_por_departamento(1)
            tiempo = time.time() - inicio
            tiempos.append(tiempo)
        
        tiempo_promedio_con_cache = statistics.mean(tiempos)
        
        # Verificar que se obtuvieron obras
        self.assertGreater(len(obras), 0)
        
        # El tiempo con cache debería ser muy rápido (<10ms)
        self.assertLess(tiempo_promedio_con_cache, 0.01)
        
        print(f"Tiempo promedio con cache: {tiempo_promedio_con_cache:.3f}s")
        return tiempo_promedio_con_cache
    
    def test_mejora_rendimiento_cache(self):
        """Test que compara la mejora de rendimiento con cache"""
        # Obtener tiempos sin y con cache
        tiempo_sin_cache = self.test_rendimiento_busqueda_departamento_sin_cache()
        tiempo_con_cache = self.test_rendimiento_busqueda_departamento_con_cache()
        
        # Calcular mejora
        mejora = tiempo_sin_cache / tiempo_con_cache
        
        print(f"Mejora de rendimiento: {mejora:.1f}x más rápido")
        
        # El cache debería ser al menos 10x más rápido
        self.assertGreater(mejora, 10)
    
    def test_rendimiento_obtener_departamentos(self):
        """Test de rendimiento para obtención de departamentos"""
        # Primera llamada (sin cache)
        inicio = time.time()
        departamentos1 = self.servicio_busqueda.obtener_departamentos_disponibles()
        tiempo_sin_cache = time.time() - inicio
        
        # Segunda llamada (con cache)
        inicio = time.time()
        departamentos2 = self.servicio_busqueda.obtener_departamentos_disponibles()
        tiempo_con_cache = time.time() - inicio
        
        # Verificar resultados
        self.assertEqual(len(departamentos1), len(departamentos2))
        self.assertGreater(tiempo_sin_cache, 0.05)  # Al menos 50ms sin cache
        self.assertLess(tiempo_con_cache, 0.01)     # Menos de 10ms con cache
        
        mejora = tiempo_sin_cache / tiempo_con_cache
        print(f"Mejora departamentos: {mejora:.1f}x más rápido")
        
        self.assertGreater(mejora, 5)
    
    def test_rendimiento_busqueda_nacionalidad(self):
        """Test de rendimiento para búsqueda por nacionalidad"""
        nacionalidad = "Test Nationality"
        
        # Primera búsqueda (sin cache)
        inicio = time.time()
        obras1 = self.servicio_busqueda.buscar_por_nacionalidad(nacionalidad)
        tiempo_sin_cache = time.time() - inicio
        
        # Segunda búsqueda (con cache)
        inicio = time.time()
        obras2 = self.servicio_busqueda.buscar_por_nacionalidad(nacionalidad)
        tiempo_con_cache = time.time() - inicio
        
        # Verificar resultados
        self.assertEqual(len(obras1), len(obras2))
        self.assertGreater(tiempo_sin_cache, 0.08)  # Al menos 80ms sin cache
        self.assertLess(tiempo_con_cache, 0.01)     # Menos de 10ms con cache
        
        mejora = tiempo_sin_cache / tiempo_con_cache
        print(f"Mejora nacionalidad: {mejora:.1f}x más rápido")
        
        self.assertGreater(mejora, 8)
    
    def test_rendimiento_obtener_detalles_obra(self):
        """Test de rendimiento para obtención de detalles de obra"""
        id_obra = 123
        
        # Primera llamada (sin cache)
        inicio = time.time()
        obra1 = self.servicio_obras.obtener_detalles_obra(id_obra)
        tiempo_sin_cache = time.time() - inicio
        
        # Segunda llamada (con cache)
        inicio = time.time()
        obra2 = self.servicio_obras.obtener_detalles_obra(id_obra)
        tiempo_con_cache = time.time() - inicio
        
        # Verificar resultados
        self.assertEqual(obra1.id_obra, obra2.id_obra)
        self.assertGreater(tiempo_sin_cache, 0.015)  # Al menos 15ms sin cache
        self.assertLess(tiempo_con_cache, 0.005)     # Menos de 5ms con cache
        
        mejora = tiempo_sin_cache / tiempo_con_cache
        print(f"Mejora detalles obra: {mejora:.1f}x más rápido")
        
        self.assertGreater(mejora, 3)
    
    def test_rendimiento_cache_bajo_carga(self):
        """Test de rendimiento del cache bajo carga intensa"""
        # Configurar mock para muchas obras
        def mock_muchas_obras(id_dept):
            time.sleep(0.1)  # Latencia base
            return list(range(1, 101))  # 100 obras
        
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = mock_muchas_obras
        
        # Realizar múltiples búsquedas simultáneas
        import threading
        
        tiempos_primera_busqueda = []
        tiempos_cache_hits = []
        
        def busqueda_inicial():
            inicio = time.time()
            self.servicio_busqueda.buscar_por_departamento(1)
            tiempo = time.time() - inicio
            tiempos_primera_busqueda.append(tiempo)
        
        def busqueda_con_cache():
            inicio = time.time()
            self.servicio_busqueda.buscar_por_departamento(1)
            tiempo = time.time() - inicio
            tiempos_cache_hits.append(tiempo)
        
        # Primera búsqueda para llenar cache
        thread_inicial = threading.Thread(target=busqueda_inicial)
        thread_inicial.start()
        thread_inicial.join()
        
        # Múltiples búsquedas con cache
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=busqueda_con_cache)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Analizar resultados
        tiempo_inicial = statistics.mean(tiempos_primera_busqueda)
        tiempo_cache = statistics.mean(tiempos_cache_hits)
        
        print(f"Tiempo inicial bajo carga: {tiempo_inicial:.3f}s")
        print(f"Tiempo cache bajo carga: {tiempo_cache:.3f}s")
        
        # El cache debería mantener buen rendimiento bajo carga
        self.assertLess(tiempo_cache, tiempo_inicial * 0.1)
        self.assertLess(tiempo_cache, 0.01)  # Menos de 10ms incluso bajo carga
    
    def test_eficiencia_memoria_cache(self):
        """Test de eficiencia de memoria del cache"""
        # Llenar cache con diferentes tipos de datos
        
        # Departamentos
        self.servicio_busqueda.obtener_departamentos_disponibles()
        
        # Obras de múltiples departamentos
        for dept_id in range(1, 4):
            self.servicio_busqueda.buscar_por_departamento(dept_id)
        
        # Búsquedas por nacionalidad
        for nacionalidad in ["Dutch", "French", "Italian"]:
            self.servicio_busqueda.buscar_por_nacionalidad(nacionalidad)
        
        # Obtener estadísticas
        estadisticas = self.almacen_datos.obtener_estadisticas_cache()
        
        print(f"Obras en cache: {estadisticas['obras_en_cache']}")
        print(f"Búsquedas en cache: {estadisticas['busquedas_en_cache']}")
        print(f"Memoria estimada: {estadisticas['memoria_estimada_kb']} KB")
        
        # Verificar que el uso de memoria es eficiente
        # Menos de 10KB por obra en promedio
        if estadisticas['obras_en_cache'] > 0:
            memoria_por_obra = estadisticas['memoria_estimada_kb'] / estadisticas['obras_en_cache']
            self.assertLess(memoria_por_obra, 10)
        
        # Memoria total razonable (menos de 1MB)
        self.assertLess(estadisticas['memoria_estimada_kb'], 1024)
    
    def test_degradacion_rendimiento_cache_lleno(self):
        """Test de degradación de rendimiento con cache lleno"""
        # Llenar cache hasta el límite
        for i in range(100):
            obra = ObraArte(
                id_obra=i,
                titulo=f"Obra {i}",
                artista=Artista(f"Artist {i}", "Test Nationality")
            )
            self.almacen_datos.almacenar_obra(obra)
        
        # Medir tiempo de operaciones con cache lleno
        tiempos_busqueda = []
        tiempos_almacenamiento = []
        
        for i in range(10):
            # Buscar obra existente
            inicio = time.time()
            self.almacen_datos.obtener_obra(i)
            tiempo_busqueda = time.time() - inicio
            tiempos_busqueda.append(tiempo_busqueda)
            
            # Almacenar nueva obra
            nueva_obra = ObraArte(
                id_obra=1000 + i,
                titulo=f"Nueva Obra {i}",
                artista=Artista(f"New Artist {i}", "Test")
            )
            inicio = time.time()
            self.almacen_datos.almacenar_obra(nueva_obra)
            tiempo_almacenamiento = time.time() - inicio
            tiempos_almacenamiento.append(tiempo_almacenamiento)
        
        # Verificar que el rendimiento sigue siendo bueno
        tiempo_promedio_busqueda = statistics.mean(tiempos_busqueda)
        tiempo_promedio_almacenamiento = statistics.mean(tiempos_almacenamiento)
        
        print(f"Tiempo búsqueda con cache lleno: {tiempo_promedio_busqueda:.6f}s")
        print(f"Tiempo almacenamiento con cache lleno: {tiempo_promedio_almacenamiento:.6f}s")
        
        # Incluso con cache lleno, las operaciones deben ser rápidas
        self.assertLess(tiempo_promedio_busqueda, 0.001)      # Menos de 1ms
        self.assertLess(tiempo_promedio_almacenamiento, 0.01) # Menos de 10ms
    
    def test_hit_ratio_optimo(self):
        """Test de ratio de hits óptimo en uso normal"""
        # Simular uso normal: búsquedas repetidas con algunas variaciones
        
        # Búsquedas por departamento (repetidas)
        for _ in range(3):
            self.servicio_busqueda.buscar_por_departamento(1)
            self.servicio_busqueda.buscar_por_departamento(2)
        
        # Obtener departamentos (repetido)
        for _ in range(5):
            self.servicio_busqueda.obtener_departamentos_disponibles()
        
        # Detalles de obras (algunas repetidas)
        for obra_id in [1, 2, 3, 1, 2, 4, 5, 1]:
            try:
                self.servicio_obras.obtener_detalles_obra(obra_id)
            except:
                pass
        
        # Verificar estadísticas
        estadisticas = self.almacen_datos.obtener_estadisticas_cache()
        
        print(f"Hit ratio obras: {estadisticas['hit_ratio_obras']:.2%}")
        print(f"Hit ratio departamentos: {estadisticas['hit_ratio_departamentos']:.2%}")
        print(f"Hit ratio búsquedas: {estadisticas['hit_ratio_busquedas']:.2%}")
        
        # En uso normal, deberíamos tener buenos hit ratios
        self.assertGreater(estadisticas['hit_ratio_departamentos'], 0.6)  # >60%
        
        # Para obras, depende del patrón de uso, pero debería haber algunos hits
        if estadisticas['hits_obras'] + estadisticas['misses_obras'] > 0:
            self.assertGreater(estadisticas['hit_ratio_obras'], 0.2)  # >20%


class TestRendimientoComparativo(unittest.TestCase):
    """Tests comparativos de rendimiento con y sin cache"""
    
    def setUp(self):
        """Configuración para tests comparativos"""
        # Servicio sin cache
        self.mock_cliente_api_sin_cache = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_sin_cache = Mock(spec=GestorNacionalidades)
        
        self.servicio_sin_cache = ServicioBusqueda(
            self.mock_cliente_api_sin_cache,
            self.mock_gestor_sin_cache
            # Sin almacen_datos - usa cache por defecto
        )
        
        # Servicio con cache
        self.almacen_datos = AlmacenDatos()
        self.mock_cliente_api_con_cache = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_con_cache = Mock(spec=GestorNacionalidades)
        
        self.servicio_con_cache = ServicioBusqueda(
            self.mock_cliente_api_con_cache,
            self.mock_gestor_con_cache,
            self.almacen_datos
        )
        
        # Configurar mocks idénticos
        self._configurar_mocks_identicos()
    
    def _configurar_mocks_identicos(self):
        """Configura mocks idénticos para comparación justa"""
        def mock_lento():
            time.sleep(0.05)  # 50ms de latencia
            return [Departamento(1, "Test Department")]
        
        self.mock_cliente_api_sin_cache.obtener_departamentos.side_effect = mock_lento
        self.mock_cliente_api_con_cache.obtener_departamentos.side_effect = mock_lento
    
    def test_comparacion_departamentos_repetidos(self):
        """Comparación de rendimiento para obtención repetida de departamentos"""
        # Test sin cache
        tiempos_sin_cache = []
        for _ in range(5):
            inicio = time.time()
            self.servicio_sin_cache.obtener_departamentos_disponibles()
            tiempo = time.time() - inicio
            tiempos_sin_cache.append(tiempo)
        
        # Test con cache (primera llamada llena el cache)
        self.servicio_con_cache.obtener_departamentos_disponibles()
        
        tiempos_con_cache = []
        for _ in range(5):
            inicio = time.time()
            self.servicio_con_cache.obtener_departamentos_disponibles()
            tiempo = time.time() - inicio
            tiempos_con_cache.append(tiempo)
        
        # Comparar resultados
        tiempo_promedio_sin_cache = statistics.mean(tiempos_sin_cache)
        tiempo_promedio_con_cache = statistics.mean(tiempos_con_cache)
        
        mejora = tiempo_promedio_sin_cache / tiempo_promedio_con_cache
        
        print(f"Sin cache: {tiempo_promedio_sin_cache:.3f}s")
        print(f"Con cache: {tiempo_promedio_con_cache:.3f}s")
        print(f"Mejora: {mejora:.1f}x")
        
        # El cache debe proporcionar mejora significativa
        self.assertGreater(mejora, 5)


if __name__ == '__main__':
    # Ejecutar tests con output detallado
    unittest.main(verbosity=2)
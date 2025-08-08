"""
Tests unitarios para el sistema de almacenamiento y cache de datos.
"""

import unittest
import time
from unittest.mock import Mock, patch
from utils.almacen_datos import AlmacenDatos, EntradaCache
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestEntradaCache(unittest.TestCase):
    """Tests para la clase EntradaCache"""
    
    def test_creacion_entrada_cache(self):
        """Test de creación de entrada de cache"""
        datos = "test_data"
        entrada = EntradaCache(datos, tiempo_vida=60)
        
        self.assertEqual(entrada.datos, datos)
        self.assertEqual(entrada.tiempo_vida, 60)
        self.assertTrue(entrada.es_valida())
        self.assertEqual(entrada.obtener_datos(), datos)
    
    def test_entrada_cache_expirada(self):
        """Test de entrada de cache expirada"""
        datos = "test_data"
        entrada = EntradaCache(datos, tiempo_vida=0.1)  # 0.1 segundos
        
        # Inicialmente válida
        self.assertTrue(entrada.es_valida())
        self.assertEqual(entrada.obtener_datos(), datos)
        
        # Esperar a que expire
        time.sleep(0.2)
        
        # Ahora debe estar expirada
        self.assertFalse(entrada.es_valida())
        self.assertIsNone(entrada.obtener_datos())
    
    def test_entrada_cache_tiempo_vida_default(self):
        """Test de tiempo de vida por defecto"""
        entrada = EntradaCache("test")
        self.assertEqual(entrada.tiempo_vida, 300)  # 5 minutos por defecto


class TestAlmacenDatos(unittest.TestCase):
    """Tests para la clase AlmacenDatos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.almacen = AlmacenDatos()
        
        # Crear objetos de prueba
        self.artista_test = Artista(
            nombre="Vincent van Gogh",
            nacionalidad="Dutch",
            fecha_nacimiento="1853",
            fecha_muerte="1890"
        )
        
        self.obra_test = ObraArte(
            id_obra=123,
            titulo="The Starry Night",
            artista=self.artista_test,
            clasificacion="Paintings",
            fecha_creacion="1889",
            url_imagen="https://example.com/image.jpg",
            departamento="European Paintings"
        )
        
        self.departamentos_test = [
            Departamento(1, "American Decorative Arts"),
            Departamento(3, "Ancient Near Eastern Art")
        ]
    
    def test_almacenar_y_obtener_obra(self):
        """Test de almacenamiento y obtención de obras"""
        # Inicialmente no debe estar en cache
        self.assertIsNone(self.almacen.obtener_obra(123))
        
        # Almacenar obra
        self.almacen.almacenar_obra(self.obra_test)
        
        # Ahora debe estar en cache
        obra_obtenida = self.almacen.obtener_obra(123)
        self.assertIsNotNone(obra_obtenida)
        self.assertEqual(obra_obtenida.id_obra, 123)
        self.assertEqual(obra_obtenida.titulo, "The Starry Night")
    
    def test_almacenar_obra_invalida(self):
        """Test de almacenamiento de obra inválida"""
        with self.assertRaises(ValueError):
            self.almacen.almacenar_obra("not_an_obra")
    
    def test_almacenar_y_obtener_departamentos(self):
        """Test de almacenamiento y obtención de departamentos"""
        # Inicialmente no debe estar en cache
        self.assertIsNone(self.almacen.obtener_departamentos())
        
        # Almacenar departamentos
        self.almacen.almacenar_departamentos(self.departamentos_test)
        
        # Ahora debe estar en cache
        departamentos_obtenidos = self.almacen.obtener_departamentos()
        self.assertIsNotNone(departamentos_obtenidos)
        self.assertEqual(len(departamentos_obtenidos), 2)
        self.assertEqual(departamentos_obtenidos[0].nombre, "American Decorative Arts")
    
    def test_almacenar_departamentos_invalidos(self):
        """Test de almacenamiento de departamentos inválidos"""
        with self.assertRaises(ValueError):
            self.almacen.almacenar_departamentos("not_a_list")
    
    def test_almacenar_y_obtener_resultado_busqueda(self):
        """Test de almacenamiento y obtención de resultados de búsqueda"""
        clave = "test_search"
        ids_obras = [123, 456, 789]
        
        # Inicialmente no debe estar en cache
        self.assertIsNone(self.almacen.obtener_resultado_busqueda(clave))
        
        # Almacenar resultado
        self.almacen.almacenar_resultado_busqueda(clave, ids_obras)
        
        # Ahora debe estar en cache
        resultado_obtenido = self.almacen.obtener_resultado_busqueda(clave)
        self.assertIsNotNone(resultado_obtenido)
        self.assertEqual(resultado_obtenido, ids_obras)
    
    def test_almacenar_resultado_busqueda_invalido(self):
        """Test de almacenamiento de resultado de búsqueda inválido"""
        with self.assertRaises(ValueError):
            self.almacen.almacenar_resultado_busqueda("test", "not_a_list")
    
    def test_almacenar_y_obtener_ids_departamento(self):
        """Test de almacenamiento y obtención de IDs de departamento"""
        id_departamento = 1
        ids_obras = [123, 456]
        
        # Inicialmente no debe estar en cache
        self.assertIsNone(self.almacen.obtener_ids_departamento(id_departamento))
        
        # Almacenar IDs
        self.almacen.almacenar_ids_departamento(id_departamento, ids_obras)
        
        # Ahora debe estar en cache
        ids_obtenidos = self.almacen.obtener_ids_departamento(id_departamento)
        self.assertIsNotNone(ids_obtenidos)
        self.assertEqual(ids_obtenidos, ids_obras)
    
    def test_buscar_obras_por_criterio(self):
        """Test de búsqueda de obras por criterio"""
        # Almacenar varias obras
        obra1 = ObraArte(1, "Obra 1", self.artista_test, "Paintings")
        obra2 = ObraArte(2, "Obra 2", self.artista_test, "Sculptures")
        obra3 = ObraArte(3, "Obra 3", self.artista_test, "Paintings")
        
        self.almacen.almacenar_obra(obra1)
        self.almacen.almacenar_obra(obra2)
        self.almacen.almacenar_obra(obra3)
        
        # Buscar obras de tipo "Paintings"
        criterio = lambda obra: obra.clasificacion == "Paintings"
        obras_encontradas = self.almacen.buscar_obras_por_criterio(criterio)
        
        self.assertEqual(len(obras_encontradas), 2)
        self.assertTrue(all(obra.clasificacion == "Paintings" for obra in obras_encontradas))
    
    def test_invalidar_cache_obras(self):
        """Test de invalidación de cache de obras"""
        self.almacen.almacenar_obra(self.obra_test)
        self.assertIsNotNone(self.almacen.obtener_obra(123))
        
        self.almacen.invalidar_cache_obras()
        self.assertIsNone(self.almacen.obtener_obra(123))
    
    def test_invalidar_cache_departamentos(self):
        """Test de invalidación de cache de departamentos"""
        self.almacen.almacenar_departamentos(self.departamentos_test)
        self.assertIsNotNone(self.almacen.obtener_departamentos())
        
        self.almacen.invalidar_cache_departamentos()
        self.assertIsNone(self.almacen.obtener_departamentos())
    
    def test_invalidar_cache_busquedas(self):
        """Test de invalidación de cache de búsquedas"""
        self.almacen.almacenar_resultado_busqueda("test", [123])
        self.assertIsNotNone(self.almacen.obtener_resultado_busqueda("test"))
        
        self.almacen.invalidar_cache_busquedas()
        self.assertIsNone(self.almacen.obtener_resultado_busqueda("test"))
    
    def test_invalidar_todo_cache(self):
        """Test de invalidación completa del cache"""
        # Llenar cache
        self.almacen.almacenar_obra(self.obra_test)
        self.almacen.almacenar_departamentos(self.departamentos_test)
        self.almacen.almacenar_resultado_busqueda("test", [123])
        self.almacen.almacenar_ids_departamento(1, [123])
        
        # Verificar que está lleno
        self.assertIsNotNone(self.almacen.obtener_obra(123))
        self.assertIsNotNone(self.almacen.obtener_departamentos())
        self.assertIsNotNone(self.almacen.obtener_resultado_busqueda("test"))
        self.assertIsNotNone(self.almacen.obtener_ids_departamento(1))
        
        # Invalidar todo
        self.almacen.invalidar_todo_cache()
        
        # Verificar que está vacío
        self.assertIsNone(self.almacen.obtener_obra(123))
        self.assertIsNone(self.almacen.obtener_departamentos())
        self.assertIsNone(self.almacen.obtener_resultado_busqueda("test"))
        self.assertIsNone(self.almacen.obtener_ids_departamento(1))
    
    def test_estadisticas_cache(self):
        """Test de obtención de estadísticas del cache"""
        # Cache vacío
        estadisticas = self.almacen.obtener_estadisticas_cache()
        self.assertEqual(estadisticas['obras_en_cache'], 0)
        self.assertEqual(estadisticas['hits_obras'], 0)
        self.assertEqual(estadisticas['misses_obras'], 0)
        
        # Agregar datos y generar hits/misses
        self.almacen.almacenar_obra(self.obra_test)
        
        # Generar hit
        self.almacen.obtener_obra(123)
        
        # Generar miss
        self.almacen.obtener_obra(999)
        
        # Verificar estadísticas
        estadisticas = self.almacen.obtener_estadisticas_cache()
        self.assertEqual(estadisticas['obras_en_cache'], 1)
        self.assertEqual(estadisticas['hits_obras'], 1)
        self.assertEqual(estadisticas['misses_obras'], 1)
        self.assertEqual(estadisticas['hit_ratio_obras'], 0.5)
    
    def test_limpiar_cache_manual(self):
        """Test de limpieza manual del cache"""
        # Agregar entrada que expirará pronto
        entrada_corta = EntradaCache(self.obra_test, tiempo_vida=0.1)
        self.almacen._cache_obras[123] = entrada_corta
        
        # Agregar entrada que no expirará
        self.almacen.almacenar_obra(ObraArte(456, "Obra 2", self.artista_test))
        
        # Esperar a que expire la primera
        time.sleep(0.2)
        
        # Limpiar manualmente
        resultado = self.almacen.limpiar_cache_manual()
        
        # Verificar que se eliminó la entrada expirada
        self.assertEqual(resultado['obras_eliminadas'], 1)
        self.assertIsNone(self.almacen.obtener_obra(123))
        self.assertIsNotNone(self.almacen.obtener_obra(456))
    
    @patch('utils.almacen_datos.AlmacenDatos._limpiar_cache_si_necesario')
    def test_limpieza_automatica_activada(self, mock_limpiar):
        """Test de activación de limpieza automática"""
        # Simular cache grande agregando muchas entradas
        for i in range(1, 1002):  # Más del límite de 1000, empezando desde 1
            self.almacen.almacenar_obra(ObraArte(i, f"Obra {i}", self.artista_test))
        
        # Verificar que se llamó la limpieza automática
        mock_limpiar.assert_called()
    
    def test_thread_safety_basico(self):
        """Test básico de thread safety"""
        import threading
        
        def agregar_obras():
            for i in range(1, 101):  # Empezar desde 1
                obra = ObraArte(i, f"Obra {i}", self.artista_test)
                self.almacen.almacenar_obra(obra)
        
        def obtener_obras():
            for i in range(1, 101):  # Empezar desde 1
                self.almacen.obtener_obra(i)
        
        # Ejecutar operaciones concurrentes
        thread1 = threading.Thread(target=agregar_obras)
        thread2 = threading.Thread(target=obtener_obras)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verificar que no hubo errores (el test pasa si no hay excepciones)
        estadisticas = self.almacen.obtener_estadisticas_cache()
        self.assertGreaterEqual(estadisticas['obras_en_cache'], 0)


class TestRendimientoAlmacenDatos(unittest.TestCase):
    """Tests de rendimiento para el sistema de cache"""
    
    def setUp(self):
        """Configuración inicial para tests de rendimiento"""
        self.almacen = AlmacenDatos()
        self.artista_test = Artista("Test Artist", "Test Nationality")
    
    def test_rendimiento_almacenamiento_obras(self):
        """Test de rendimiento para almacenamiento de obras"""
        import time
        
        inicio = time.time()
        
        # Almacenar 1000 obras
        for i in range(1, 1001):  # Empezar desde 1
            obra = ObraArte(i, f"Obra {i}", self.artista_test)
            self.almacen.almacenar_obra(obra)
        
        tiempo_almacenamiento = time.time() - inicio
        
        # Verificar que el almacenamiento es rápido (menos de 1 segundo)
        self.assertLess(tiempo_almacenamiento, 1.0)
        
        # Verificar que todas las obras están en cache
        self.assertEqual(self.almacen.obtener_estadisticas_cache()['obras_en_cache'], 1000)
    
    def test_rendimiento_busqueda_obras(self):
        """Test de rendimiento para búsqueda de obras"""
        import time
        
        # Llenar cache con obras
        for i in range(1, 1001):  # Empezar desde 1
            obra = ObraArte(i, f"Obra {i}", self.artista_test)
            self.almacen.almacenar_obra(obra)
        
        inicio = time.time()
        
        # Buscar 1000 obras (todas deberían estar en cache)
        for i in range(1, 1001):  # Empezar desde 1
            obra = self.almacen.obtener_obra(i)
            self.assertIsNotNone(obra)
        
        tiempo_busqueda = time.time() - inicio
        
        # Verificar que la búsqueda es rápida (menos de 0.5 segundos)
        self.assertLess(tiempo_busqueda, 0.5)
        
        # Verificar hit ratio perfecto
        estadisticas = self.almacen.obtener_estadisticas_cache()
        self.assertEqual(estadisticas['hit_ratio_obras'], 1.0)
    
    def test_rendimiento_busqueda_por_criterio(self):
        """Test de rendimiento para búsqueda por criterio"""
        import time
        
        # Llenar cache con obras de diferentes tipos
        for i in range(500):
            obra1 = ObraArte(i*2+1, f"Painting {i}", self.artista_test, "Paintings")  # +1 para evitar ID 0
            obra2 = ObraArte(i*2+2, f"Sculpture {i}", self.artista_test, "Sculptures")
            self.almacen.almacenar_obra(obra1)
            self.almacen.almacenar_obra(obra2)
        
        inicio = time.time()
        
        # Buscar todas las pinturas
        criterio = lambda obra: obra.clasificacion == "Paintings"
        pinturas = self.almacen.buscar_obras_por_criterio(criterio)
        
        tiempo_busqueda = time.time() - inicio
        
        # Verificar que la búsqueda es rápida (menos de 0.1 segundos)
        self.assertLess(tiempo_busqueda, 0.1)
        
        # Verificar que encontró todas las pinturas
        self.assertEqual(len(pinturas), 500)
        self.assertTrue(all(obra.clasificacion == "Paintings" for obra in pinturas))


if __name__ == '__main__':
    unittest.main()
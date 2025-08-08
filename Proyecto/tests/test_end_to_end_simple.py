"""
Tests end-to-end simplificados para validar flujos principales del sistema.

Estos tests se enfocan en validar la funcionalidad principal sin mocking complejo,
usando componentes reales donde sea posible.
"""

import unittest
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gestor_nacionalidades import GestorNacionalidades, ErrorArchivoNacionalidades
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento
from services.cliente_api_met_museum import ExcepcionesAPIMetMuseum


class TestEndToEndSimple(unittest.TestCase):
    """Tests end-to-end simplificados para funcionalidades principales"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_simple.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\nGerman\nBritish\nJapanese\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    def test_gestor_nacionalidades_carga_archivo_real(self):
        """Test end-to-end: Carga real de archivo de nacionalidades"""
        gestor = GestorNacionalidades(self.archivo_nacionalidades_test)
        gestor.cargar_nacionalidades()
        
        # Verificar que se cargaron correctamente
        nacionalidades = gestor.obtener_nacionalidades_disponibles()
        self.assertEqual(len(nacionalidades), 8)
        self.assertIn("American", nacionalidades)
        self.assertIn("French", nacionalidades)
        self.assertIn("Japanese", nacionalidades)
        
        # Verificar validación
        self.assertTrue(gestor.validar_nacionalidad("American"))
        self.assertFalse(gestor.validar_nacionalidad("Martian"))
    
    def test_gestor_nacionalidades_archivo_vacio(self):
        """Test end-to-end: Manejo de archivo vacío"""
        archivo_vacio = "test_nacionalidades_vacio.txt"
        with open(archivo_vacio, 'w', encoding='utf-8') as f:
            f.write("")
        
        try:
            gestor = GestorNacionalidades(archivo_vacio)
            
            # El gestor debe lanzar excepción para archivo vacío
            with self.assertRaises(ErrorArchivoNacionalidades):
                gestor.cargar_nacionalidades()
            
        finally:
            if os.path.exists(archivo_vacio):
                os.remove(archivo_vacio)
    
    def test_gestor_nacionalidades_archivo_inexistente(self):
        """Test end-to-end: Manejo de archivo inexistente"""
        gestor = GestorNacionalidades("archivo_inexistente.txt")
        
        with self.assertRaises(ErrorArchivoNacionalidades):
            gestor.cargar_nacionalidades()
    
    def test_modelos_datos_integracion_completa(self):
        """Test end-to-end: Integración completa de modelos de datos"""
        # Crear artista
        artista = Artista("Claude Monet", "French", "1840", "1926")
        
        # Crear obra
        obra = ObraArte(
            436535, "Water Lilies", artista, 
            "Painting", "1919", "http://example.com/waterlilies.jpg",
            "European Paintings"
        )
        
        # Verificar integración
        self.assertEqual(obra.artista.nombre, "Claude Monet")
        self.assertEqual(obra.artista.nacionalidad, "French")
        self.assertTrue(obra.tiene_imagen())
        
        # Verificar formateo
        resumen = obra.mostrar_resumen()
        self.assertIn("Water Lilies", resumen)
        self.assertIn("Claude Monet", resumen)
        
        detalles = obra.mostrar_detalles_completos()
        self.assertIn("Water Lilies", detalles)
        self.assertIn("Claude Monet", detalles)
        self.assertIn("French", detalles)
        self.assertIn("1840-1926", detalles)
        self.assertIn("Painting", detalles)
        self.assertIn("1919", detalles)
    
    def test_departamento_modelo_completo(self):
        """Test end-to-end: Modelo de departamento completo"""
        departamento = Departamento(11, "European Paintings")
        
        self.assertEqual(departamento.id_departamento, 11)
        self.assertEqual(departamento.nombre, "European Paintings")
        
        # Verificar representación string
        str_repr = str(departamento)
        self.assertIn("European Paintings", str_repr)
    
    def test_flujo_busqueda_nacionalidad_con_archivo_real(self):
        """Test end-to-end: Flujo de búsqueda por nacionalidad con archivo real"""
        # Cargar nacionalidades reales
        gestor = GestorNacionalidades(self.archivo_nacionalidades_test)
        gestor.cargar_nacionalidades()
        
        # Simular selección de nacionalidad
        nacionalidades_disponibles = gestor.obtener_nacionalidades_disponibles()
        self.assertIn("French", nacionalidades_disponibles)
        
        # Validar nacionalidad seleccionada
        nacionalidad_seleccionada = "French"
        self.assertTrue(gestor.validar_nacionalidad(nacionalidad_seleccionada))
        
        # Simular creación de obras filtradas
        obras_francesas = [
            ObraArte(1, "Impression, Sunrise", Artista("Claude Monet", "French"), 
                    "Painting", "1872", "", "European Paintings"),
            ObraArte(2, "The Thinker", Artista("Auguste Rodin", "French"), 
                    "Sculpture", "1904", "", "European Sculpture")
        ]
        
        # Verificar que todas las obras son francesas
        for obra in obras_francesas:
            self.assertEqual(obra.artista.nacionalidad, "French")
    
    def test_manejo_errores_api_simulado(self):
        """Test end-to-end: Manejo de diferentes tipos de errores de API"""
        errores_a_probar = [
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("No se puede conectar"),
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Obra no encontrada"),
            ExcepcionesAPIMetMuseum.ErrorDatosIncompletos("Datos faltantes"),
            ExcepcionesAPIMetMuseum.ErrorRateLimitAPI("Límite excedido")
        ]
        
        for error in errores_a_probar:
            with self.subTest(error=type(error).__name__):
                # Verificar que el error se puede crear y tiene mensaje
                self.assertIsInstance(error, Exception)
                self.assertTrue(len(str(error)) > 0)
                
                # Verificar jerarquía de excepciones
                self.assertIsInstance(error, ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)
    
    def test_integracion_obra_artista_departamento(self):
        """Test end-to-end: Integración completa entre obra, artista y departamento"""
        # Crear departamento
        departamento = Departamento(11, "European Paintings")
        
        # Crear artista
        artista = Artista("Vincent van Gogh", "Dutch", "1853", "1890")
        
        # Crear obra
        obra = ObraArte(
            436532, "The Starry Night", artista,
            "Painting", "1889", "http://example.com/starrynight.jpg",
            departamento.nombre
        )
        
        # Verificar integración completa
        self.assertEqual(obra.departamento, departamento.nombre)
        self.assertEqual(obra.artista.nombre, artista.nombre)
        self.assertEqual(obra.artista.nacionalidad, artista.nacionalidad)
        
        # Verificar que los datos se mantienen consistentes
        detalles = obra.mostrar_detalles_completos()
        self.assertIn(departamento.nombre, detalles)
        self.assertIn(artista.nombre, detalles)
        self.assertIn(artista.nacionalidad, detalles)
    
    def test_casos_edge_entrada_usuario(self):
        """Test end-to-end: Casos edge de entrada de usuario"""
        gestor = GestorNacionalidades(self.archivo_nacionalidades_test)
        gestor.cargar_nacionalidades()
        
        # Casos edge de nacionalidades
        casos_edge = [
            ("american", True),   # Minúsculas (case-insensitive)
            ("AMERICAN", True),   # Mayúsculas (case-insensitive)
            ("American", True),   # Correcto
            ("", False),          # Vacío
            ("   ", False),       # Solo espacios
            ("Martian", False),   # No existe
            ("Amer", False),      # Parcial
        ]
        
        for entrada, esperado in casos_edge:
            with self.subTest(entrada=entrada):
                resultado = gestor.validar_nacionalidad(entrada)
                self.assertEqual(resultado, esperado)
    
    def test_flujo_completo_datos_obra_sin_imagen(self):
        """Test end-to-end: Flujo completo con obra sin imagen"""
        artista = Artista("Unknown Artist", "Unknown")
        obra = ObraArte(
            999999, "Untitled Work", artista,
            "Unknown", "Unknown", "", "Unknown Department"
        )
        
        # Verificar que maneja correctamente la ausencia de imagen
        self.assertFalse(obra.tiene_imagen())
        
        # Verificar que los detalles se muestran correctamente
        detalles = obra.mostrar_detalles_completos()
        self.assertIn("Imagen disponible: No", detalles)
        self.assertIn("Untitled Work", detalles)
        self.assertIn("Unknown Artist", detalles)
    
    def test_validacion_datos_obra_completos(self):
        """Test end-to-end: Validación de datos completos de obra"""
        # Obra con todos los datos
        artista_completo = Artista("Leonardo da Vinci", "Italian", "1452", "1519")
        obra_completa = ObraArte(
            436533, "Mona Lisa", artista_completo,
            "Painting", "1503-1519", "http://example.com/monalisa.jpg",
            "European Paintings"
        )
        
        # Verificar que todos los campos están presentes
        detalles = obra_completa.mostrar_detalles_completos()
        campos_esperados = [
            "Mona Lisa", "Leonardo da Vinci", "Italian",
            "1452-1519", "Painting", "1503-1519",
            "European Paintings", "Imagen disponible: Sí"
        ]
        
        for campo in campos_esperados:
            self.assertIn(campo, detalles)
    
    def test_regresion_funcionalidades_basicas(self):
        """Test de regresión: Funcionalidades básicas del sistema"""
        # Test 1: Carga de nacionalidades
        gestor = GestorNacionalidades(self.archivo_nacionalidades_test)
        gestor.cargar_nacionalidades()
        self.assertTrue(gestor.archivo_cargado)
        self.assertGreater(len(gestor), 0)
        
        # Test 2: Creación de modelos
        artista = Artista("Test Artist", "American")
        self.assertEqual(artista.nombre, "Test Artist")
        self.assertEqual(artista.nacionalidad, "American")
        
        departamento = Departamento(1, "Test Department")
        self.assertEqual(departamento.id_departamento, 1)
        self.assertEqual(departamento.nombre, "Test Department")
        
        obra = ObraArte(1, "Test Artwork", artista, "Painting", "2000")
        self.assertEqual(obra.id_obra, 1)
        self.assertEqual(obra.titulo, "Test Artwork")
        self.assertEqual(obra.artista, artista)
        
        # Test 3: Validaciones
        self.assertTrue(gestor.validar_nacionalidad("American"))
        self.assertFalse(gestor.validar_nacionalidad("Inexistente"))
        
        # Test 4: Formateo
        resumen = obra.mostrar_resumen()
        self.assertIn("Test Artwork", resumen)
        self.assertIn("Test Artist", resumen)


if __name__ == '__main__':
    unittest.main(verbosity=2)
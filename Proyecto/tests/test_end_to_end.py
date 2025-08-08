"""
Tests de integración end-to-end para el sistema completo del catálogo del museo.

Estos tests validan flujos completos de la aplicación desde la entrada del usuario
hasta la salida final, integrando todos los componentes del sistema.
"""

import unittest
import pytest
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controlador_principal import ControladorPrincipal
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from services.servicio_busqueda import ServicioBusqueda, ExcepcionesServicioBusqueda
from services.servicio_obras import ServicioObras
from utils.gestor_nacionalidades import GestorNacionalidades, ErrorArchivoNacionalidades
from ui.interfaz_usuario import InterfazUsuario
from ui.visualizador_imagenes import VisualizadorImagenes
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestEndToEndBusquedaDepartamento(unittest.TestCase):
    """Tests end-to-end para flujos completos de búsqueda por departamento"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\nGerman\nBritish\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    def test_flujo_completo_busqueda_departamento_exitoso(self, mock_servicio_obras, mock_servicio_busqueda, mock_visualizador, mock_interfaz):
        """Test end-to-end: Flujo completo de búsqueda por departamento exitoso"""
        # Configurar datos de prueba
        departamentos_mock = [
            Departamento(1, "American Decorative Arts"),
            Departamento(3, "Ancient Near Eastern Art"),
            Departamento(11, "European Paintings")
        ]
        
        obras_mock = [
            ObraArte(12345, "Test Artwork 1", Artista("Test Artist 1", "American"), 
                    "Painting", "1850", "http://example.com/image1.jpg", "American Decorative Arts"),
            ObraArte(12346, "Test Artwork 2", Artista("Test Artist 2", "American"), 
                    "Sculpture", "1860", "", "American Decorative Arts")
        ]
        
        # Configurar mocks de servicios
        mock_servicio_busqueda_instance = Mock()
        mock_servicio_busqueda.return_value = mock_servicio_busqueda_instance
        mock_servicio_busqueda_instance.obtener_departamentos_disponibles.return_value = departamentos_mock
        mock_servicio_busqueda_instance.buscar_por_departamento.return_value = obras_mock
        
        mock_servicio_obras_instance = Mock()
        mock_servicio_obras.return_value = mock_servicio_obras_instance
        mock_servicio_obras_instance.obtener_detalles_obra.return_value = obras_mock[0]
        
        # Configurar mock de interfaz para simular interacción completa
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
        mock_interfaz_instance.confirmar_accion.side_effect = [True, True, False]  # Ver detalles, ver imagen, no continuar
        mock_interfaz_instance.solicitar_id_obra.return_value = 12345
        
        # Configurar mock de visualizador
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador con gestor real
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            with patch('controlador_principal.ClienteAPIMetMuseum') as mock_cliente_class:
                gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
                gestor_real.cargar_nacionalidades()
                mock_gestor_class.return_value = gestor_real
                
                mock_cliente_instance = Mock()
                mock_cliente_class.return_value = mock_cliente_instance
                
                controlador = ControladorPrincipal()
                
                # Ejecutar flujo completo de búsqueda por departamento
                controlador.procesar_busqueda_por_departamento()
                
                # Verificar secuencia completa de llamadas
                mock_servicio_busqueda_instance.obtener_departamentos_disponibles.assert_called_once()
                mock_interfaz_instance.solicitar_seleccion_departamento.assert_called_once_with(departamentos_mock)
                mock_servicio_busqueda_instance.buscar_por_departamento.assert_called_once_with(1)
                mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
                
                # Verificar que se ofrecieron ver detalles
                mock_interfaz_instance.confirmar_accion.assert_any_call("¿Desea ver los detalles de alguna obra específica?")
                mock_interfaz_instance.solicitar_id_obra.assert_called_once()
                mock_interfaz_instance.mostrar_detalles_obra_con_opciones.assert_called_once()
                
                # Verificar que se mostró la imagen
                mock_servicio_obras_instance.mostrar_imagen_obra.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_departamento_sin_obras(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Flujo completo cuando departamento no tiene obras"""
        # Configurar departamentos pero sin obras
        departamentos_mock = [Departamento(1, "Empty Department")]
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.return_value = departamentos_mock
        mock_cliente_instance.obtener_obras_por_departamento.return_value = []
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_departamento()
            
            # Verificar que se mostró lista vacía
            mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
            args, kwargs = mock_interfaz_instance.mostrar_lista_obras.call_args
            self.assertEqual(len(args[0]), 0)  # Lista vacía
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_error_departamento_invalido(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Manejo de error cuando departamento es inválido"""
        departamentos_mock = [Departamento(1, "Valid Department")]
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.return_value = departamentos_mock
        mock_cliente_instance.obtener_obras_por_departamento.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Departamento no encontrado")
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 999
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_departamento()
            
            # Verificar que se mostró mensaje de error apropiado
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("Error del servicio", args[0])


class TestEndToEndBusquedaNacionalidad(unittest.TestCase):
    """Tests end-to-end para flujos completos de búsqueda por nacionalidad"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\nGerman\nBritish\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_busqueda_nacionalidad_con_archivo_real(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Búsqueda por nacionalidad usando archivo real"""
        # Configurar obras de artistas franceses
        obras_data = [
            {
                'objectID': 20001,
                'title': 'French Artwork 1',
                'artistDisplayName': 'Claude Monet',
                'artistNationality': 'French',
                'classification': 'Painting',
                'department': 'European Paintings',
                'objectDate': '1890',
                'primaryImage': 'http://example.com/monet.jpg'
            },
            {
                'objectID': 20002,
                'title': 'French Artwork 2',
                'artistDisplayName': 'Auguste Rodin',
                'artistNationality': 'French',
                'classification': 'Sculpture',
                'department': 'European Sculpture',
                'objectDate': '1885'
            }
        ]
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.buscar_obras_por_query.return_value = [20001, 20002]
        mock_cliente_instance.obtener_detalles_obra.side_effect = obras_data
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_nacionalidad.return_value = "French"
        mock_interfaz_instance.confirmar_accion.return_value = False
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Usar gestor real con archivo de test
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_nacionalidad()
            
            # Verificar que se usó el archivo real de nacionalidades
            nacionalidades_disponibles = gestor_real.obtener_nacionalidades_disponibles()
            self.assertIn("French", nacionalidades_disponibles)
            self.assertIn("American", nacionalidades_disponibles)
            self.assertEqual(len(nacionalidades_disponibles), 7)
            
            # Verificar flujo de búsqueda
            mock_interfaz_instance.solicitar_seleccion_nacionalidad.assert_called_once()
            mock_cliente_instance.buscar_obras_por_query.assert_called_once_with("French")
            mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
            
            # Verificar que se filtraron correctamente las obras francesas
            args, kwargs = mock_interfaz_instance.mostrar_lista_obras.call_args
            obras_mostradas = args[0]
            self.assertTrue(all(obra.artista.nacionalidad == "French" for obra in obras_mostradas))
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_nacionalidad_inexistente_en_archivo(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Error cuando nacionalidad no existe en archivo"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_nacionalidad.return_value = "Martian"  # No existe
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_nacionalidad()
            
            # Verificar que se mostró error de nacionalidad inválida
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("Nacionalidad inválida", args[0])
    
    def test_flujo_completo_archivo_nacionalidades_corrupto(self):
        """Test end-to-end: Error cuando archivo de nacionalidades está corrupto"""
        # Crear archivo corrupto
        archivo_corrupto = "test_nacionalidades_corrupto.txt"
        with open(archivo_corrupto, 'w', encoding='utf-8') as f:
            f.write("")  # Archivo vacío
        
        try:
            with patch('controlador_principal.InterfazUsuario') as mock_interfaz_class:
                with patch('controlador_principal.VisualizadorImagenes') as mock_visualizador_class:
                    with patch('controlador_principal.ClienteAPIMetMuseum') as mock_cliente_class:
                        mock_interfaz_instance = Mock()
                        mock_interfaz_class.return_value = mock_interfaz_instance
                        
                        mock_visualizador_instance = Mock()
                        mock_visualizador_class.return_value = mock_visualizador_instance
                        
                        mock_cliente_instance = Mock()
                        mock_cliente_class.return_value = mock_cliente_instance
                        
                        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
                            gestor_real = GestorNacionalidades(archivo_corrupto)
                            gestor_real.cargar_nacionalidades()
                            mock_gestor_class.return_value = gestor_real
                            
                            controlador = ControladorPrincipal()
                            controlador.procesar_busqueda_por_nacionalidad()
                            
                            # Verificar que se mostró mensaje de error apropiado
                            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
                            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
                            self.assertIn("No hay nacionalidades disponibles", args[0])
        finally:
            if os.path.exists(archivo_corrupto):
                os.remove(archivo_corrupto)


class TestEndToEndBusquedaArtista(unittest.TestCase):
    """Tests end-to-end para búsqueda por artista con casos edge"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_busqueda_artista_nombre_parcial(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Búsqueda por nombre parcial de artista"""
        obras_data = [
            {
                'objectID': 30001,
                'title': 'Water Lilies',
                'artistDisplayName': 'Claude Monet',
                'artistNationality': 'French',
                'classification': 'Painting',
                'department': 'European Paintings'
            },
            {
                'objectID': 30002,
                'title': 'Impression, Sunrise',
                'artistDisplayName': 'Claude Monet',
                'artistNationality': 'French',
                'classification': 'Painting',
                'department': 'European Paintings'
            }
        ]
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.buscar_obras_por_query.return_value = [30001, 30002]
        mock_cliente_instance.obtener_detalles_obra.side_effect = obras_data
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_nombre_artista.return_value = "Monet"  # Nombre parcial
        mock_interfaz_instance.confirmar_accion.return_value = False
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_artista()
            
            # Verificar búsqueda por nombre parcial
            mock_cliente_instance.buscar_obras_por_query.assert_called_once_with("Monet")
            mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
            
            # Verificar que todas las obras son de Monet
            args, kwargs = mock_interfaz_instance.mostrar_lista_obras.call_args
            obras_mostradas = args[0]
            self.assertTrue(all("Monet" in obra.artista.nombre for obra in obras_mostradas))
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_busqueda_artista_caracteres_especiales(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Búsqueda con caracteres especiales en nombre"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.buscar_obras_por_query.return_value = []
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_nombre_artista.return_value = "José María@#$%"
        mock_interfaz_instance.confirmar_accion.return_value = False
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_artista()
            
            # Verificar que se procesó la búsqueda sin errores
            mock_cliente_instance.buscar_obras_por_query.assert_called_once()
            mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_busqueda_artista_nombre_vacio(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Búsqueda con nombre vacío o solo espacios"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_nombre_artista.return_value = "   "  # Solo espacios
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_artista()
            
            # Verificar que se manejó apropiadamente
            # El comportamiento específico depende de la implementación del servicio
            self.assertTrue(True)  # Test pasa si no hay excepciones


class TestEndToEndVisualizacionDetalles(unittest.TestCase):
    """Tests end-to-end para visualización de detalles y manejo de errores"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_detalles_obra_con_imagen(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Visualización completa de detalles con imagen"""
        obra_data = {
            'objectID': 40001,
            'title': 'Masterpiece with Image',
            'artistDisplayName': 'Famous Artist',
            'artistNationality': 'French',
            'artistBeginDate': '1800',
            'artistEndDate': '1880',
            'classification': 'Painting',
            'objectDate': '1850',
            'primaryImage': 'http://example.com/masterpiece.jpg',
            'department': 'European Paintings'
        }
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_detalles_obra.return_value = obra_data
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_id_obra.return_value = 40001
        mock_interfaz_instance.confirmar_accion.return_value = True  # Confirma ver imagen
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_mostrar_detalles_obra()
            
            # Verificar flujo completo
            mock_interfaz_instance.solicitar_id_obra.assert_called_once()
            mock_cliente_instance.obtener_detalles_obra.assert_called_once_with(40001)
            mock_interfaz_instance.mostrar_detalles_obra_con_opciones.assert_called_once()
            mock_interfaz_instance.confirmar_accion.assert_called_with("¿Desea ver la imagen de la obra?")
            mock_visualizador_instance.mostrar_imagen_en_ventana.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_detalles_obra_sin_imagen(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Visualización de detalles sin imagen disponible"""
        obra_data = {
            'objectID': 40002,
            'title': 'Artwork without Image',
            'artistDisplayName': 'Another Artist',
            'artistNationality': 'Italian',
            'classification': 'Sculpture',
            'objectDate': '1900',
            'primaryImage': '',  # Sin imagen
            'department': 'European Sculpture'
        }
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_detalles_obra.return_value = obra_data
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_id_obra.return_value = 40002
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_mostrar_detalles_obra()
            
            # Verificar que se mostraron detalles pero no se ofreció imagen
            mock_interfaz_instance.mostrar_detalles_obra_con_opciones.assert_called_once()
            mock_interfaz_instance.confirmar_accion.assert_not_called()  # No se pregunta por imagen
            mock_visualizador_instance.mostrar_imagen_en_ventana.assert_not_called()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_obra_inexistente(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Error cuando obra no existe"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_detalles_obra.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Obra no encontrada")
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_id_obra.return_value = 99999
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_mostrar_detalles_obra()
            
            # Verificar manejo de error
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("No se encontró una obra con ID 99999", args[0])


class TestEndToEndManejoErroresAPI(unittest.TestCase):
    """Tests end-to-end para manejo de errores de API y conectividad"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_error_conexion_api(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Error de conexión con API"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("No se puede conectar")
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_departamento()
            
            # Verificar manejo de error de conexión
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("Error de conexión con la API", args[0])
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_error_rate_limit(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Error de límite de consultas API"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.buscar_obras_por_query.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRateLimitAPI("Límite excedido")
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_nombre_artista.return_value = "Picasso"
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_artista()
            
            # Verificar manejo de error de rate limit
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("límite de consultas", args[0])
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_flujo_completo_datos_api_corruptos(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test end-to-end: Datos corruptos de la API"""
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_detalles_obra.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorDatosIncompletos("Datos corruptos")
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_id_obra.return_value = 12345
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            controlador.procesar_mostrar_detalles_obra()
            
            # Verificar manejo de datos corruptos
            mock_interfaz_instance.mostrar_mensaje_error.assert_called()
            args, kwargs = mock_interfaz_instance.mostrar_mensaje_error.call_args
            self.assertIn("Datos incompletos", args[0])


class TestEndToEndSuiteRegresion(unittest.TestCase):
    """Suite de tests de regresión para funcionalidades principales"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.archivo_nacionalidades_test = "test_nacionalidades_e2e.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\nGerman\nBritish\nJapanese\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    def test_regresion_inicializacion_completa_sistema(self, mock_servicio_obras, mock_servicio_busqueda, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de regresión: Inicialización completa del sistema"""
        # Configurar mocks para inicialización exitosa
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.return_value = [
            Departamento(1, "Test Department")
        ]
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        mock_servicio_busqueda_instance = Mock()
        mock_servicio_busqueda.return_value = mock_servicio_busqueda_instance
        
        mock_servicio_obras_instance = Mock()
        mock_servicio_obras.return_value = mock_servicio_obras_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            mock_gestor_class.return_value = gestor_real
            
            # Crear controlador (esto ejecuta inicialización)
            controlador = ControladorPrincipal()
            
            # Verificar que todos los componentes se inicializaron
            self.assertIsNotNone(controlador._cliente_api)
            self.assertIsNotNone(controlador._servicio_busqueda)
            self.assertIsNotNone(controlador._servicio_obras)
            self.assertIsNotNone(controlador._gestor_nacionalidades)
            
            # Ejecutar inicialización de recursos
            controlador._inicializar_recursos()
            
            # Verificar que se cargaron las nacionalidades
            self.assertTrue(gestor_real.archivo_cargado)
            self.assertEqual(len(gestor_real), 8)
            
            # Verificar que se verificó la API
            mock_cliente_instance.obtener_departamentos.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    def test_regresion_flujos_busqueda_todos_tipos(self, mock_servicio_obras, mock_servicio_busqueda, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de regresión: Todos los tipos de búsqueda funcionan"""
        # Configurar datos de prueba
        departamentos_mock = [Departamento(1, "Test Department")]
        obra_mock = ObraArte(
            50001, "Regression Test Artwork", 
            Artista("Test Artist", "American"), 
            "Painting", "2000", "", "Test Department"
        )
        
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        
        mock_servicio_busqueda_instance = Mock()
        mock_servicio_busqueda.return_value = mock_servicio_busqueda_instance
        mock_servicio_busqueda_instance.obtener_departamentos_disponibles.return_value = departamentos_mock
        mock_servicio_busqueda_instance.buscar_por_departamento.return_value = [obra_mock]
        mock_servicio_busqueda_instance.buscar_por_nacionalidad.return_value = [obra_mock]
        mock_servicio_busqueda_instance.buscar_por_nombre_artista.return_value = [obra_mock]
        
        mock_servicio_obras_instance = Mock()
        mock_servicio_obras.return_value = mock_servicio_obras_instance
        mock_servicio_obras_instance.obtener_detalles_obra.return_value = obra_mock
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
        mock_interfaz_instance.solicitar_seleccion_nacionalidad.return_value = "American"
        mock_interfaz_instance.solicitar_nombre_artista.return_value = "Test Artist"
        mock_interfaz_instance.solicitar_id_obra.return_value = 50001
        mock_interfaz_instance.confirmar_accion.return_value = False
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            
            # Test búsqueda por departamento
            controlador.procesar_busqueda_por_departamento()
            mock_interfaz_instance.mostrar_lista_obras.assert_called()
            
            # Reset mock para siguiente test
            mock_interfaz_instance.reset_mock()
            
            # Test búsqueda por nacionalidad
            controlador.procesar_busqueda_por_nacionalidad()
            mock_interfaz_instance.mostrar_lista_obras.assert_called()
            
            # Reset mock para siguiente test
            mock_interfaz_instance.reset_mock()
            
            # Test búsqueda por artista
            controlador.procesar_busqueda_por_artista()
            mock_interfaz_instance.mostrar_lista_obras.assert_called()
            
            # Reset mock para siguiente test
            mock_interfaz_instance.reset_mock()
            
            # Test mostrar detalles
            controlador.procesar_mostrar_detalles_obra()
            mock_interfaz_instance.mostrar_detalles_obra_con_opciones.assert_called()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    def test_regresion_manejo_errores_consistente(self, mock_servicio_obras, mock_servicio_busqueda, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de regresión: Manejo consistente de errores en todos los flujos"""
        # Configurar diferentes tipos de errores
        errores_a_probar = [
            ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido("Error departamento"),
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error conexión"),
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("No encontrado"),
            ExcepcionesAPIMetMuseum.ErrorDatosIncompletos("Datos incompletos")
        ]
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
        mock_interfaz_instance.solicitar_id_obra.return_value = 12345
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            gestor_real.cargar_nacionalidades()
            mock_gestor_class.return_value = gestor_real
            
            for error in errores_a_probar:
                with self.subTest(error=type(error).__name__):
                    mock_cliente_instance = Mock()
                    mock_cliente.return_value = mock_cliente_instance
                    
                    mock_servicio_busqueda_instance = Mock()
                    mock_servicio_busqueda.return_value = mock_servicio_busqueda_instance
                    mock_servicio_busqueda_instance.obtener_departamentos_disponibles.side_effect = error
                    
                    mock_servicio_obras_instance = Mock()
                    mock_servicio_obras.return_value = mock_servicio_obras_instance
                    mock_servicio_obras_instance.obtener_detalles_obra.side_effect = error
                    
                    controlador = ControladorPrincipal()
                    
                    # Test error en búsqueda por departamento
                    mock_interfaz_instance.reset_mock()
                    controlador.procesar_busqueda_por_departamento()
                    mock_interfaz_instance.mostrar_mensaje_error.assert_called()
                    
                    # Test error en mostrar detalles
                    mock_interfaz_instance.reset_mock()
                    controlador.procesar_mostrar_detalles_obra()
                    mock_interfaz_instance.mostrar_mensaje_error.assert_called()
    
    def test_regresion_integridad_archivo_nacionalidades(self):
        """Test de regresión: Integridad del archivo de nacionalidades"""
        # Verificar que el archivo real existe y es válido
        archivo_real = "nacionalidades.txt"
        
        if os.path.exists(archivo_real):
            gestor = GestorNacionalidades(archivo_real)
            gestor.cargar_nacionalidades()
            
            nacionalidades = gestor.obtener_nacionalidades_disponibles()
            
            # Verificar que hay nacionalidades cargadas
            self.assertGreater(len(nacionalidades), 0)
            
            # Verificar que no hay duplicados
            self.assertEqual(len(nacionalidades), len(set(nacionalidades)))
            
            # Verificar que no hay entradas vacías
            self.assertTrue(all(nac.strip() for nac in nacionalidades))
            
            # Verificar algunas nacionalidades comunes
            nacionalidades_lower = [nac.lower() for nac in nacionalidades]
            self.assertIn("american", nacionalidades_lower)
            self.assertIn("french", nacionalidades_lower)
        else:
            self.skipTest("Archivo nacionalidades.txt no encontrado")


if __name__ == '__main__':
    # Configurar para ejecutar todos los tests end-to-end
    unittest.main(verbosity=2)
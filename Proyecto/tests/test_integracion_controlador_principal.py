"""
Tests de integración para el controlador principal del sistema de catálogo del museo.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controlador_principal import ControladorPrincipal
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from services.servicio_busqueda import ServicioBusqueda
from services.servicio_obras import ServicioObras
from utils.gestor_nacionalidades import GestorNacionalidades
from ui.interfaz_usuario import InterfazUsuario
from ui.visualizador_imagenes import VisualizadorImagenes
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestIntegracionControladorPrincipal(unittest.TestCase):
    """Tests de integración para el controlador principal"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear archivo temporal de nacionalidades para tests
        self.archivo_nacionalidades_test = "test_nacionalidades.txt"
        with open(self.archivo_nacionalidades_test, 'w', encoding='utf-8') as f:
            f.write("American\nFrench\nItalian\nSpanish\nDutch\n")
    
    def tearDown(self):
        """Limpieza después de cada test"""
        # Eliminar archivo temporal
        if os.path.exists(self.archivo_nacionalidades_test):
            os.remove(self.archivo_nacionalidades_test)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    def test_integracion_inicializacion_completa(self, mock_visualizador, mock_interfaz):
        """Test de integración de inicialización completa del controlador"""
        # Configurar mocks básicos
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador con archivo de nacionalidades de test
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor:
            mock_gestor_instance = Mock()
            mock_gestor.return_value = mock_gestor_instance
            
            controlador = ControladorPrincipal()
            
            # Verificar que todas las dependencias se inicializaron
            self.assertIsInstance(controlador._cliente_api, ClienteAPIMetMuseum)
            self.assertIsInstance(controlador._servicio_busqueda, ServicioBusqueda)
            self.assertIsInstance(controlador._servicio_obras, ServicioObras)
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_integracion_flujo_busqueda_departamento(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de integración del flujo completo de búsqueda por departamento"""
        # Configurar datos de prueba
        departamentos_mock = [
            Departamento(1, "American Decorative Arts"),
            Departamento(3, "Ancient Near Eastern Art")
        ]
        
        obra_data = {
            'objectID': 12345,
            'title': 'Test Artwork',
            'artistDisplayName': 'Test Artist',
            'artistNationality': 'American',
            'classification': 'Painting',
            'department': 'American Decorative Arts'
        }
        
        # Configurar mocks del cliente API
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.return_value = departamentos_mock
        mock_cliente_instance.obtener_obras_por_departamento.return_value = [12345]
        mock_cliente_instance.obtener_detalles_obra.return_value = obra_data
        
        # Configurar mock de interfaz
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
        mock_interfaz_instance.confirmar_accion.return_value = False
        
        # Configurar mock de visualizador
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador y ejecutar búsqueda
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor:
            mock_gestor_instance = Mock()
            mock_gestor.return_value = mock_gestor_instance
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_departamento()
            
            # Verificar que se llamaron los métodos correctos
            mock_cliente_instance.obtener_departamentos.assert_called_once()
            mock_interfaz_instance.solicitar_seleccion_departamento.assert_called_once()
            mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_integracion_manejo_errores_api(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de integración del manejo de errores de API"""
        # Configurar mock del cliente API para lanzar excepción
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        # Configurar mocks básicos
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador y ejecutar búsqueda
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor:
            mock_gestor_instance = Mock()
            mock_gestor.return_value = mock_gestor_instance
            
            controlador = ControladorPrincipal()
            controlador.procesar_busqueda_por_departamento()
            
            # Verificar que se mostró el mensaje de error apropiado
            mock_interfaz_instance.mostrar_mensaje_error.assert_called_with(
                "Error del servicio: Error de conexión"
            )
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    def test_integracion_gestor_nacionalidades_real(self, mock_visualizador, mock_interfaz):
        """Test de integración con gestor de nacionalidades real"""
        # Configurar mocks básicos
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador con archivo real de nacionalidades
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            # Crear instancia real del gestor con archivo de test
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            mock_gestor_class.return_value = gestor_real
            
            # Configurar mock del cliente API
            with patch('controlador_principal.ClienteAPIMetMuseum') as mock_cliente:
                mock_cliente_instance = Mock()
                mock_cliente.return_value = mock_cliente_instance
                mock_cliente_instance.buscar_obras_por_query.return_value = []
                
                controlador = ControladorPrincipal()
                
                # Cargar nacionalidades
                gestor_real.cargar_nacionalidades()
                
                # Configurar interfaz para seleccionar nacionalidad válida
                mock_interfaz_instance.solicitar_seleccion_nacionalidad.return_value = "American"
                mock_interfaz_instance.confirmar_accion.return_value = False
                
                # Ejecutar búsqueda por nacionalidad
                controlador.procesar_busqueda_por_nacionalidad()
                
                # Verificar que se procesó correctamente
                mock_interfaz_instance.mostrar_lista_obras.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_integracion_flujo_completo_con_imagen(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de integración del flujo completo incluyendo visualización de imagen"""
        # Configurar datos de prueba con imagen
        obra_data = {
            'objectID': 12345,
            'title': 'Test Artwork with Image',
            'artistDisplayName': 'Test Artist',
            'artistNationality': 'American',
            'classification': 'Painting',
            'primaryImage': 'http://example.com/image.jpg',
            'department': 'American Decorative Arts'
        }
        
        # Configurar mocks del cliente API
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_detalles_obra.return_value = obra_data
        
        # Configurar mock de interfaz para confirmar visualización de imagen
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_interfaz_instance.solicitar_id_obra.return_value = 12345
        mock_interfaz_instance.confirmar_accion.return_value = True
        
        # Configurar mock de visualizador
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador y ejecutar
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor:
            mock_gestor_instance = Mock()
            mock_gestor.return_value = mock_gestor_instance
            
            controlador = ControladorPrincipal()
            controlador.procesar_mostrar_detalles_obra()
            
            # Verificar que se mostró la imagen
            mock_visualizador_instance.mostrar_imagen_en_ventana.assert_called_once_with(
                'http://example.com/image.jpg',
                'Test Artwork with Image - Test Artist'
            )
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.ClienteAPIMetMuseum')
    def test_integracion_inicializar_recursos_completo(self, mock_cliente, mock_visualizador, mock_interfaz):
        """Test de integración de inicialización completa de recursos"""
        # Configurar mocks
        mock_cliente_instance = Mock()
        mock_cliente.return_value = mock_cliente_instance
        mock_cliente_instance.obtener_departamentos.return_value = [
            Departamento(1, "Test Department")
        ]
        
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador con gestor real
        with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
            gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
            mock_gestor_class.return_value = gestor_real
            
            controlador = ControladorPrincipal()
            
            # Ejecutar inicialización
            controlador._inicializar_recursos()
            
            # Verificar que se cargaron las nacionalidades
            self.assertTrue(gestor_real.archivo_cargado)
            self.assertEqual(len(gestor_real), 5)  # 5 nacionalidades en el archivo de test
            
            # Verificar que se verificó la API
            mock_cliente_instance.obtener_departamentos.assert_called_once()
    
    @patch('controlador_principal.InterfazUsuario')
    @patch('controlador_principal.VisualizadorImagenes')
    def test_integracion_servicios_reales(self, mock_visualizador, mock_interfaz):
        """Test de integración con servicios reales (sin mocks de servicios)"""
        # Configurar mocks básicos de UI
        mock_interfaz_instance = Mock()
        mock_interfaz.return_value = mock_interfaz_instance
        mock_visualizador_instance = Mock()
        mock_visualizador.return_value = mock_visualizador_instance
        
        # Crear controlador con servicios reales pero API mockeada
        with patch('controlador_principal.ClienteAPIMetMuseum') as mock_cliente_class:
            mock_cliente_instance = Mock()
            mock_cliente_class.return_value = mock_cliente_instance
            
            # Configurar respuestas de API
            mock_cliente_instance.obtener_departamentos.return_value = [
                Departamento(1, "American Decorative Arts")
            ]
            mock_cliente_instance.obtener_obras_por_departamento.return_value = [12345]
            mock_cliente_instance.obtener_detalles_obra.return_value = {
                'objectID': 12345,
                'title': 'Test Artwork',
                'artistDisplayName': 'Test Artist',
                'artistNationality': 'American'
            }
            
            with patch('controlador_principal.GestorNacionalidades') as mock_gestor_class:
                gestor_real = GestorNacionalidades(self.archivo_nacionalidades_test)
                gestor_real.cargar_nacionalidades()
                mock_gestor_class.return_value = gestor_real
                
                controlador = ControladorPrincipal()
                
                # Verificar que los servicios se crearon correctamente
                self.assertIsInstance(controlador._servicio_busqueda, ServicioBusqueda)
                self.assertIsInstance(controlador._servicio_obras, ServicioObras)
                
                # Configurar interfaz para búsqueda
                mock_interfaz_instance.solicitar_seleccion_departamento.return_value = 1
                mock_interfaz_instance.confirmar_accion.return_value = False
                
                # Ejecutar búsqueda (debería usar servicios reales)
                controlador.procesar_busqueda_por_departamento()
                
                # Verificar que se procesó correctamente
                mock_interfaz_instance.mostrar_lista_obras.assert_called_once()


if __name__ == '__main__':
    unittest.main()
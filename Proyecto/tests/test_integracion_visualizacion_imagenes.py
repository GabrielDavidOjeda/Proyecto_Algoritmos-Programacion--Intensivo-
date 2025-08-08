"""
Tests de integración para el flujo completo de visualización de imágenes.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.servicio_obras import ServicioObras
from services.cliente_api_met_museum import ClienteAPIMetMuseum
from ui.visualizador_imagenes import VisualizadorImagenes
from controlador_principal import ControladorPrincipal
from models.obra_arte import ObraArte
from models.artista import Artista


class TestIntegracionVisualizacionImagenes(unittest.TestCase):
    """Tests de integración para el flujo completo de visualización de imágenes."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear mocks
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_visualizador = Mock(spec=VisualizadorImagenes)
        
        # Crear servicio con dependencias mockeadas
        self.servicio_obras = ServicioObras(self.mock_cliente_api, self.mock_visualizador)
        
        # Datos de ejemplo
        self.datos_obra_con_imagen = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'primaryImage': 'https://images.metmuseum.org/test.jpg'
        }
        
        self.datos_obra_sin_imagen = {
            'objectID': 123456,
            'title': 'Obra Sin Imagen',
            'artistDisplayName': 'Artista Test'
        }
    
    def test_servicio_obras_integracion_con_visualizador(self):
        """Test de integración entre ServicioObras y VisualizadorImagenes."""
        # Configurar mock del cliente API
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_con_imagen
        
        # Obtener obra
        obra = self.servicio_obras.obtener_detalles_obra(436535)
        
        # Verificar que la obra tiene imagen
        self.assertTrue(obra.tiene_imagen())
        
        # Mostrar imagen usando el servicio integrado
        self.servicio_obras.mostrar_imagen_obra(obra)
        
        # Verificar que se llamó al visualizador con los parámetros correctos
        self.mock_visualizador.mostrar_imagen_en_ventana.assert_called_once_with(
            'https://images.metmuseum.org/test.jpg',
            'The Harvesters - Pieter Bruegel the Elder'
        )
    
    def test_servicio_obras_error_obra_sin_imagen(self):
        """Test de error al intentar mostrar imagen de obra sin imagen."""
        # Configurar mock del cliente API
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_sin_imagen
        
        # Obtener obra
        obra = self.servicio_obras.obtener_detalles_obra(123456)
        
        # Verificar que la obra no tiene imagen
        self.assertFalse(obra.tiene_imagen())
        
        # Intentar mostrar imagen debe lanzar error
        with self.assertRaises(ValueError) as context:
            self.servicio_obras.mostrar_imagen_obra(obra)
        
        self.assertIn("no tiene imagen disponible", str(context.exception))
        
        # Verificar que no se llamó al visualizador
        self.mock_visualizador.mostrar_imagen_en_ventana.assert_not_called()
    
    def test_servicio_obras_error_visualizador(self):
        """Test de manejo de error del visualizador."""
        # Configurar mock del cliente API
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_con_imagen
        
        # Configurar mock del visualizador para lanzar excepción
        self.mock_visualizador.mostrar_imagen_en_ventana.side_effect = \
            Exception("Error de visualización")
        
        # Obtener obra
        obra = self.servicio_obras.obtener_detalles_obra(436535)
        
        # Intentar mostrar imagen debe propagar el error
        with self.assertRaises(Exception) as context:
            self.servicio_obras.mostrar_imagen_obra(obra)
        
        self.assertIn("Error al mostrar imagen de la obra", str(context.exception))
    
    def test_servicio_obras_parametro_invalido(self):
        """Test de error con parámetro inválido."""
        with self.assertRaises(ValueError) as context:
            self.servicio_obras.mostrar_imagen_obra("no_es_obra")
        
        self.assertIn("ObraArte", str(context.exception))
    
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.GestorNacionalidades')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.InterfazUsuario')
    def test_controlador_flujo_completo_visualizacion(self, mock_interfaz_class, 
                                                    mock_visualizador_class,
                                                    mock_servicio_obras_class,
                                                    mock_servicio_busqueda_class,
                                                    mock_gestor_class, mock_cliente_class):
        """Test del flujo completo de visualización desde el controlador."""
        # Configurar mocks
        mock_cliente = Mock()
        mock_gestor = Mock()
        mock_servicio_busqueda = Mock()
        mock_servicio_obras = Mock()
        mock_visualizador = Mock()
        mock_interfaz = Mock()
        
        mock_cliente_class.return_value = mock_cliente
        mock_gestor_class.return_value = mock_gestor
        mock_servicio_busqueda_class.return_value = mock_servicio_busqueda
        mock_servicio_obras_class.return_value = mock_servicio_obras
        mock_visualizador_class.return_value = mock_visualizador
        mock_interfaz_class.return_value = mock_interfaz
        
        # Crear controlador
        controlador = ControladorPrincipal()
        
        # Crear obra de prueba con imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, 
                       url_imagen="https://example.com/image.jpg")
        
        # Configurar mock del servicio de obras para retornar la obra
        mock_servicio_obras.obtener_detalles_obra.return_value = obra
        
        # Configurar interfaz para confirmar visualización
        mock_interfaz.solicitar_id_obra.return_value = 12345
        mock_interfaz.confirmar_accion.return_value = True
        
        # Ejecutar método de procesamiento
        controlador.procesar_mostrar_detalles_obra()
        
        # Verificar que se solicitó el ID de la obra
        mock_interfaz.solicitar_id_obra.assert_called_once()
        
        # Verificar que se mostraron los detalles con opciones
        mock_interfaz.mostrar_detalles_obra_con_opciones.assert_called_once_with(obra)
        
        # Verificar que se confirmó la acción de mostrar imagen
        mock_interfaz.confirmar_accion.assert_called_with("¿Desea ver la imagen de la obra?")
        
        # Verificar que se mostró mensaje de éxito
        mock_interfaz.mostrar_mensaje_exito.assert_called_with("Imagen mostrada correctamente")
    
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.GestorNacionalidades')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.InterfazUsuario')
    def test_controlador_flujo_obra_sin_imagen(self, mock_interfaz_class, 
                                             mock_visualizador_class,
                                             mock_servicio_obras_class,
                                             mock_servicio_busqueda_class,
                                             mock_gestor_class, mock_cliente_class):
        """Test del flujo cuando la obra no tiene imagen."""
        # Configurar mocks
        mock_cliente = Mock()
        mock_gestor = Mock()
        mock_servicio_busqueda = Mock()
        mock_servicio_obras = Mock()
        mock_visualizador = Mock()
        mock_interfaz = Mock()
        
        mock_cliente_class.return_value = mock_cliente
        mock_gestor_class.return_value = mock_gestor
        mock_servicio_busqueda_class.return_value = mock_servicio_busqueda
        mock_servicio_obras_class.return_value = mock_servicio_obras
        mock_visualizador_class.return_value = mock_visualizador
        mock_interfaz_class.return_value = mock_interfaz
        
        # Crear controlador
        controlador = ControladorPrincipal()
        
        # Crear obra de prueba sin imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista)  # Sin URL de imagen
        
        # Configurar mock del servicio de obras
        mock_servicio_obras.obtener_detalles_obra.return_value = obra
        
        # Configurar interfaz
        mock_interfaz.solicitar_id_obra.return_value = 12345
        
        # Ejecutar método de procesamiento
        controlador.procesar_mostrar_detalles_obra()
        
        # Verificar que se mostraron los detalles
        mock_interfaz.mostrar_detalles_obra_con_opciones.assert_called_once_with(obra)
        
        # Verificar que NO se ofreció mostrar imagen (porque no tiene)
        mock_interfaz.confirmar_accion.assert_not_called()
    
    @patch('controlador_principal.ClienteAPIMetMuseum')
    @patch('controlador_principal.GestorNacionalidades')
    @patch('controlador_principal.ServicioBusqueda')
    @patch('controlador_principal.ServicioObras')
    @patch('controlador_principal.VisualizadorImagenes')
    @patch('controlador_principal.InterfazUsuario')
    def test_controlador_error_visualizacion(self, mock_interfaz_class, 
                                           mock_visualizador_class,
                                           mock_servicio_obras_class,
                                           mock_servicio_busqueda_class,
                                           mock_gestor_class, mock_cliente_class):
        """Test del manejo de errores en visualización desde el controlador."""
        # Configurar mocks
        mock_cliente = Mock()
        mock_gestor = Mock()
        mock_servicio_busqueda = Mock()
        mock_servicio_obras = Mock()
        mock_visualizador = Mock()
        mock_interfaz = Mock()
        
        mock_cliente_class.return_value = mock_cliente
        mock_gestor_class.return_value = mock_gestor
        mock_servicio_busqueda_class.return_value = mock_servicio_busqueda
        mock_servicio_obras_class.return_value = mock_servicio_obras
        mock_visualizador_class.return_value = mock_visualizador
        mock_interfaz_class.return_value = mock_interfaz
        
        # Crear controlador
        controlador = ControladorPrincipal()
        
        # Crear obra de prueba con imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, 
                       url_imagen="https://example.com/image.jpg")
        
        # Configurar mock del servicio de obras para lanzar excepción
        mock_servicio_obras.obtener_detalles_obra.return_value = obra
        mock_servicio_obras.mostrar_imagen_obra.side_effect = Exception("Error de visualización")
        
        # Configurar interfaz
        mock_interfaz.solicitar_id_obra.return_value = 12345
        mock_interfaz.confirmar_accion.return_value = True
        
        # Ejecutar método de procesamiento
        controlador.procesar_mostrar_detalles_obra()
        
        # Verificar que se mostró mensaje de error
        mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Error al mostrar imagen: Error de visualización"
        )
    
    def test_integracion_completa_con_datos_reales(self):
        """Test de integración completa con estructura de datos real."""
        # Crear instancias reales (sin mocks para el flujo principal)
        cliente_api = Mock(spec=ClienteAPIMetMuseum)
        visualizador = Mock(spec=VisualizadorImagenes)
        servicio = ServicioObras(cliente_api, visualizador)
        
        # Datos que simulan respuesta real de la API
        datos_api_reales = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'artistBeginDate': '1525',
            'artistEndDate': '1569',
            'classification': 'Paintings',
            'objectDate': '1565',
            'primaryImage': 'https://images.metmuseum.org/CRDImages/ep/original/DT1567.jpg',
            'department': 'European Paintings'
        }
        
        # Configurar mock del cliente API
        cliente_api.obtener_detalles_obra.return_value = datos_api_reales
        
        # Flujo completo: obtener obra y mostrar imagen
        obra = servicio.obtener_detalles_obra(436535)
        
        # Verificar que la obra se creó correctamente
        self.assertEqual(obra.id_obra, 436535)
        self.assertEqual(obra.titulo, 'The Harvesters')
        self.assertEqual(obra.artista.nombre, 'Pieter Bruegel the Elder')
        self.assertTrue(obra.tiene_imagen())
        
        # Mostrar imagen
        servicio.mostrar_imagen_obra(obra)
        
        # Verificar que se llamó al visualizador con los datos correctos
        visualizador.mostrar_imagen_en_ventana.assert_called_once_with(
            'https://images.metmuseum.org/CRDImages/ep/original/DT1567.jpg',
            'The Harvesters - Pieter Bruegel the Elder'
        )


if __name__ == '__main__':
    unittest.main()
"""
Tests de integración para ServicioObras con ClienteAPIMetMuseum.
"""

import unittest
from unittest.mock import patch, Mock
import requests
from services.servicio_obras import ServicioObras
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from models.obra_arte import ObraArte


class TestIntegracionServicioObras(unittest.TestCase):
    """Tests de integración para ServicioObras"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.cliente_api = ClienteAPIMetMuseum()
        self.servicio = ServicioObras(self.cliente_api)
    
    @patch('requests.Session.get')
    def test_integracion_obtener_detalles_obra_exitoso(self, mock_get):
        """Test: Integración exitosa para obtener detalles de obra"""
        # Simular respuesta de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'artistBeginDate': '1525',
            'artistEndDate': '1569',
            'classification': 'Paintings',
            'objectDate': '1565',
            'primaryImage': 'https://images.metmuseum.org/test.jpg',
            'department': 'European Paintings'
        }
        mock_get.return_value = mock_response
        
        # Ejecutar
        resultado = self.servicio.obtener_detalles_obra(436535)
        
        # Verificar
        self.assertIsInstance(resultado, ObraArte)
        self.assertEqual(resultado.id_obra, 436535)
        self.assertEqual(resultado.titulo, 'The Harvesters')
        self.assertEqual(resultado.artista.nombre, 'Pieter Bruegel the Elder')
        self.assertEqual(resultado.artista.nacionalidad, 'Netherlandish')
        
        # Verificar que se hizo la llamada correcta a la API
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn('/objects/436535', args[0])
    
    @patch('requests.Session.get')
    def test_integracion_obra_no_encontrada(self, mock_get):
        """Test: Integración cuando la obra no existe"""
        # Simular respuesta 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Verificar que se lanza la excepción correcta
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado):
            self.servicio.obtener_detalles_obra(999999)
    
    @patch('requests.Session.get')
    def test_integracion_error_conexion(self, mock_get):
        """Test: Integración con error de conexión"""
        # Simular error de conexión
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        # Verificar que se lanza la excepción correcta
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorConexionAPI):
            self.servicio.obtener_detalles_obra(436535)
    
    @patch('requests.Session.get')
    def test_integracion_datos_api_incompletos(self, mock_get):
        """Test: Integración con datos incompletos de la API"""
        # Simular respuesta con datos incompletos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'objectID': 123456
            # Falta 'title' que es obligatorio
        }
        mock_get.return_value = mock_response
        
        # Verificar que se lanza la excepción correcta
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos):
            self.servicio.obtener_detalles_obra(123456)
    
    @patch('requests.Session.get')
    def test_integracion_formateo_completo(self, mock_get):
        """Test: Integración completa incluyendo formateo"""
        # Simular respuesta de la API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'artistBeginDate': '1525',
            'artistEndDate': '1569',
            'classification': 'Paintings',
            'objectDate': '1565',
            'primaryImage': 'https://images.metmuseum.org/test.jpg',
            'department': 'European Paintings'
        }
        mock_get.return_value = mock_response
        
        # Obtener obra y formatear
        obra = self.servicio.obtener_detalles_obra(436535)
        detalles_formateados = self.servicio.formatear_detalles_completos(obra)
        
        # Verificar formateo
        self.assertIn("DETALLES DE LA OBRA", detalles_formateados)
        self.assertIn("The Harvesters", detalles_formateados)
        self.assertIn("Pieter Bruegel the Elder", detalles_formateados)
        self.assertIn("Netherlandish", detalles_formateados)
        self.assertIn("1525-1569", detalles_formateados)
        self.assertIn("Paintings", detalles_formateados)
        self.assertIn("1565", detalles_formateados)
        self.assertIn("European Paintings", detalles_formateados)
        self.assertIn("Imagen: Disponible", detalles_formateados)


if __name__ == '__main__':
    unittest.main()
"""
Tests para el cliente API del Metropolitan Museum of Art
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from models.departamento import Departamento


class TestClienteAPIMetMuseum:
    """Tests para la clase ClienteAPIMetMuseum"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()


class TestObtenerDepartamentos:
    """Tests para el método obtener_departamentos"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_departamentos_exitoso(self, mock_get):
        """Test de obtención exitosa de departamentos"""
        # Configurar mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "departments": [
                {"departmentId": 1, "displayName": "American Decorative Arts"},
                {"departmentId": 3, "displayName": "Ancient Near Eastern Art"},
                {"departmentId": 4, "displayName": "Arms and Armor"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Ejecutar
        departamentos = self.cliente.obtener_departamentos()
        
        # Verificar
        assert len(departamentos) == 3
        assert all(isinstance(dept, Departamento) for dept in departamentos)
        assert departamentos[0].id_departamento == 1
        assert departamentos[0].nombre == "American Decorative Arts"
        assert departamentos[1].id_departamento == 3
        assert departamentos[1].nombre == "Ancient Near Eastern Art"
        
        # Verificar que se hizo la llamada correcta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/departments" in args[0]
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_departamentos_respuesta_vacia(self, mock_get):
        """Test cuando la API retorna lista vacía"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"departments": []}
        mock_get.return_value = mock_response
        
        departamentos = self.cliente.obtener_departamentos()
        
        assert len(departamentos) == 0
        assert isinstance(departamentos, list)
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_departamentos_datos_incompletos(self, mock_get):
        """Test cuando algunos departamentos tienen datos incompletos"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "departments": [
                {"departmentId": 1, "displayName": "American Decorative Arts"},
                {"departmentId": 2},  # Sin displayName
                {"displayName": "Ancient Near Eastern Art"},  # Sin departmentId
                {"departmentId": 4, "displayName": "Arms and Armor"}
            ]
        }
        mock_get.return_value = mock_response
        
        departamentos = self.cliente.obtener_departamentos()
        
        # Solo deben incluirse los departamentos con datos completos
        assert len(departamentos) == 2
        assert departamentos[0].id_departamento == 1
        assert departamentos[1].id_departamento == 4
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_departamentos_sin_campo_departments(self, mock_get):
        """Test cuando la respuesta no tiene el campo 'departments'"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"total": 0}
        mock_get.return_value = mock_response
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos) as exc_info:
            self.cliente.obtener_departamentos()
        
        assert "no contiene la lista de departamentos" in str(exc_info.value)
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_departamentos_error_conexion(self, mock_get):
        """Test de manejo de errores de conexión"""
        mock_get.side_effect = requests.ConnectionError("Error de conexión")
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorConexionAPI) as exc_info:
            self.cliente.obtener_departamentos()
        
        assert "Error de conexión después de 3 intentos" in str(exc_info.value)


class TestObtenerDetallesObra:
    """Tests para el método obtener_detalles_obra"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_detalles_obra_exitoso(self, mock_get):
        """Test de obtención exitosa de detalles de obra"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objectID": 436535,
            "title": "The Harvesters",
            "artistDisplayName": "Pieter Bruegel the Elder",
            "artistNationality": "Netherlandish",
            "artistBeginDate": "1525",
            "artistEndDate": "1569",
            "classification": "Paintings",
            "objectDate": "1565",
            "primaryImage": "https://images.metmuseum.org/test.jpg",
            "department": "European Paintings"
        }
        mock_get.return_value = mock_response
        
        detalles = self.cliente.obtener_detalles_obra(436535)
        
        assert detalles["objectID"] == 436535
        assert detalles["title"] == "The Harvesters"
        assert detalles["artistDisplayName"] == "Pieter Bruegel the Elder"
        
        # Verificar llamada correcta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/objects/436535" in args[0]
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_detalles_obra_sin_titulo(self, mock_get):
        """Test cuando la obra no tiene título"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objectID": 436535,
            "title": None,  # Título nulo
            "artistDisplayName": "Test Artist"
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos) as exc_info:
            self.cliente.obtener_detalles_obra(436535)
        
        assert "Campo requerido 'title' faltante o nulo" in str(exc_info.value)
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_detalles_obra_id_no_coincide(self, mock_get):
        """Test cuando el ID de la respuesta no coincide con el solicitado"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objectID": 999999,  # ID diferente al solicitado
            "title": "Test Title"
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos) as exc_info:
            self.cliente.obtener_detalles_obra(436535)
        
        assert "ID de obra no coincide" in str(exc_info.value)
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_detalles_obra_no_encontrada(self, mock_get):
        """Test cuando la obra no existe (404)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado) as exc_info:
            self.cliente.obtener_detalles_obra(999999)
        
        assert "no encontrado" in str(exc_info.value)


class TestBuscarObrasPorQuery:
    """Tests para el método buscar_obras_por_query"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_buscar_obras_por_query_exitoso(self, mock_get):
        """Test de búsqueda exitosa por query"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 3,
            "objectIDs": [436535, 459055, 437853]
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.buscar_obras_por_query("sunflowers")
        
        assert len(ids) == 3
        assert ids == [436535, 459055, 437853]
        
        # Verificar llamada correcta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/search" in args[0]
        assert kwargs['params']['q'] == "sunflowers"
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_buscar_obras_por_query_con_departamento(self, mock_get):
        """Test de búsqueda con filtro de departamento"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 2,
            "objectIDs": [436535, 459055]
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.buscar_obras_por_query("sunflowers", departamento_id=11)
        
        assert len(ids) == 2
        
        # Verificar que se incluyó el departamento en los parámetros
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['q'] == "sunflowers"
        assert kwargs['params']['departmentId'] == 11
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_buscar_obras_por_query_sin_resultados(self, mock_get):
        """Test cuando no hay resultados"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 0,
            "objectIDs": None
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.buscar_obras_por_query("nonexistent")
        
        assert len(ids) == 0
        assert isinstance(ids, list)
    
    def test_buscar_obras_por_query_vacia(self):
        """Test con query vacía"""
        ids = self.cliente.buscar_obras_por_query("")
        assert len(ids) == 0
        
        ids = self.cliente.buscar_obras_por_query("   ")
        assert len(ids) == 0
        
        ids = self.cliente.buscar_obras_por_query(None)
        assert len(ids) == 0
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_buscar_obras_por_query_ids_invalidos(self, mock_get):
        """Test con IDs inválidos en la respuesta"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 5,
            "objectIDs": [436535, "invalid", -1, 0, 459055, None]
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.buscar_obras_por_query("test")
        
        # Solo deben incluirse los IDs válidos (enteros positivos)
        assert len(ids) == 2
        assert ids == [436535, 459055]


class TestObtenerObrasPorDepartamento:
    """Tests para el método obtener_obras_por_departamento"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_obras_por_departamento_exitoso(self, mock_get):
        """Test de obtención exitosa de obras por departamento"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 3,
            "objectIDs": [436535, 459055, 437853]
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.obtener_obras_por_departamento(11)
        
        assert len(ids) == 3
        assert ids == [436535, 459055, 437853]
        
        # Verificar llamada correcta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/objects" in args[0]
        assert kwargs['params']['departmentIds'] == 11
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_obtener_obras_por_departamento_vacio(self, mock_get):
        """Test cuando el departamento no tiene obras"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 0,
            "objectIDs": None
        }
        mock_get.return_value = mock_response
        
        ids = self.cliente.obtener_obras_por_departamento(999)
        
        assert len(ids) == 0
        assert isinstance(ids, list)


class TestRealizarPeticion:
    """Tests para el método _realizar_peticion"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_realizar_peticion_exitosa(self, mock_get):
        """Test de petición exitosa"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        resultado = self.cliente._realizar_peticion("/test")
        
        assert resultado == {"test": "data"}
        mock_get.assert_called_once()
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_realizar_peticion_con_parametros(self, mock_get):
        """Test de petición con parámetros"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        params = {"q": "test", "limit": 10}
        resultado = self.cliente._realizar_peticion("/test", params=params)
        
        assert resultado == {"test": "data"}
        args, kwargs = mock_get.call_args
        assert kwargs['params'] == params
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_realizar_peticion_json_invalido(self, mock_get):
        """Test cuando la respuesta no es JSON válido"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos) as exc_info:
            self.cliente._realizar_peticion("/test")
        
        assert "Respuesta no es JSON válido" in str(exc_info.value)
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    @patch('time.sleep')  # Mock sleep para acelerar tests
    def test_realizar_peticion_reintentos(self, mock_sleep, mock_get):
        """Test de reintentos en caso de error de conexión"""
        # Configurar para fallar 2 veces y luego tener éxito
        mock_get.side_effect = [
            requests.ConnectionError("Connection failed"),
            requests.ConnectionError("Connection failed"),
            Mock(status_code=200, json=lambda: {"success": True})
        ]
        
        resultado = self.cliente._realizar_peticion("/test")
        
        assert resultado == {"success": True}
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2  # Se durmió entre reintentos
    
    @patch('services.cliente_api_met_museum.requests.Session.get')
    def test_realizar_peticion_max_reintentos_excedido(self, mock_get):
        """Test cuando se exceden los reintentos máximos"""
        mock_get.side_effect = requests.ConnectionError("Connection failed")
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorConexionAPI) as exc_info:
            self.cliente._realizar_peticion("/test")
        
        assert "después de 3 intentos" in str(exc_info.value)
        assert mock_get.call_count == 3


class TestManejarErroresAPI:
    """Tests para el método _manejar_errores_api"""
    
    def setup_method(self):
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    def test_manejar_errores_api_200_ok(self):
        """Test con respuesta exitosa (200)"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        # No debe lanzar excepción
        self.cliente._manejar_errores_api(mock_response)
    
    def test_manejar_errores_api_404_not_found(self):
        """Test con error 404"""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado):
            self.cliente._manejar_errores_api(mock_response)
    
    def test_manejar_errores_api_429_rate_limit(self):
        """Test con error 429 (rate limit)"""
        mock_response = Mock()
        mock_response.status_code = 429
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorRateLimitAPI) as exc_info:
            self.cliente._manejar_errores_api(mock_response)
        
        assert "Límite de velocidad" in str(exc_info.value)
    
    def test_manejar_errores_api_500_server_error(self):
        """Test con error del servidor (500)"""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorConexionAPI) as exc_info:
            self.cliente._manejar_errores_api(mock_response)
        
        assert "Error del servidor" in str(exc_info.value)
    
    def test_manejar_errores_api_400_client_error(self):
        """Test con error del cliente (400)"""
        mock_response = Mock()
        mock_response.status_code = 400
        
        with pytest.raises(ExcepcionesAPIMetMuseum.ErrorConexionAPI) as exc_info:
            self.cliente._manejar_errores_api(mock_response)
        
        assert "Error del cliente" in str(exc_info.value)


class TestExcepcionesAPIMetMuseum:
    """Tests para las excepciones personalizadas"""
    
    def test_jerarquia_excepciones(self):
        """Test de la jerarquía de excepciones"""
        # Verificar que todas las excepciones heredan de ErrorAPIMetMuseum
        assert issubclass(ExcepcionesAPIMetMuseum.ErrorConexionAPI, 
                         ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)
        assert issubclass(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos, 
                         ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)
        assert issubclass(ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado, 
                         ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)
        assert issubclass(ExcepcionesAPIMetMuseum.ErrorRateLimitAPI, 
                         ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)
    
    def test_crear_excepciones_con_mensaje(self):
        """Test de creación de excepciones con mensajes personalizados"""
        mensaje = "Test error message"
        
        exc = ExcepcionesAPIMetMuseum.ErrorConexionAPI(mensaje)
        assert str(exc) == mensaje
        
        exc = ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(mensaje)
        assert str(exc) == mensaje
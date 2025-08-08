"""
Tests unitarios para el servicio de búsqueda del sistema de catálogo del museo.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from services.servicio_busqueda import ServicioBusqueda, ExcepcionesServicioBusqueda
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from utils.gestor_nacionalidades import GestorNacionalidades
from models.artista import Artista
from models.obra_arte import ObraArte
from models.departamento import Departamento


class TestServicioBusqueda(unittest.TestCase):
    """Tests para la clase ServicioBusqueda"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        
        # Datos de ejemplo para tests
        self.datos_obra_ejemplo = {
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
        
        self.departamento_ejemplo = Departamento(1, "European Paintings")
    
    def test_inicializacion_exitosa(self):
        """Test de inicialización correcta del servicio"""
        servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        self.assertIsInstance(servicio, ServicioBusqueda)
    
    def test_inicializacion_cliente_api_invalido(self):
        """Test de inicialización con cliente API inválido"""
        with self.assertRaises(ValueError) as context:
            ServicioBusqueda("no_es_cliente", self.mock_gestor_nacionalidades)
        
        self.assertIn("ClienteAPIMetMuseum", str(context.exception))
    
    def test_inicializacion_gestor_nacionalidades_invalido(self):
        """Test de inicialización con gestor de nacionalidades inválido"""
        with self.assertRaises(ValueError) as context:
            ServicioBusqueda(self.mock_cliente_api, "no_es_gestor")
        
        self.assertIn("GestorNacionalidades", str(context.exception))


class TestBuscarPorDepartamento(unittest.TestCase):
    """Tests para el método buscar_por_departamento"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        
        self.datos_obra_ejemplo = {
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
    
    def test_busqueda_exitosa_con_obras(self):
        """Test de búsqueda exitosa que retorna obras"""
        # Configurar mocks
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = [436535, 436536]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_ejemplo
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_departamento(1)
        
        # Verificar resultados
        self.assertEqual(len(resultado), 2)
        self.assertIsInstance(resultado[0], ObraArte)
        self.assertEqual(resultado[0].id_obra, 436535)
        self.assertEqual(resultado[0].titulo, 'The Harvesters')
        
        # Verificar llamadas a mocks
        self.mock_cliente_api.obtener_obras_por_departamento.assert_called_once_with(1)
        self.assertEqual(self.mock_cliente_api.obtener_detalles_obra.call_count, 2)
    
    def test_busqueda_sin_obras(self):
        """Test de búsqueda que no retorna obras"""
        # Configurar mock para retornar lista vacía
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = []
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_departamento(1)
        
        # Verificar resultado vacío
        self.assertEqual(len(resultado), 0)
        self.mock_cliente_api.obtener_obras_por_departamento.assert_called_once_with(1)
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
    
    def test_id_departamento_invalido_negativo(self):
        """Test con ID de departamento negativo"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido) as context:
            self.servicio.buscar_por_departamento(-1)
        
        self.assertIn("inválido", str(context.exception))
        self.mock_cliente_api.obtener_obras_por_departamento.assert_not_called()
    
    def test_id_departamento_invalido_cero(self):
        """Test con ID de departamento cero"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido):
            self.servicio.buscar_por_departamento(0)
    
    def test_id_departamento_invalido_no_entero(self):
        """Test con ID de departamento que no es entero"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido):
            self.servicio.buscar_por_departamento("1")
    
    def test_departamento_no_encontrado(self):
        """Test cuando el departamento no existe en la API"""
        # Configurar mock para lanzar excepción de recurso no encontrado
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Departamento no encontrado")
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido) as context:
            self.servicio.buscar_por_departamento(999)
        
        self.assertIn("no encontrado", str(context.exception))
    
    def test_error_conexion_api(self):
        """Test cuando hay error de conexión con la API"""
        # Configurar mock para lanzar excepción de conexión
        self.mock_cliente_api.obtener_obras_por_departamento.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_departamento(1)
        
        self.assertIn("Error al buscar obras", str(context.exception))
    
    def test_limitacion_obras_procesadas(self):
        """Test que verifica la limitación de obras procesadas"""
        # Configurar mock para retornar muchas obras
        ids_obras = list(range(1, 51))  # 50 obras
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = ids_obras
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_ejemplo
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_departamento(1)
        
        # Verificar que solo se procesaron 20 obras (límite)
        self.assertEqual(len(resultado), 20)
        self.assertEqual(self.mock_cliente_api.obtener_detalles_obra.call_count, 20)
    
    def test_manejo_errores_conversion_individual(self):
        """Test del manejo de errores en conversión de obras individuales"""
        # Configurar mocks
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = [1, 2, 3]
        
        # Primera obra exitosa, segunda con error, tercera exitosa
        def side_effect(id_obra):
            if id_obra == 2:
                raise Exception("Error de conversión")
            return self.datos_obra_ejemplo
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_departamento(1)
        
        # Verificar que se procesaron solo las obras exitosas
        self.assertEqual(len(resultado), 2)
    
    def test_demasiados_errores_conversion(self):
        """Test cuando hay demasiados errores de conversión"""
        # Configurar mocks para que todas las conversiones fallen
        self.mock_cliente_api.obtener_obras_por_departamento.return_value = [1, 2, 3, 4]
        self.mock_cliente_api.obtener_detalles_obra.side_effect = Exception("Error de conversión")
        
        # Ejecutar búsqueda y verificar excepción
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorConversionDatos) as context:
            self.servicio.buscar_por_departamento(1)
        
        self.assertIn("Demasiados errores", str(context.exception))


class TestObtenerDepartamentosDisponibles(unittest.TestCase):
    """Tests para el método obtener_departamentos_disponibles"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
    
    def test_obtener_departamentos_exitoso(self):
        """Test de obtención exitosa de departamentos"""
        # Configurar mock
        departamentos_mock = [
            Departamento(3, "Ancient Near Eastern Art"),
            Departamento(1, "American Decorative Arts"),
            Departamento(2, "Arms and Armor")
        ]
        self.mock_cliente_api.obtener_departamentos.return_value = departamentos_mock
        
        # Ejecutar método
        resultado = self.servicio.obtener_departamentos_disponibles()
        
        # Verificar resultados (deben estar ordenados por nombre)
        self.assertEqual(len(resultado), 3)
        self.assertEqual(resultado[0].nombre, "American Decorative Arts")
        self.assertEqual(resultado[1].nombre, "Ancient Near Eastern Art")
        self.assertEqual(resultado[2].nombre, "Arms and Armor")
        
        # Verificar llamada al mock
        self.mock_cliente_api.obtener_departamentos.assert_called_once()
    
    def test_error_api_obtener_departamentos(self):
        """Test cuando hay error de API al obtener departamentos"""
        # Configurar mock para lanzar excepción
        self.mock_cliente_api.obtener_departamentos.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        # Ejecutar y verificar excepción
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.obtener_departamentos_disponibles()
        
        self.assertIn("Error al obtener departamentos", str(context.exception))


class TestConvertirDatosAPIAObra(unittest.TestCase):
    """Tests para el método _convertir_datos_api_a_obra"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        
        self.datos_completos = {
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
    
    def test_conversion_datos_completos(self):
        """Test de conversión con datos completos"""
        obra = self.servicio._convertir_datos_api_a_obra(self.datos_completos)
        
        # Verificar obra
        self.assertIsInstance(obra, ObraArte)
        self.assertEqual(obra.id_obra, 436535)
        self.assertEqual(obra.titulo, 'The Harvesters')
        self.assertEqual(obra.clasificacion, 'Paintings')
        self.assertEqual(obra.fecha_creacion, '1565')
        self.assertEqual(obra.url_imagen, 'https://images.metmuseum.org/test.jpg')
        self.assertEqual(obra.departamento, 'European Paintings')
        
        # Verificar artista
        self.assertEqual(obra.artista.nombre, 'Pieter Bruegel the Elder')
        self.assertEqual(obra.artista.nacionalidad, 'Netherlandish')
        self.assertEqual(obra.artista.fecha_nacimiento, '1525')
        self.assertEqual(obra.artista.fecha_muerte, '1569')
    
    def test_conversion_datos_minimos(self):
        """Test de conversión con datos mínimos requeridos"""
        datos_minimos = {
            'objectID': 123,
            'title': 'Obra de prueba'
        }
        
        obra = self.servicio._convertir_datos_api_a_obra(datos_minimos)
        
        # Verificar obra
        self.assertEqual(obra.id_obra, 123)
        self.assertEqual(obra.titulo, 'Obra de prueba')
        self.assertEqual(obra.artista.nombre, 'Artista desconocido')
        self.assertIsNone(obra.clasificacion)
        self.assertIsNone(obra.url_imagen)
    
    def test_conversion_titulo_nulo(self):
        """Test de conversión cuando el título es nulo"""
        datos_titulo_nulo = {
            'objectID': 123,
            'title': None
        }
        
        obra = self.servicio._convertir_datos_api_a_obra(datos_titulo_nulo)
        self.assertEqual(obra.titulo, 'Título desconocido')
    
    def test_conversion_url_imagen_vacia(self):
        """Test de conversión con URL de imagen vacía"""
        datos_imagen_vacia = {
            'objectID': 123,
            'title': 'Test',
            'primaryImage': '   '  # Solo espacios
        }
        
        obra = self.servicio._convertir_datos_api_a_obra(datos_imagen_vacia)
        self.assertIsNone(obra.url_imagen)
    
    def test_conversion_sin_object_id(self):
        """Test de conversión sin objectID"""
        datos_sin_id = {
            'title': 'Test'
        }
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorConversionDatos) as context:
            self.servicio._convertir_datos_api_a_obra(datos_sin_id)
        
        self.assertIn("objectID", str(context.exception))
    
    def test_conversion_sin_titulo(self):
        """Test de conversión sin título"""
        datos_sin_titulo = {
            'objectID': 123
        }
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorConversionDatos) as context:
            self.servicio._convertir_datos_api_a_obra(datos_sin_titulo)
        
        self.assertIn("title", str(context.exception))
    
    def test_conversion_datos_invalidos(self):
        """Test de conversión con datos inválidos que causan ValueError"""
        datos_invalidos = {
            'objectID': 'no_es_entero',  # Debería ser entero
            'title': 'Test'
        }
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorConversionDatos):
            self.servicio._convertir_datos_api_a_obra(datos_invalidos)


class TestBuscarPorNacionalidad(unittest.TestCase):
    """Tests para el método buscar_por_nacionalidad"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        
        self.datos_obra_ejemplo = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'artistBeginDate': '1525',
            'artistEndDate': '1569'
        }
        
        self.datos_obra_sin_nacionalidad = {
            'objectID': 436536,
            'title': 'Unknown Work',
            'artistDisplayName': 'Unknown Artist',
            'artistNationality': None
        }
        
        self.datos_obra_nacionalidad_diferente = {
            'objectID': 436537,
            'title': 'French Work',
            'artistDisplayName': 'French Artist',
            'artistNationality': 'French'
        }
    
    def test_busqueda_nacionalidad_exitosa(self):
        """Test de búsqueda exitosa por nacionalidad"""
        # Configurar mocks
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_ejemplo
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nacionalidad("Netherlandish")
        
        # Verificar resultados
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].artista.nacionalidad, "Netherlandish")
        
        # Verificar llamadas
        self.mock_gestor_nacionalidades.validar_nacionalidad.assert_called_once_with("Netherlandish")
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Netherlandish")
    
    def test_busqueda_nacionalidad_sin_resultados(self):
        """Test de búsqueda por nacionalidad que no retorna obras"""
        # Configurar mocks
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = []
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nacionalidad("Inexistente")
        
        # Verificar resultado vacío
        self.assertEqual(len(resultado), 0)
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
    
    def test_filtrado_por_nacionalidad_exacta(self):
        """Test que verifica el filtrado por nacionalidad exacta del artista"""
        # Configurar mocks para retornar obras con diferentes nacionalidades
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535, 436536, 436537]
        
        def side_effect(id_obra):
            if id_obra == 436535:
                return self.datos_obra_ejemplo  # Netherlandish
            elif id_obra == 436536:
                return self.datos_obra_sin_nacionalidad  # Sin nacionalidad
            else:
                return self.datos_obra_nacionalidad_diferente  # French
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda por "Netherlandish"
        resultado = self.servicio.buscar_por_nacionalidad("Netherlandish")
        
        # Verificar que solo se retorna la obra con nacionalidad coincidente
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].artista.nacionalidad, "Netherlandish")
    
    def test_busqueda_nacionalidad_coincidencia_parcial(self):
        """Test de búsqueda con coincidencia parcial en nacionalidad"""
        # Configurar datos con nacionalidad que contiene la búsqueda
        datos_obra_american = {
            'objectID': 436538,
            'title': 'American Work',
            'artistDisplayName': 'American Artist',
            'artistNationality': 'American, New York'  # Contiene "American"
        }
        
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436538]
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_obra_american
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nacionalidad("American")
        
        # Verificar que encuentra la obra con coincidencia parcial
        self.assertEqual(len(resultado), 1)
        self.assertIn("American", resultado[0].artista.nacionalidad)
    
    def test_manejo_errores_conversion_individual_nacionalidad(self):
        """Test del manejo de errores en conversión de obras individuales para búsqueda por nacionalidad"""
        # Configurar mocks
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = [1, 2, 3]
        
        # Primera obra exitosa, segunda con error, tercera exitosa
        def side_effect(id_obra):
            if id_obra == 2:
                raise Exception("Error de conversión")
            return self.datos_obra_ejemplo
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nacionalidad("Netherlandish")
        
        # Verificar que se procesaron solo las obras exitosas
        self.assertEqual(len(resultado), 2)
    
    def test_limitacion_obras_procesadas_nacionalidad(self):
        """Test que verifica la limitación de obras procesadas en búsqueda por nacionalidad"""
        # Configurar mock para retornar muchas obras
        ids_obras = list(range(1, 51))  # 50 obras
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = ids_obras
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_ejemplo
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nacionalidad("Netherlandish")
        
        # Verificar que solo se procesaron 30 obras (límite para nacionalidad)
        self.assertEqual(len(resultado), 30)
        self.assertEqual(self.mock_cliente_api.obtener_detalles_obra.call_count, 30)
    
    def test_nacionalidad_con_espacios(self):
        """Test con nacionalidad que tiene espacios al inicio y final"""
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = []
        
        # Ejecutar búsqueda con espacios
        resultado = self.servicio.buscar_por_nacionalidad("  Netherlandish  ")
        
        # Verificar que se limpia la nacionalidad antes de validar
        self.mock_gestor_nacionalidades.validar_nacionalidad.assert_called_once_with("Netherlandish")
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Netherlandish")
    
    def test_nacionalidad_invalida_vacia(self):
        """Test con nacionalidad vacía"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida):
            self.servicio.buscar_por_nacionalidad("")
    
    def test_nacionalidad_invalida_solo_espacios(self):
        """Test con nacionalidad que solo contiene espacios"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida):
            self.servicio.buscar_por_nacionalidad("   ")
    
    def test_nacionalidad_invalida_none(self):
        """Test con nacionalidad None"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida):
            self.servicio.buscar_por_nacionalidad(None)
    
    def test_nacionalidad_invalida_no_string(self):
        """Test con nacionalidad que no es string"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida):
            self.servicio.buscar_por_nacionalidad(123)
    
    def test_nacionalidad_no_en_lista(self):
        """Test con nacionalidad no válida según el gestor"""
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = False
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida) as context:
            self.servicio.buscar_por_nacionalidad("NoExiste")
        
        self.assertIn("no encontrada", str(context.exception))
    
    def test_error_api_busqueda_nacionalidad(self):
        """Test cuando hay error de API al buscar por nacionalidad"""
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_nacionalidad("Netherlandish")
        
        self.assertIn("Error al buscar obras por nacionalidad", str(context.exception))
    
    def test_integracion_gestor_nacionalidades(self):
        """Test que verifica la integración correcta con el gestor de nacionalidades"""
        # Configurar mock del gestor
        self.mock_gestor_nacionalidades.validar_nacionalidad.return_value = True
        self.mock_cliente_api.buscar_obras_por_query.return_value = []
        
        # Ejecutar búsqueda
        self.servicio.buscar_por_nacionalidad("TestNationality")
        
        # Verificar que se llama al gestor para validar
        self.mock_gestor_nacionalidades.validar_nacionalidad.assert_called_once_with("TestNationality")


class TestBuscarPorNombreArtista(unittest.TestCase):
    """Tests para el método buscar_por_nombre_artista"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
        
        # Datos de ejemplo para diferentes artistas
        self.datos_obra_bruegel = {
            'objectID': 436535,
            'title': 'The Harvesters',
            'artistDisplayName': 'Pieter Bruegel the Elder',
            'artistNationality': 'Netherlandish',
            'classification': 'Paintings',
            'objectDate': '1565'
        }
        
        self.datos_obra_van_gogh = {
            'objectID': 436536,
            'title': 'The Starry Night',
            'artistDisplayName': 'Vincent van Gogh',
            'artistNationality': 'Dutch',
            'classification': 'Paintings',
            'objectDate': '1889'
        }
        
        self.datos_obra_picasso = {
            'objectID': 436537,
            'title': 'Les Demoiselles d\'Avignon',
            'artistDisplayName': 'Pablo Picasso',
            'artistNationality': 'Spanish',
            'classification': 'Paintings',
            'objectDate': '1907'
        }
        
        self.datos_obra_sin_artista = {
            'objectID': 436538,
            'title': 'Unknown Work',
            'artistDisplayName': None,
            'artistNationality': None
        }
    
    def test_busqueda_artista_exitosa_nombre_completo(self):
        """Test de búsqueda exitosa por nombre completo de artista"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_bruegel
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("Pieter Bruegel the Elder")
        
        # Verificar resultados
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].id_obra, 436535)
        self.assertEqual(resultado[0].titulo, 'The Harvesters')
        self.assertEqual(resultado[0].artista.nombre, 'Pieter Bruegel the Elder')
        
        # Verificar llamadas
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Pieter Bruegel the Elder")
    
    def test_busqueda_artista_exitosa_nombre_parcial(self):
        """Test de búsqueda exitosa por nombre parcial de artista (Requirement 3.5)"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_bruegel
        
        # Ejecutar búsqueda con nombre parcial
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar resultados
        self.assertEqual(len(resultado), 1)
        self.assertIn("Bruegel", resultado[0].artista.nombre)
        
        # Verificar llamadas
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Bruegel")
    
    def test_busqueda_artista_multiples_coincidencias(self):
        """Test de búsqueda que retorna múltiples obras del mismo artista (Requirement 3.2, 3.3)"""
        # Configurar mocks para múltiples obras
        obra_bruegel_2 = self.datos_obra_bruegel.copy()
        obra_bruegel_2['objectID'] = 436539
        obra_bruegel_2['title'] = 'The Tower of Babel'
        
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535, 436539]
        
        def side_effect(id_obra):
            if id_obra == 436535:
                return self.datos_obra_bruegel
            else:
                return obra_bruegel_2
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar resultados
        self.assertEqual(len(resultado), 2)
        for obra in resultado:
            self.assertIn("Bruegel", obra.artista.nombre)
            self.assertIsNotNone(obra.id_obra)  # Requirement 3.3: ID de la obra
            self.assertIsNotNone(obra.titulo)   # Requirement 3.3: Título
            self.assertIsNotNone(obra.artista.nombre)  # Requirement 3.3: Nombre del autor
    
    def test_busqueda_artista_sin_resultados(self):
        """Test de búsqueda que no retorna obras (Requirement 3.4)"""
        # Configurar mock para retornar lista vacía
        self.mock_cliente_api.buscar_obras_por_query.return_value = []
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("ArtistaInexistente")
        
        # Verificar resultado vacío
        self.assertEqual(len(resultado), 0)
        self.mock_cliente_api.obtener_detalles_obra.assert_not_called()
    
    def test_busqueda_artista_filtrado_por_coincidencia(self):
        """Test que verifica el filtrado por coincidencia de nombre"""
        # Configurar mocks para retornar obras de diferentes artistas
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535, 436536, 436537]
        
        def side_effect(id_obra):
            if id_obra == 436535:
                return self.datos_obra_bruegel  # Contiene "Bruegel"
            elif id_obra == 436536:
                return self.datos_obra_van_gogh  # No contiene "Bruegel"
            else:
                return self.datos_obra_picasso  # No contiene "Bruegel"
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda por "Bruegel"
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar que solo se retorna la obra con nombre coincidente
        self.assertEqual(len(resultado), 1)
        self.assertIn("Bruegel", resultado[0].artista.nombre)
    
    def test_busqueda_artista_insensible_mayusculas(self):
        """Test de búsqueda insensible a mayúsculas y minúsculas"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_bruegel
        
        # Ejecutar búsqueda con diferentes casos
        resultado_lower = self.servicio.buscar_por_nombre_artista("bruegel")
        resultado_upper = self.servicio.buscar_por_nombre_artista("BRUEGEL")
        resultado_mixed = self.servicio.buscar_por_nombre_artista("BrUeGeL")
        
        # Verificar que todos encuentran la obra
        self.assertEqual(len(resultado_lower), 1)
        self.assertEqual(len(resultado_upper), 1)
        self.assertEqual(len(resultado_mixed), 1)
    
    def test_busqueda_artista_con_espacios(self):
        """Test de búsqueda con espacios al inicio y final"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_bruegel
        
        # Ejecutar búsqueda con espacios
        resultado = self.servicio.buscar_por_nombre_artista("  Bruegel  ")
        
        # Verificar resultado
        self.assertEqual(len(resultado), 1)
        
        # Verificar que se sanitizó el nombre antes de la búsqueda
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Bruegel")
    
    def test_busqueda_artista_caracteres_especiales(self):
        """Test de búsqueda con caracteres especiales en el nombre"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436536]
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_van_gogh
        
        # Ejecutar búsqueda con caracteres especiales
        resultado = self.servicio.buscar_por_nombre_artista("van Gogh")
        
        # Verificar resultado
        self.assertEqual(len(resultado), 1)
        self.assertIn("van Gogh", resultado[0].artista.nombre)
    
    def test_sanitizacion_nombre_artista(self):
        """Test de sanitización de nombres con caracteres problemáticos"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = []
        
        # Ejecutar búsqueda con caracteres problemáticos
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel@#$%^&*()")
        
        # Verificar que se sanitizó correctamente
        self.mock_cliente_api.buscar_obras_por_query.assert_called_once_with("Bruegel")
    
    def test_manejo_errores_conversion_individual_artista(self):
        """Test del manejo de errores en conversión de obras individuales"""
        # Configurar mocks
        self.mock_cliente_api.buscar_obras_por_query.return_value = [1, 2, 3]
        
        # Primera obra exitosa, segunda con error, tercera exitosa
        def side_effect(id_obra):
            if id_obra == 2:
                raise Exception("Error de conversión")
            return self.datos_obra_bruegel
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar que se procesaron solo las obras exitosas
        self.assertEqual(len(resultado), 2)
    
    def test_limitacion_obras_procesadas_artista(self):
        """Test que verifica la limitación de obras procesadas"""
        # Configurar mock para retornar muchas obras
        ids_obras = list(range(1, 51))  # 50 obras
        self.mock_cliente_api.buscar_obras_por_query.return_value = ids_obras
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_bruegel
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar que solo se procesaron 25 obras (límite)
        self.assertEqual(len(resultado), 25)
        self.assertEqual(self.mock_cliente_api.obtener_detalles_obra.call_count, 25)
    
    def test_obras_sin_nombre_artista(self):
        """Test con obras que no tienen nombre de artista"""
        # Configurar mocks para incluir obra sin artista
        self.mock_cliente_api.buscar_obras_por_query.return_value = [436535, 436538]
        
        def side_effect(id_obra):
            if id_obra == 436535:
                return self.datos_obra_bruegel  # Con artista
            else:
                return self.datos_obra_sin_artista  # Sin artista
        
        self.mock_cliente_api.obtener_detalles_obra.side_effect = side_effect
        
        # Ejecutar búsqueda
        resultado = self.servicio.buscar_por_nombre_artista("Bruegel")
        
        # Verificar que solo se retorna la obra con artista coincidente
        self.assertEqual(len(resultado), 1)
        self.assertIn("Bruegel", resultado[0].artista.nombre)
    
    def test_nombre_artista_vacio(self):
        """Test con nombre de artista vacío"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_nombre_artista("")
        
        self.assertIn("no vacía", str(context.exception))
    
    def test_nombre_artista_solo_espacios(self):
        """Test con nombre de artista que solo contiene espacios"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_nombre_artista("   ")
        
        self.assertIn("vacío después de la sanitización", str(context.exception))
    
    def test_nombre_artista_none(self):
        """Test con nombre de artista None"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_nombre_artista(None)
        
        self.assertIn("cadena no vacía", str(context.exception))
    
    def test_nombre_artista_no_string(self):
        """Test con nombre de artista que no es string"""
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda):
            self.servicio.buscar_por_nombre_artista(123)
    
    def test_error_api_busqueda_artista(self):
        """Test cuando hay error de API al buscar por artista"""
        self.mock_cliente_api.buscar_obras_por_query.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        with self.assertRaises(ExcepcionesServicioBusqueda.ErrorServicioBusqueda) as context:
            self.servicio.buscar_por_nombre_artista("Bruegel")
        
        self.assertIn("Error al buscar obras por artista", str(context.exception))


class TestSanitizarNombreArtista(unittest.TestCase):
    """Tests para el método _sanitizar_nombre_artista"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
    
    def test_sanitizacion_nombre_normal(self):
        """Test de sanitización con nombre normal"""
        resultado = self.servicio._sanitizar_nombre_artista("Vincent van Gogh")
        self.assertEqual(resultado, "Vincent van Gogh")
    
    def test_sanitizacion_espacios_extra(self):
        """Test de sanitización con espacios extra"""
        resultado = self.servicio._sanitizar_nombre_artista("  Vincent   van   Gogh  ")
        self.assertEqual(resultado, "Vincent van Gogh")
    
    def test_sanitizacion_caracteres_especiales(self):
        """Test de sanitización con caracteres especiales"""
        resultado = self.servicio._sanitizar_nombre_artista("Vincent@#$%van&*()Gogh")
        self.assertEqual(resultado, "VincentvanGogh")
    
    def test_sanitizacion_caracteres_permitidos(self):
        """Test de sanitización manteniendo caracteres permitidos"""
        resultado = self.servicio._sanitizar_nombre_artista("Jean-Baptiste O'Connor")
        self.assertEqual(resultado, "Jean-Baptiste O'Connor")
    
    def test_sanitizacion_numeros(self):
        """Test de sanitización con números"""
        resultado = self.servicio._sanitizar_nombre_artista("Artist 123")
        self.assertEqual(resultado, "Artist 123")
    
    def test_sanitizacion_string_vacio(self):
        """Test de sanitización con string vacío"""
        resultado = self.servicio._sanitizar_nombre_artista("")
        self.assertEqual(resultado, "")
    
    def test_sanitizacion_solo_caracteres_especiales(self):
        """Test de sanitización con solo caracteres especiales"""
        resultado = self.servicio._sanitizar_nombre_artista("@#$%^&*()")
        self.assertEqual(resultado, "")


class TestVerificarCoincidenciaNombreArtista(unittest.TestCase):
    """Tests para el método _verificar_coincidencia_nombre_artista"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.mock_gestor_nacionalidades = Mock(spec=GestorNacionalidades)
        self.servicio = ServicioBusqueda(self.mock_cliente_api, self.mock_gestor_nacionalidades)
    
    def test_coincidencia_exacta(self):
        """Test de coincidencia exacta"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "Vincent van Gogh", "Vincent van Gogh"
        )
        self.assertTrue(resultado)
    
    def test_coincidencia_parcial(self):
        """Test de coincidencia parcial"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "Vincent van Gogh", "van Gogh"
        )
        self.assertTrue(resultado)
    
    def test_coincidencia_insensible_mayusculas(self):
        """Test de coincidencia insensible a mayúsculas"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "Vincent van Gogh", "VINCENT"
        )
        self.assertTrue(resultado)
    
    def test_sin_coincidencia(self):
        """Test sin coincidencia"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "Vincent van Gogh", "Picasso"
        )
        self.assertFalse(resultado)
    
    def test_nombre_obra_vacio(self):
        """Test con nombre de obra vacío"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "", "Vincent"
        )
        self.assertFalse(resultado)
    
    def test_nombre_busqueda_vacio(self):
        """Test con nombre de búsqueda vacío"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(
            "Vincent van Gogh", ""
        )
        self.assertFalse(resultado)
    
    def test_ambos_nombres_none(self):
        """Test con ambos nombres None"""
        resultado = self.servicio._verificar_coincidencia_nombre_artista(None, None)
        self.assertFalse(resultado)


if __name__ == '__main__':
    unittest.main()
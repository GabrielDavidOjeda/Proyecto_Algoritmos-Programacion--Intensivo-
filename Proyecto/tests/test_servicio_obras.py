"""
Tests unitarios para la clase ServicioObras.
"""

import unittest
from unittest.mock import Mock, patch
from services.servicio_obras import ServicioObras
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from models.obra_arte import ObraArte
from models.artista import Artista


class TestServicioObras(unittest.TestCase):
    """Tests para la clase ServicioObras"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_cliente_api = Mock(spec=ClienteAPIMetMuseum)
        self.servicio = ServicioObras(self.mock_cliente_api)
        
        # Datos de ejemplo para una obra completa
        self.datos_obra_completa = {
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
        
        # Datos de ejemplo para una obra mínima
        self.datos_obra_minima = {
            'objectID': 123456,
            'title': 'Obra Sin Detalles'
        }
    
    def test_init_con_cliente_valido(self):
        """Test: Inicialización correcta con cliente API válido"""
        cliente = Mock(spec=ClienteAPIMetMuseum)
        servicio = ServicioObras(cliente)
        self.assertEqual(servicio._cliente_api, cliente)
        self.assertIsNotNone(servicio._visualizador_imagenes)
    
    def test_init_con_cliente_invalido(self):
        """Test: Error al inicializar con cliente inválido"""
        with self.assertRaises(ValueError) as context:
            ServicioObras("no_es_cliente")
        
        self.assertIn("ClienteAPIMetMuseum", str(context.exception))
    
    def test_init_con_visualizador_personalizado(self):
        """Test: Inicialización con visualizador personalizado"""
        from ui.visualizador_imagenes import VisualizadorImagenes
        cliente = Mock(spec=ClienteAPIMetMuseum)
        visualizador = Mock(spec=VisualizadorImagenes)
        servicio = ServicioObras(cliente, visualizador)
        self.assertEqual(servicio._cliente_api, cliente)
        self.assertEqual(servicio._visualizador_imagenes, visualizador)
    
    def test_obtener_detalles_obra_exitoso(self):
        """Test: Obtención exitosa de detalles de obra"""
        # Configurar mock
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_completa
        
        # Ejecutar
        resultado = self.servicio.obtener_detalles_obra(436535)
        
        # Verificar
        self.assertIsInstance(resultado, ObraArte)
        self.assertEqual(resultado.id_obra, 436535)
        self.assertEqual(resultado.titulo, 'The Harvesters')
        self.assertEqual(resultado.artista.nombre, 'Pieter Bruegel the Elder')
        self.assertEqual(resultado.artista.nacionalidad, 'Netherlandish')
        self.assertEqual(resultado.clasificacion, 'Paintings')
        self.assertEqual(resultado.fecha_creacion, '1565')
        self.assertEqual(resultado.url_imagen, 'https://images.metmuseum.org/test.jpg')
        self.assertEqual(resultado.departamento, 'European Paintings')
        
        # Verificar que se llamó al cliente API
        self.mock_cliente_api.obtener_detalles_obra.assert_called_once_with(436535)
    
    def test_obtener_detalles_obra_con_datos_minimos(self):
        """Test: Obtención de obra con datos mínimos"""
        # Configurar mock
        self.mock_cliente_api.obtener_detalles_obra.return_value = self.datos_obra_minima
        
        # Ejecutar
        resultado = self.servicio.obtener_detalles_obra(123456)
        
        # Verificar
        self.assertIsInstance(resultado, ObraArte)
        self.assertEqual(resultado.id_obra, 123456)
        self.assertEqual(resultado.titulo, 'Obra Sin Detalles')
        self.assertEqual(resultado.artista.nombre, 'Artista desconocido')
        self.assertIsNone(resultado.artista.nacionalidad)
        self.assertIsNone(resultado.clasificacion)
        self.assertIsNone(resultado.fecha_creacion)
        self.assertIsNone(resultado.url_imagen)
        self.assertIsNone(resultado.departamento)
    
    def test_obtener_detalles_obra_id_invalido(self):
        """Test: Error con ID de obra inválido"""
        casos_invalidos = [0, -1, "123", None, 3.14]
        
        for id_invalido in casos_invalidos:
            with self.subTest(id_obra=id_invalido):
                with self.assertRaises(ValueError) as context:
                    self.servicio.obtener_detalles_obra(id_invalido)
                
                self.assertIn("entero positivo", str(context.exception))
    
    def test_obtener_detalles_obra_no_encontrada(self):
        """Test: Manejo de obra no encontrada"""
        # Configurar mock para lanzar excepción
        self.mock_cliente_api.obtener_detalles_obra.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Obra no encontrada")
        
        # Verificar que se propaga la excepción
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado):
            self.servicio.obtener_detalles_obra(999999)
    
    def test_obtener_detalles_obra_error_conexion(self):
        """Test: Manejo de error de conexión"""
        # Configurar mock para lanzar excepción
        self.mock_cliente_api.obtener_detalles_obra.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        # Verificar que se propaga la excepción
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorConexionAPI):
            self.servicio.obtener_detalles_obra(436535)
    
    def test_obtener_detalles_obra_datos_incompletos(self):
        """Test: Manejo de datos incompletos de la API"""
        # Datos sin campos obligatorios
        datos_incompletos = {'objectID': 123}  # Falta 'title'
        
        self.mock_cliente_api.obtener_detalles_obra.return_value = datos_incompletos
        
        with self.assertRaises(ExcepcionesAPIMetMuseum.ErrorDatosIncompletos) as context:
            self.servicio.obtener_detalles_obra(123)
        
        self.assertIn("Datos incompletos", str(context.exception))
    
    def test_formatear_detalles_completos_obra_completa(self):
        """Test: Formateo de detalles de obra completa"""
        # Crear obra de ejemplo
        artista = Artista(
            nombre="Pieter Bruegel the Elder",
            nacionalidad="Netherlandish",
            fecha_nacimiento="1525",
            fecha_muerte="1569"
        )
        obra = ObraArte(
            id_obra=436535,
            titulo="The Harvesters",
            artista=artista,
            clasificacion="Paintings",
            fecha_creacion="1565",
            url_imagen="https://images.metmuseum.org/test.jpg",
            departamento="European Paintings"
        )
        
        # Ejecutar
        resultado = self.servicio.formatear_detalles_completos(obra)
        
        # Verificar contenido
        self.assertIn("DETALLES DE LA OBRA", resultado)
        self.assertIn("ID de la Obra: 436535", resultado)
        self.assertIn("Título: The Harvesters", resultado)
        self.assertIn("Nombre: Pieter Bruegel the Elder", resultado)
        self.assertIn("Nacionalidad: Netherlandish", resultado)
        self.assertIn("Período de vida: 1525-1569", resultado)
        self.assertIn("Tipo: Paintings", resultado)
        self.assertIn("Año de creación: 1565", resultado)
        self.assertIn("Departamento: European Paintings", resultado)
        self.assertIn("Imagen: Disponible", resultado)
    
    def test_formatear_detalles_completos_obra_minima(self):
        """Test: Formateo de detalles de obra con información mínima"""
        # Crear obra mínima
        artista = Artista(nombre="Artista desconocido")
        obra = ObraArte(
            id_obra=123456,
            titulo="Obra Sin Detalles",
            artista=artista
        )
        
        # Ejecutar
        resultado = self.servicio.formatear_detalles_completos(obra)
        
        # Verificar contenido básico
        self.assertIn("ID de la Obra: 123456", resultado)
        self.assertIn("Título: Obra Sin Detalles", resultado)
        self.assertIn("Nombre: Artista desconocido", resultado)
        self.assertIn("Imagen: No disponible", resultado)
        
        # Verificar que no aparecen campos opcionales
        self.assertNotIn("Nacionalidad:", resultado)
        self.assertNotIn("Tipo:", resultado)
        self.assertNotIn("Año de creación:", resultado)
        self.assertNotIn("Departamento:", resultado)
    
    def test_formatear_detalles_completos_parametro_invalido(self):
        """Test: Error al formatear con parámetro inválido"""
        with self.assertRaises(ValueError) as context:
            self.servicio.formatear_detalles_completos("no_es_obra")
        
        self.assertIn("ObraArte", str(context.exception))
    
    def test_validar_datos_obra_datos_validos(self):
        """Test: Validación exitosa de datos válidos"""
        self.assertTrue(self.servicio._validar_datos_obra(self.datos_obra_completa))
        self.assertTrue(self.servicio._validar_datos_obra(self.datos_obra_minima))
    
    def test_validar_datos_obra_datos_invalidos(self):
        """Test: Validación de datos inválidos"""
        casos_invalidos = [
            None,  # No es diccionario
            {},  # Diccionario vacío
            {'objectID': 123},  # Falta title
            {'title': 'Test'},  # Falta objectID
            {'objectID': 'abc', 'title': 'Test'},  # objectID no es entero
            {'objectID': -1, 'title': 'Test'},  # objectID negativo
            {'objectID': 0, 'title': 'Test'},  # objectID cero
            {'objectID': 123, 'title': ''},  # title vacío
            {'objectID': 123, 'title': '   '},  # title solo espacios
            {'objectID': 123, 'title': None},  # title None
        ]
        
        for datos_invalidos in casos_invalidos:
            with self.subTest(datos=datos_invalidos):
                self.assertFalse(self.servicio._validar_datos_obra(datos_invalidos))
    
    def test_convertir_datos_api_a_obra_completa(self):
        """Test: Conversión exitosa de datos completos"""
        resultado = self.servicio._convertir_datos_api_a_obra(self.datos_obra_completa)
        
        self.assertIsInstance(resultado, ObraArte)
        self.assertEqual(resultado.id_obra, 436535)
        self.assertEqual(resultado.titulo, 'The Harvesters')
        self.assertEqual(resultado.artista.nombre, 'Pieter Bruegel the Elder')
        self.assertEqual(resultado.artista.nacionalidad, 'Netherlandish')
    
    def test_convertir_datos_api_a_obra_minima(self):
        """Test: Conversión de datos mínimos"""
        resultado = self.servicio._convertir_datos_api_a_obra(self.datos_obra_minima)
        
        self.assertIsInstance(resultado, ObraArte)
        self.assertEqual(resultado.id_obra, 123456)
        self.assertEqual(resultado.titulo, 'Obra Sin Detalles')
        self.assertEqual(resultado.artista.nombre, 'Artista desconocido')
    
    def test_extraer_nombre_artista_diferentes_campos(self):
        """Test: Extracción de nombre de artista de diferentes campos"""
        casos = [
            ({'artistDisplayName': 'Van Gogh'}, 'Van Gogh'),
            ({'artistName': 'Picasso'}, 'Picasso'),
            ({'artist': 'Monet'}, 'Monet'),
            ({'artistDisplayName': '', 'artistName': 'Dalí'}, 'Dalí'),
            ({}, 'Artista desconocido'),
            ({'artistDisplayName': '   '}, 'Artista desconocido'),
        ]
        
        for datos, esperado in casos:
            with self.subTest(datos=datos):
                resultado = self.servicio._extraer_nombre_artista(datos)
                self.assertEqual(resultado, esperado)
    
    def test_extraer_campo_opcional(self):
        """Test: Extracción de campos opcionales"""
        datos = {
            'campo_presente': 'valor',
            'campo_vacio': '',
            'campo_espacios': '   ',
            'campo_none': None
        }
        
        # Campo presente
        self.assertEqual(
            self.servicio._extraer_campo_opcional(datos, 'campo_presente'),
            'valor'
        )
        
        # Campos que deben retornar None
        campos_none = ['campo_vacio', 'campo_espacios', 'campo_none', 'campo_inexistente']
        for campo in campos_none:
            with self.subTest(campo=campo):
                self.assertIsNone(
                    self.servicio._extraer_campo_opcional(datos, campo)
                )
    
    def test_extraer_url_imagen_diferentes_campos(self):
        """Test: Extracción de URL de imagen de diferentes campos"""
        casos = [
            ({'primaryImage': 'https://example.com/img1.jpg'}, 'https://example.com/img1.jpg'),
            ({'primaryImageSmall': 'http://example.com/img2.jpg'}, 'http://example.com/img2.jpg'),
            ({'image': 'https://example.com/img3.jpg'}, 'https://example.com/img3.jpg'),
            ({'primaryImage': 'invalid-url'}, None),
            ({'primaryImage': ''}, None),
            ({}, None),
        ]
        
        for datos, esperado in casos:
            with self.subTest(datos=datos):
                resultado = self.servicio._extraer_url_imagen(datos)
                self.assertEqual(resultado, esperado)
    
    def test_mostrar_imagen_obra_exitoso(self):
        """Test: Mostrar imagen de obra exitoso"""
        from ui.visualizador_imagenes import VisualizadorImagenes
        
        # Crear mock del visualizador
        mock_visualizador = Mock(spec=VisualizadorImagenes)
        servicio = ServicioObras(self.mock_cliente_api, mock_visualizador)
        
        # Crear obra con imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, 
                       url_imagen="https://example.com/image.jpg")
        
        # Ejecutar
        servicio.mostrar_imagen_obra(obra)
        
        # Verificar
        mock_visualizador.mostrar_imagen_en_ventana.assert_called_once_with(
            "https://example.com/image.jpg",
            "Test Artwork - Test Artist"
        )
    
    def test_mostrar_imagen_obra_sin_imagen(self):
        """Test: Error al mostrar imagen de obra sin imagen"""
        # Crear obra sin imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista)  # Sin URL de imagen
        
        # Ejecutar y verificar error
        with self.assertRaises(ValueError) as context:
            self.servicio.mostrar_imagen_obra(obra)
        
        self.assertIn("no tiene imagen disponible", str(context.exception))
    
    def test_mostrar_imagen_obra_parametro_invalido(self):
        """Test: Error con parámetro inválido en mostrar imagen"""
        with self.assertRaises(ValueError) as context:
            self.servicio.mostrar_imagen_obra("no_es_obra")
        
        self.assertIn("ObraArte", str(context.exception))
    
    def test_mostrar_imagen_obra_error_visualizador(self):
        """Test: Error del visualizador al mostrar imagen"""
        from ui.visualizador_imagenes import VisualizadorImagenes
        
        # Crear mock del visualizador que lanza excepción
        mock_visualizador = Mock(spec=VisualizadorImagenes)
        mock_visualizador.mostrar_imagen_en_ventana.side_effect = \
            Exception("Error de visualización")
        
        servicio = ServicioObras(self.mock_cliente_api, mock_visualizador)
        
        # Crear obra con imagen
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, 
                       url_imagen="https://example.com/image.jpg")
        
        # Ejecutar y verificar error
        with self.assertRaises(Exception) as context:
            servicio.mostrar_imagen_obra(obra)
        
        self.assertIn("Error al mostrar imagen de la obra", str(context.exception))


if __name__ == '__main__':
    unittest.main()
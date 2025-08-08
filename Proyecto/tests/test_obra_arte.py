"""
Tests unitarios para la clase ObraArte.
"""

import unittest
from models.artista import Artista
from models.obra_arte import ObraArte


class TestObraArte(unittest.TestCase):
    """Tests para la clase ObraArte."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.artista = Artista(
            nombre="Pieter Bruegel the Elder",
            nacionalidad="Netherlandish",
            fecha_nacimiento="1525",
            fecha_muerte="1569"
        )
        
        self.obra_completa = ObraArte(
            id_obra=436535,
            titulo="The Harvesters",
            artista=self.artista,
            clasificacion="Paintings",
            fecha_creacion="1565",
            url_imagen="https://images.metmuseum.org/test.jpg",
            departamento="European Paintings"
        )
        
        self.obra_minima = ObraArte(
            id_obra=123,
            titulo="Test Artwork",
            artista=self.artista
        )
    
    def test_creacion_obra_con_datos_completos(self):
        """Test de creación de obra con todos los datos."""
        obra = ObraArte(
            id_obra=12345,
            titulo="Starry Night",
            artista=self.artista,
            clasificacion="Oil Painting",
            fecha_creacion="1889",
            url_imagen="https://example.com/image.jpg",
            departamento="Modern Art"
        )
        
        self.assertEqual(obra.id_obra, 12345)
        self.assertEqual(obra.titulo, "Starry Night")
        self.assertEqual(obra.artista, self.artista)
        self.assertEqual(obra.clasificacion, "Oil Painting")
        self.assertEqual(obra.fecha_creacion, "1889")
        self.assertEqual(obra.url_imagen, "https://example.com/image.jpg")
        self.assertEqual(obra.departamento, "Modern Art")
    
    def test_creacion_obra_datos_minimos(self):
        """Test de creación de obra con datos mínimos requeridos."""
        obra = ObraArte(id_obra=999, titulo="Test", artista=self.artista)
        
        self.assertEqual(obra.id_obra, 999)
        self.assertEqual(obra.titulo, "Test")
        self.assertEqual(obra.artista, self.artista)
        self.assertIsNone(obra.clasificacion)
        self.assertIsNone(obra.fecha_creacion)
        self.assertIsNone(obra.url_imagen)
        self.assertIsNone(obra.departamento)
    
    def test_id_obra_requerido_y_valido(self):
        """Test que el ID de obra es requerido y válido."""
        with self.assertRaises(ValueError):
            ObraArte(id_obra=0, titulo="Test", artista=self.artista)
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra=-1, titulo="Test", artista=self.artista)
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra="123", titulo="Test", artista=self.artista)
    
    def test_titulo_requerido(self):
        """Test que el título es requerido."""
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo="", artista=self.artista)
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo=None, artista=self.artista)
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo="   ", artista=self.artista)
    
    def test_artista_requerido_y_valido(self):
        """Test que el artista es requerido y debe ser instancia de Artista."""
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo="Test", artista=None)
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo="Test", artista="Not an artist")
        
        with self.assertRaises(ValueError):
            ObraArte(id_obra=123, titulo="Test", artista={})
    
    def test_propiedades_getter(self):
        """Test de los getters de propiedades."""
        self.assertEqual(self.obra_completa.id_obra, 436535)
        self.assertEqual(self.obra_completa.titulo, "The Harvesters")
        self.assertEqual(self.obra_completa.artista, self.artista)
        self.assertEqual(self.obra_completa.clasificacion, "Paintings")
        self.assertEqual(self.obra_completa.fecha_creacion, "1565")
        self.assertEqual(self.obra_completa.url_imagen, "https://images.metmuseum.org/test.jpg")
        self.assertEqual(self.obra_completa.departamento, "European Paintings")
    
    def test_propiedades_setter(self):
        """Test de los setters de propiedades."""
        obra = ObraArte(id_obra=123, titulo="Test", artista=self.artista)
        nuevo_artista = Artista("New Artist")
        
        obra.titulo = "Nuevo Título"
        self.assertEqual(obra.titulo, "Nuevo Título")
        
        obra.artista = nuevo_artista
        self.assertEqual(obra.artista, nuevo_artista)
        
        obra.clasificacion = "Sculpture"
        self.assertEqual(obra.clasificacion, "Sculpture")
        
        obra.fecha_creacion = "2000"
        self.assertEqual(obra.fecha_creacion, "2000")
        
        obra.url_imagen = "https://new-image.com"
        self.assertEqual(obra.url_imagen, "https://new-image.com")
        
        obra.departamento = "Contemporary Art"
        self.assertEqual(obra.departamento, "Contemporary Art")
    
    def test_setter_titulo_invalido(self):
        """Test que el setter de título valida correctamente."""
        obra = ObraArte(id_obra=123, titulo="Test", artista=self.artista)
        
        with self.assertRaises(ValueError):
            obra.titulo = ""
        
        with self.assertRaises(ValueError):
            obra.titulo = None
        
        with self.assertRaises(ValueError):
            obra.titulo = 123
    
    def test_setter_artista_invalido(self):
        """Test que el setter de artista valida correctamente."""
        obra = ObraArte(id_obra=123, titulo="Test", artista=self.artista)
        
        with self.assertRaises(ValueError):
            obra.artista = "Not an artist"
        
        with self.assertRaises(ValueError):
            obra.artista = None
    
    def test_mostrar_resumen(self):
        """Test del método mostrar_resumen."""
        resumen = self.obra_completa.mostrar_resumen()
        expected = "ID: 436535 | The Harvesters | Pieter Bruegel the Elder"
        self.assertEqual(resumen, expected)
    
    def test_mostrar_detalles_completos(self):
        """Test del método mostrar_detalles_completos."""
        detalles = self.obra_completa.mostrar_detalles_completos()
        
        self.assertIn("ID de la Obra: 436535", detalles)
        self.assertIn("Título: The Harvesters", detalles)
        self.assertIn("Artista: Pieter Bruegel the Elder", detalles)
        self.assertIn("Tipo: Paintings", detalles)
        self.assertIn("Año de creación: 1565", detalles)
        self.assertIn("Departamento: European Paintings", detalles)
        self.assertIn("Imagen disponible: Sí", detalles)
    
    def test_mostrar_detalles_completos_sin_imagen(self):
        """Test del método mostrar_detalles_completos sin imagen."""
        detalles = self.obra_minima.mostrar_detalles_completos()
        self.assertIn("Imagen disponible: No", detalles)
    
    def test_tiene_imagen(self):
        """Test del método tiene_imagen."""
        self.assertTrue(self.obra_completa.tiene_imagen())
        self.assertFalse(self.obra_minima.tiene_imagen())
        
        # Test con URL vacía
        obra_sin_imagen = ObraArte(id_obra=123, titulo="Test", artista=self.artista, url_imagen="")
        self.assertFalse(obra_sin_imagen.tiene_imagen())
    
    def test_obtener_info_artista(self):
        """Test del método obtener_info_artista."""
        info = self.obra_completa.obtener_info_artista()
        
        self.assertEqual(info['nombre'], "Pieter Bruegel the Elder")
        self.assertEqual(info['nacionalidad'], "Netherlandish")
        self.assertEqual(info['fecha_nacimiento'], "1525")
        self.assertEqual(info['fecha_muerte'], "1569")
        self.assertEqual(info['periodo_vida'], "1525-1569")
    
    def test_str_representation(self):
        """Test de la representación en cadena."""
        str_repr = str(self.obra_completa)
        expected = '"The Harvesters" por Pieter Bruegel the Elder (ID: 436535)'
        self.assertEqual(str_repr, expected)
    
    def test_repr_representation(self):
        """Test de la representación técnica."""
        repr_str = repr(self.obra_completa)
        self.assertIn("ObraArte", repr_str)
        self.assertIn("436535", repr_str)
        self.assertIn("The Harvesters", repr_str)
    
    def test_equality(self):
        """Test de comparación de igualdad."""
        obra1 = ObraArte(id_obra=123, titulo="Test1", artista=self.artista)
        obra2 = ObraArte(id_obra=123, titulo="Test2", artista=self.artista)  # Mismo ID
        obra3 = ObraArte(id_obra=456, titulo="Test1", artista=self.artista)  # Diferente ID
        
        self.assertEqual(obra1, obra2)  # Mismo ID
        self.assertNotEqual(obra1, obra3)  # Diferente ID
        self.assertNotEqual(obra1, "not an artwork")
    
    def test_espacios_en_blanco_eliminados(self):
        """Test que los espacios en blanco se eliminan correctamente."""
        obra = ObraArte(
            id_obra=123,
            titulo="  Test Title  ",
            artista=self.artista,
            clasificacion="  Painting  ",
            fecha_creacion="  1900  ",
            url_imagen="  https://example.com  ",
            departamento="  Art Department  "
        )
        
        self.assertEqual(obra.titulo, "Test Title")
        self.assertEqual(obra.clasificacion, "Painting")
        self.assertEqual(obra.fecha_creacion, "1900")
        self.assertEqual(obra.url_imagen, "https://example.com")
        self.assertEqual(obra.departamento, "Art Department")
    
    def test_valores_none_manejados_correctamente(self):
        """Test que los valores None se manejan correctamente."""
        obra = ObraArte(
            id_obra=123,
            titulo="Test",
            artista=self.artista,
            clasificacion=None,
            fecha_creacion=None,
            url_imagen=None,
            departamento=None
        )
        
        self.assertEqual(obra.titulo, "Test")
        self.assertIsNone(obra.clasificacion)
        self.assertIsNone(obra.fecha_creacion)
        self.assertIsNone(obra.url_imagen)
        self.assertIsNone(obra.departamento)


if __name__ == '__main__':
    unittest.main()
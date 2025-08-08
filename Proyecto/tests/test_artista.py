"""
Tests unitarios para la clase Artista.
"""

import unittest
from models.artista import Artista


class TestArtista(unittest.TestCase):
    """Tests para la clase Artista."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.artista_completo = Artista(
            nombre="Pieter Bruegel the Elder",
            nacionalidad="Netherlandish",
            fecha_nacimiento="1525",
            fecha_muerte="1569"
        )
        
        self.artista_minimo = Artista(nombre="Leonardo da Vinci")
    
    def test_creacion_artista_con_datos_completos(self):
        """Test de creación de artista con todos los datos."""
        artista = Artista(
            nombre="Vincent van Gogh",
            nacionalidad="Dutch",
            fecha_nacimiento="1853",
            fecha_muerte="1890"
        )
        
        self.assertEqual(artista.nombre, "Vincent van Gogh")
        self.assertEqual(artista.nacionalidad, "Dutch")
        self.assertEqual(artista.fecha_nacimiento, "1853")
        self.assertEqual(artista.fecha_muerte, "1890")
    
    def test_creacion_artista_solo_nombre(self):
        """Test de creación de artista solo con nombre."""
        artista = Artista(nombre="Pablo Picasso")
        
        self.assertEqual(artista.nombre, "Pablo Picasso")
        self.assertIsNone(artista.nacionalidad)
        self.assertIsNone(artista.fecha_nacimiento)
        self.assertIsNone(artista.fecha_muerte)
    
    def test_nombre_requerido(self):
        """Test que el nombre es requerido."""
        with self.assertRaises(ValueError):
            Artista(nombre="")
        
        with self.assertRaises(ValueError):
            Artista(nombre=None)
        
        with self.assertRaises(ValueError):
            Artista(nombre="   ")
    
    def test_nombre_debe_ser_string(self):
        """Test que el nombre debe ser una cadena."""
        with self.assertRaises(ValueError):
            Artista(nombre=123)
        
        with self.assertRaises(ValueError):
            Artista(nombre=[])
    
    def test_propiedades_getter(self):
        """Test de los getters de propiedades."""
        self.assertEqual(self.artista_completo.nombre, "Pieter Bruegel the Elder")
        self.assertEqual(self.artista_completo.nacionalidad, "Netherlandish")
        self.assertEqual(self.artista_completo.fecha_nacimiento, "1525")
        self.assertEqual(self.artista_completo.fecha_muerte, "1569")
    
    def test_propiedades_setter(self):
        """Test de los setters de propiedades."""
        artista = Artista(nombre="Test Artist")
        
        artista.nombre = "Nuevo Nombre"
        self.assertEqual(artista.nombre, "Nuevo Nombre")
        
        artista.nacionalidad = "Spanish"
        self.assertEqual(artista.nacionalidad, "Spanish")
        
        artista.fecha_nacimiento = "1900"
        self.assertEqual(artista.fecha_nacimiento, "1900")
        
        artista.fecha_muerte = "1980"
        self.assertEqual(artista.fecha_muerte, "1980")
    
    def test_setter_nombre_invalido(self):
        """Test que el setter de nombre valida correctamente."""
        artista = Artista(nombre="Test Artist")
        
        with self.assertRaises(ValueError):
            artista.nombre = ""
        
        with self.assertRaises(ValueError):
            artista.nombre = None
        
        with self.assertRaises(ValueError):
            artista.nombre = 123
    
    def test_obtener_periodo_vida_completo(self):
        """Test del método obtener_periodo_vida con fechas completas."""
        periodo = self.artista_completo.obtener_periodo_vida()
        self.assertEqual(periodo, "1525-1569")
    
    def test_obtener_periodo_vida_solo_nacimiento(self):
        """Test del método obtener_periodo_vida solo con fecha de nacimiento."""
        artista = Artista(nombre="Test", fecha_nacimiento="1900")
        periodo = artista.obtener_periodo_vida()
        self.assertEqual(periodo, "1900-presente")
    
    def test_obtener_periodo_vida_sin_fechas(self):
        """Test del método obtener_periodo_vida sin fechas."""
        periodo = self.artista_minimo.obtener_periodo_vida()
        self.assertEqual(periodo, "Fechas desconocidas")
    
    def test_str_representation(self):
        """Test de la representación en cadena."""
        str_completo = str(self.artista_completo)
        self.assertIn("Pieter Bruegel the Elder", str_completo)
        self.assertIn("Netherlandish", str_completo)
        self.assertIn("1525-1569", str_completo)
        
        str_minimo = str(self.artista_minimo)
        self.assertEqual(str_minimo, "Leonardo da Vinci")
    
    def test_repr_representation(self):
        """Test de la representación técnica."""
        repr_str = repr(self.artista_completo)
        self.assertIn("Artista", repr_str)
        self.assertIn("Pieter Bruegel the Elder", repr_str)
        self.assertIn("Netherlandish", repr_str)
    
    def test_equality(self):
        """Test de comparación de igualdad."""
        artista1 = Artista("Test", "Spanish", "1900", "1980")
        artista2 = Artista("Test", "Spanish", "1900", "1980")
        artista3 = Artista("Test", "French", "1900", "1980")
        
        self.assertEqual(artista1, artista2)
        self.assertNotEqual(artista1, artista3)
        self.assertNotEqual(artista1, "not an artist")
    
    def test_espacios_en_blanco_eliminados(self):
        """Test que los espacios en blanco se eliminan correctamente."""
        artista = Artista(
            nombre="  Test Artist  ",
            nacionalidad="  Spanish  ",
            fecha_nacimiento="  1900  ",
            fecha_muerte="  1980  "
        )
        
        self.assertEqual(artista.nombre, "Test Artist")
        self.assertEqual(artista.nacionalidad, "Spanish")
        self.assertEqual(artista.fecha_nacimiento, "1900")
        self.assertEqual(artista.fecha_muerte, "1980")
    
    def test_valores_none_manejados_correctamente(self):
        """Test que los valores None se manejan correctamente."""
        artista = Artista(
            nombre="Test",
            nacionalidad=None,
            fecha_nacimiento=None,
            fecha_muerte=None
        )
        
        self.assertEqual(artista.nombre, "Test")
        self.assertIsNone(artista.nacionalidad)
        self.assertIsNone(artista.fecha_nacimiento)
        self.assertIsNone(artista.fecha_muerte)


if __name__ == '__main__':
    unittest.main()
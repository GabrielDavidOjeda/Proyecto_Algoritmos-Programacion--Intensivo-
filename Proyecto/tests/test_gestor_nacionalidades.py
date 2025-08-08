"""
Tests unitarios para la clase GestorNacionalidades.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from utils.gestor_nacionalidades import GestorNacionalidades, ErrorArchivoNacionalidades


class TestGestorNacionalidades(unittest.TestCase):
    """Tests para la clase GestorNacionalidades."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.archivo_temporal = None
        self.gestor = None
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if self.archivo_temporal and os.path.exists(self.archivo_temporal):
            os.unlink(self.archivo_temporal)
    
    def crear_archivo_temporal(self, contenido: str) -> str:
        """
        Crea un archivo temporal con el contenido especificado.
        
        Args:
            contenido (str): Contenido del archivo
            
        Returns:
            str: Ruta del archivo temporal creado
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(contenido)
            return f.name
    
    def test_inicializacion_gestor(self):
        """Test de inicialización correcta del gestor."""
        ruta_archivo = "test_nacionalidades.txt"
        gestor = GestorNacionalidades(ruta_archivo)
        
        self.assertEqual(gestor.ruta_archivo, ruta_archivo)
        self.assertFalse(gestor.archivo_cargado)
        self.assertEqual(len(gestor), 0)
    
    def test_cargar_nacionalidades_exitoso(self):
        """Test de carga exitosa de nacionalidades desde archivo."""
        contenido = "American\nBritish\nFrench\nGerman\nItalian\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        self.assertTrue(gestor.archivo_cargado)
        self.assertEqual(len(gestor), 5)
        
        nacionalidades = gestor.obtener_nacionalidades_disponibles()
        self.assertEqual(nacionalidades, ["American", "British", "French", "German", "Italian"])
    
    def test_cargar_nacionalidades_con_comentarios_y_lineas_vacias(self):
        """Test de carga de nacionalidades ignorando comentarios y líneas vacías."""
        contenido = """# Este es un comentario
American
# Otro comentario
British

French
    
German
# Comentario final
Italian"""
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        nacionalidades = gestor.obtener_nacionalidades_disponibles()
        self.assertEqual(nacionalidades, ["American", "British", "French", "German", "Italian"])
    
    def test_cargar_nacionalidades_elimina_duplicados(self):
        """Test que verifica la eliminación de nacionalidades duplicadas."""
        contenido = "American\nBritish\nAmerican\nFrench\nBritish\nGerman\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        nacionalidades = gestor.obtener_nacionalidades_disponibles()
        self.assertEqual(nacionalidades, ["American", "British", "French", "German"])
        self.assertEqual(len(gestor), 4)
    
    def test_cargar_nacionalidades_archivo_inexistente(self):
        """Test de error cuando el archivo no existe."""
        gestor = GestorNacionalidades("archivo_inexistente.txt")
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.cargar_nacionalidades()
        
        self.assertIn("no existe", str(context.exception))
        self.assertFalse(gestor.archivo_cargado)
    
    def test_cargar_nacionalidades_archivo_vacio(self):
        """Test de error cuando el archivo está vacío."""
        self.archivo_temporal = self.crear_archivo_temporal("")
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.cargar_nacionalidades()
        
        self.assertIn("vacío", str(context.exception))
        self.assertFalse(gestor.archivo_cargado)
    
    def test_cargar_nacionalidades_solo_comentarios(self):
        """Test de error cuando el archivo solo contiene comentarios."""
        contenido = "# Solo comentarios\n# Más comentarios\n# Y más comentarios\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.cargar_nacionalidades()
        
        self.assertIn("vacío", str(context.exception))
    
    def test_cargar_nacionalidades_directorio_en_lugar_de_archivo(self):
        """Test de error cuando se proporciona un directorio en lugar de archivo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            gestor = GestorNacionalidades(temp_dir)
            
            with self.assertRaises(ErrorArchivoNacionalidades) as context:
                gestor.cargar_nacionalidades()
            
            self.assertIn("no es un archivo", str(context.exception))
    
    @patch("os.path.exists", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", side_effect=IOError("Error de lectura"))
    def test_cargar_nacionalidades_error_lectura(self, mock_file, mock_isfile, mock_exists):
        """Test de error de lectura del archivo."""
        gestor = GestorNacionalidades("test.txt")
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.cargar_nacionalidades()
        
        self.assertIn("Error al leer", str(context.exception))
    
    def test_validar_nacionalidad_exitoso(self):
        """Test de validación exitosa de nacionalidades."""
        contenido = "American\nBritish\nFrench\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        self.assertTrue(gestor.validar_nacionalidad("American"))
        self.assertTrue(gestor.validar_nacionalidad("British"))
        self.assertTrue(gestor.validar_nacionalidad("French"))
        self.assertFalse(gestor.validar_nacionalidad("German"))
        self.assertFalse(gestor.validar_nacionalidad("Italian"))
    
    def test_validar_nacionalidad_case_insensitive(self):
        """Test de validación case-insensitive de nacionalidades."""
        contenido = "American\nBritish\nFrench\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        self.assertTrue(gestor.validar_nacionalidad("american"))
        self.assertTrue(gestor.validar_nacionalidad("BRITISH"))
        self.assertTrue(gestor.validar_nacionalidad("French"))
        self.assertTrue(gestor.validar_nacionalidad("fReNcH"))
    
    def test_validar_nacionalidad_con_espacios(self):
        """Test de validación de nacionalidades con espacios."""
        contenido = "American\nBritish\nFrench\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        self.assertTrue(gestor.validar_nacionalidad("  American  "))
        self.assertTrue(gestor.validar_nacionalidad(" British "))
        self.assertFalse(gestor.validar_nacionalidad(""))
        self.assertFalse(gestor.validar_nacionalidad("   "))
    
    def test_validar_nacionalidad_sin_cargar_archivo(self):
        """Test de error al validar sin haber cargado el archivo."""
        gestor = GestorNacionalidades("test.txt")
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.validar_nacionalidad("American")
        
        self.assertIn("no han sido cargadas", str(context.exception))
    
    def test_obtener_nacionalidades_disponibles_sin_cargar(self):
        """Test de error al obtener nacionalidades sin haber cargado el archivo."""
        gestor = GestorNacionalidades("test.txt")
        
        with self.assertRaises(ErrorArchivoNacionalidades) as context:
            gestor.obtener_nacionalidades_disponibles()
        
        self.assertIn("no han sido cargadas", str(context.exception))
    
    def test_obtener_nacionalidades_disponibles_retorna_copia(self):
        """Test que verifica que se retorna una copia de la lista."""
        contenido = "American\nBritish\nFrench\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        nacionalidades1 = gestor.obtener_nacionalidades_disponibles()
        nacionalidades2 = gestor.obtener_nacionalidades_disponibles()
        
        # Verificar que son listas diferentes (copias)
        self.assertIsNot(nacionalidades1, nacionalidades2)
        self.assertEqual(nacionalidades1, nacionalidades2)
        
        # Modificar una lista no debe afectar la otra
        nacionalidades1.append("German")
        self.assertNotEqual(nacionalidades1, nacionalidades2)
    
    def test_propiedades_gestor(self):
        """Test de las propiedades del gestor."""
        ruta_archivo = "test_nacionalidades.txt"
        gestor = GestorNacionalidades(ruta_archivo)
        
        # Antes de cargar
        self.assertEqual(gestor.ruta_archivo, ruta_archivo)
        self.assertFalse(gestor.archivo_cargado)
        self.assertEqual(len(gestor), 0)
        
        # Después de cargar
        contenido = "American\nBritish\nFrench\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        self.assertTrue(gestor.archivo_cargado)
        self.assertEqual(len(gestor), 3)
    
    def test_manejo_encoding_utf8(self):
        """Test de manejo correcto de caracteres UTF-8."""
        contenido = "Español\nFrançais\nDeutsch\nРусский\n中文\n"
        self.archivo_temporal = self.crear_archivo_temporal(contenido)
        
        gestor = GestorNacionalidades(self.archivo_temporal)
        gestor.cargar_nacionalidades()
        
        nacionalidades = gestor.obtener_nacionalidades_disponibles()
        self.assertEqual(len(nacionalidades), 5)
        self.assertIn("Español", nacionalidades)
        self.assertIn("Français", nacionalidades)
        self.assertIn("Русский", nacionalidades)
        self.assertIn("中文", nacionalidades)
        
        # Test de validación con caracteres especiales
        self.assertTrue(gestor.validar_nacionalidad("Español"))
        self.assertTrue(gestor.validar_nacionalidad("Français"))


if __name__ == '__main__':
    unittest.main()
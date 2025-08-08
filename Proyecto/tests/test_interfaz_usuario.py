"""
Tests unitarios para la clase InterfazUsuario.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from ui.interfaz_usuario import InterfazUsuario
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestInterfazUsuario(unittest.TestCase):
    """Tests para la clase InterfazUsuario."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.interfaz = InterfazUsuario()
        
        # Crear objetos de prueba
        self.artista_prueba = Artista(
            nombre="Vincent van Gogh",
            nacionalidad="Dutch",
            fecha_nacimiento="1853",
            fecha_muerte="1890"
        )
        
        self.obra_prueba = ObraArte(
            id_obra=436535,
            titulo="The Starry Night",
            artista=self.artista_prueba,
            clasificacion="Paintings",
            fecha_creacion="1889",
            url_imagen="https://example.com/image.jpg",
            departamento="European Paintings"
        )
        
        self.departamento_prueba = Departamento(1, "European Paintings")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_mostrar_menu_principal_opcion_valida(self, mock_print, mock_input):
        """Test que el menú principal retorna opción válida."""
        mock_input.return_value = "1"
        
        resultado = self.interfaz.mostrar_menu_principal()
        
        self.assertEqual(resultado, 1)
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_mostrar_menu_principal_opcion_invalida_luego_valida(self, mock_print, mock_input):
        """Test que el menú principal maneja opciones inválidas."""
        mock_input.side_effect = ["0", "6", "abc", "3"]
        
        resultado = self.interfaz.mostrar_menu_principal()
        
        self.assertEqual(resultado, 3)
        # Verificar que se llamó input múltiples veces
        self.assertEqual(mock_input.call_count, 4)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_seleccion_departamento_valida(self, mock_print, mock_input):
        """Test selección válida de departamento."""
        departamentos = [
            Departamento(1, "European Paintings"),
            Departamento(2, "American Decorative Arts")
        ]
        mock_input.return_value = "1"
        
        resultado = self.interfaz.solicitar_seleccion_departamento(departamentos)
        
        self.assertEqual(resultado, 1)
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_seleccion_departamento_invalida_luego_valida(self, mock_print, mock_input):
        """Test selección inválida de departamento seguida de válida."""
        departamentos = [Departamento(1, "European Paintings")]
        mock_input.side_effect = ["0", "2", "abc", "1"]
        
        resultado = self.interfaz.solicitar_seleccion_departamento(departamentos)
        
        self.assertEqual(resultado, 1)
        self.assertEqual(mock_input.call_count, 4)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_seleccion_nacionalidad_valida(self, mock_print, mock_input):
        """Test selección válida de nacionalidad."""
        nacionalidades = ["Dutch", "French", "Italian"]
        mock_input.return_value = "2"
        
        resultado = self.interfaz.solicitar_seleccion_nacionalidad(nacionalidades)
        
        self.assertEqual(resultado, "French")
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_seleccion_nacionalidad_invalida_luego_valida(self, mock_print, mock_input):
        """Test selección inválida de nacionalidad seguida de válida."""
        nacionalidades = ["Dutch", "French"]
        mock_input.side_effect = ["0", "3", "abc", "1"]
        
        resultado = self.interfaz.solicitar_seleccion_nacionalidad(nacionalidades)
        
        self.assertEqual(resultado, "Dutch")
        self.assertEqual(mock_input.call_count, 4)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_nombre_artista_valido(self, mock_print, mock_input):
        """Test solicitud válida de nombre de artista."""
        mock_input.return_value = "Van Gogh"
        
        resultado = self.interfaz.solicitar_nombre_artista()
        
        self.assertEqual(resultado, "Van Gogh")
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_nombre_artista_vacio_luego_valido(self, mock_print, mock_input):
        """Test solicitud de nombre vacío seguido de válido."""
        mock_input.side_effect = ["", "   ", "Picasso"]
        
        resultado = self.interfaz.solicitar_nombre_artista()
        
        self.assertEqual(resultado, "Picasso")
        self.assertEqual(mock_input.call_count, 3)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_id_obra_valido(self, mock_print, mock_input):
        """Test solicitud válida de ID de obra."""
        mock_input.return_value = "436535"
        
        resultado = self.interfaz.solicitar_id_obra()
        
        self.assertEqual(resultado, 436535)
        mock_print.assert_called()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_solicitar_id_obra_invalido_luego_valido(self, mock_print, mock_input):
        """Test solicitud de ID inválido seguido de válido."""
        mock_input.side_effect = ["abc", "12.5", "436535"]
        
        resultado = self.interfaz.solicitar_id_obra()
        
        self.assertEqual(resultado, 436535)
        self.assertEqual(mock_input.call_count, 3)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_lista_obras_con_obras(self, mock_stdout):
        """Test mostrar lista de obras con datos."""
        obras = [self.obra_prueba]
        
        self.interfaz.mostrar_lista_obras(obras)
        
        output = mock_stdout.getvalue()
        self.assertIn("RESULTADOS DE BÚSQUEDA", output)
        self.assertIn("The Starry Night", output)
        self.assertIn("Vincent van Gogh", output)
        self.assertIn("436535", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_lista_obras_vacia(self, mock_stdout):
        """Test mostrar lista vacía de obras."""
        obras = []
        
        self.interfaz.mostrar_lista_obras(obras)
        
        output = mock_stdout.getvalue()
        self.assertIn("No se encontraron obras", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_lista_obras_multiples(self, mock_stdout):
        """Test mostrar múltiples obras."""
        artista2 = Artista("Pablo Picasso", "Spanish", "1881", "1973")
        obra2 = ObraArte(123456, "Guernica", artista2, "Paintings", "1937")
        obras = [self.obra_prueba, obra2]
        
        self.interfaz.mostrar_lista_obras(obras)
        
        output = mock_stdout.getvalue()
        self.assertIn("2 obras encontradas", output)
        self.assertIn("The Starry Night", output)
        self.assertIn("Guernica", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_detalles_obra_completa(self, mock_stdout):
        """Test mostrar detalles completos de obra."""
        self.interfaz.mostrar_detalles_obra(self.obra_prueba)
        
        output = mock_stdout.getvalue()
        self.assertIn("DETALLES DE LA OBRA", output)
        self.assertIn("The Starry Night", output)
        self.assertIn("Vincent van Gogh", output)
        self.assertIn("Dutch", output)
        self.assertIn("1853", output)
        self.assertIn("1890", output)
        self.assertIn("Paintings", output)
        self.assertIn("1889", output)
        self.assertIn("European Paintings", output)
        self.assertIn("Disponible", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_detalles_obra_datos_parciales(self, mock_stdout):
        """Test mostrar detalles de obra con datos parciales."""
        artista_parcial = Artista("Artista Desconocido")
        obra_parcial = ObraArte(123, "Obra Sin Datos", artista_parcial)
        
        self.interfaz.mostrar_detalles_obra(obra_parcial)
        
        output = mock_stdout.getvalue()
        self.assertIn("DETALLES DE LA OBRA", output)
        self.assertIn("Obra Sin Datos", output)
        self.assertIn("Artista Desconocido", output)
        self.assertIn("No disponible", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_mensaje_error(self, mock_stdout):
        """Test mostrar mensaje de error."""
        mensaje = "Error de prueba"
        
        self.interfaz.mostrar_mensaje_error(mensaje)
        
        output = mock_stdout.getvalue()
        self.assertIn("ERROR", output)
        self.assertIn(mensaje, output)
        self.assertIn("!", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_mensaje_info(self, mock_stdout):
        """Test mostrar mensaje informativo."""
        mensaje = "Información de prueba"
        
        self.interfaz.mostrar_mensaje_info(mensaje)
        
        output = mock_stdout.getvalue()
        self.assertIn("INFORMACIÓN", output)
        self.assertIn(mensaje, output)
        self.assertIn("*", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_mostrar_mensaje_exito(self, mock_stdout):
        """Test mostrar mensaje de éxito."""
        mensaje = "Operación exitosa"
        
        self.interfaz.mostrar_mensaje_exito(mensaje)
        
        output = mock_stdout.getvalue()
        self.assertIn("ÉXITO", output)
        self.assertIn(mensaje, output)
        self.assertIn("+", output)
    
    @patch('builtins.input')
    def test_confirmar_accion_si(self, mock_input):
        """Test confirmación positiva."""
        mock_input.return_value = "s"
        
        resultado = self.interfaz.confirmar_accion("¿Continuar?")
        
        self.assertTrue(resultado)
    
    @patch('builtins.input')
    def test_confirmar_accion_no(self, mock_input):
        """Test confirmación negativa."""
        mock_input.return_value = "n"
        
        resultado = self.interfaz.confirmar_accion("¿Continuar?")
        
        self.assertFalse(resultado)
    
    @patch('builtins.input')
    def test_confirmar_accion_respuestas_variadas(self, mock_input):
        """Test confirmación con diferentes respuestas válidas."""
        # Test respuestas positivas
        for respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            mock_input.return_value = respuesta
            resultado = self.interfaz.confirmar_accion("¿Continuar?")
            self.assertTrue(resultado, f"Falló con respuesta: {respuesta}")
        
        # Test respuestas negativas
        for respuesta in ['n', 'no']:
            mock_input.return_value = respuesta
            resultado = self.interfaz.confirmar_accion("¿Continuar?")
            self.assertFalse(resultado, f"Falló con respuesta: {respuesta}")
    
    @patch('builtins.input')
    def test_confirmar_accion_respuesta_invalida_luego_valida(self, mock_input):
        """Test confirmación con respuesta inválida seguida de válida."""
        mock_input.side_effect = ["maybe", "quizás", "s"]
        
        resultado = self.interfaz.confirmar_accion("¿Continuar?")
        
        self.assertTrue(resultado)
        self.assertEqual(mock_input.call_count, 3)
    
    @patch('builtins.input')
    def test_pausar_para_continuar(self, mock_input):
        """Test pausa para continuar."""
        mock_input.return_value = ""
        
        # No debería lanzar excepción
        self.interfaz.pausar_para_continuar()
        
        mock_input.assert_called_once()
    
    @patch('os.system')
    def test_limpiar_pantalla_windows(self, mock_system):
        """Test limpiar pantalla en Windows."""
        with patch('os.name', 'nt'):
            self.interfaz.limpiar_pantalla()
            mock_system.assert_called_once_with('cls')
    
    @patch('os.system')
    def test_limpiar_pantalla_unix(self, mock_system):
        """Test limpiar pantalla en Unix/Linux."""
        with patch('os.name', 'posix'):
            self.interfaz.limpiar_pantalla()
            mock_system.assert_called_once_with('clear')
    
    def test_mostrar_lista_obras_titulo_largo(self):
        """Test mostrar obra con título muy largo (truncamiento)."""
        artista = Artista("Artista")
        titulo_largo = "Este es un título extremadamente largo que debería ser truncado para mantener el formato de la tabla"
        obra_titulo_largo = ObraArte(123, titulo_largo, artista)
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.interfaz.mostrar_lista_obras([obra_titulo_largo])
            output = mock_stdout.getvalue()
            
            # Verificar que el título fue truncado
            self.assertIn("...", output)
            # Verificar que no excede el ancho de columna
            lines = output.split('\n')
            for line in lines:
                if '123' in line:  # Línea con los datos de la obra
                    self.assertLessEqual(len(line), 95)  # Ancho máximo de tabla
    
    def test_mostrar_detalles_obra_sin_imagen(self):
        """Test mostrar detalles de obra sin imagen."""
        artista = Artista("Artista Sin Imagen")
        obra_sin_imagen = ObraArte(456, "Obra Sin Imagen", artista)
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            self.interfaz.mostrar_detalles_obra(obra_sin_imagen)
            output = mock_stdout.getvalue()
            
            self.assertIn("No disponible", output)
            self.assertNotIn("Use la opción de visualización", output)


if __name__ == '__main__':
    unittest.main()
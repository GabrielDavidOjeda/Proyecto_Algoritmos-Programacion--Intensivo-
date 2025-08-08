"""
Tests unitarios para el módulo VisualizadorImagenes.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import tempfile
import os
import requests
from PIL import Image
import tkinter as tk

from ui.visualizador_imagenes import VisualizadorImagenes


class TestVisualizadorImagenes(unittest.TestCase):
    """Tests para la clase VisualizadorImagenes."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Limpiar archivos temporales antes de cada test
        VisualizadorImagenes._archivos_temporales.clear()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        # Limpiar archivos temporales después de cada test
        VisualizadorImagenes.limpiar_cache()
    
    @patch('ui.visualizador_imagenes.messagebox')
    def test_mostrar_imagen_url_vacia(self, mock_messagebox):
        """Test que verifica el manejo de URL vacía."""
        VisualizadorImagenes.mostrar_imagen_en_ventana("", "Obra Test")
        
        mock_messagebox.showwarning.assert_called_once_with(
            "Imagen no disponible", 
            "No hay imagen disponible para la obra: Obra Test"
        )
    
    @patch('ui.visualizador_imagenes.messagebox')
    def test_mostrar_imagen_url_none(self, mock_messagebox):
        """Test que verifica el manejo de URL None."""
        VisualizadorImagenes.mostrar_imagen_en_ventana(None, "Obra Test")
        
        mock_messagebox.showwarning.assert_called_once_with(
            "Imagen no disponible", 
            "No hay imagen disponible para la obra: Obra Test"
        )
    
    @patch('ui.visualizador_imagenes.VisualizadorImagenes._crear_ventana_imagen')
    @patch('ui.visualizador_imagenes.VisualizadorImagenes._descargar_imagen_temporal')
    def test_mostrar_imagen_exitoso(self, mock_descargar, mock_crear_ventana):
        """Test de visualización exitosa de imagen."""
        mock_descargar.return_value = "/tmp/test_image.jpg"
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(
            "https://example.com/image.jpg", 
            "Obra Test"
        )
        
        mock_descargar.assert_called_once_with("https://example.com/image.jpg")
        mock_crear_ventana.assert_called_once_with("/tmp/test_image.jpg", "Obra Test")
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.VisualizadorImagenes._descargar_imagen_temporal')
    def test_mostrar_imagen_error_descarga(self, mock_descargar, mock_messagebox):
        """Test que verifica el manejo de error en descarga."""
        mock_descargar.return_value = None
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(
            "https://example.com/image.jpg", 
            "Obra Test"
        )
        
        mock_messagebox.showerror.assert_called_once_with(
            "Error de descarga", 
            "No se pudo descargar la imagen de: Obra Test"
        )
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.VisualizadorImagenes._descargar_imagen_temporal')
    def test_mostrar_imagen_excepcion_general(self, mock_descargar, mock_messagebox):
        """Test que verifica el manejo de excepciones generales."""
        mock_descargar.side_effect = Exception("Error de prueba")
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(
            "https://example.com/image.jpg", 
            "Obra Test"
        )
        
        mock_messagebox.showerror.assert_called_once_with(
            "Error de visualización", 
            "Error al mostrar la imagen: Error de prueba"
        )
    
    @patch('ui.visualizador_imagenes.tempfile.NamedTemporaryFile')
    @patch('ui.visualizador_imagenes.requests.get')
    def test_descargar_imagen_temporal_exitoso(self, mock_get, mock_tempfile):
        """Test de descarga exitosa de imagen temporal."""
        # Configurar mock de respuesta HTTP
        mock_response = MagicMock()
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Configurar mock de archivo temporal
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_image.jpg"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        resultado = VisualizadorImagenes._descargar_imagen_temporal("https://example.com/image.jpg")
        
        self.assertEqual(resultado, "/tmp/test_image.jpg")
        self.assertIn("/tmp/test_image.jpg", VisualizadorImagenes._archivos_temporales)
        mock_get.assert_called_once_with("https://example.com/image.jpg", timeout=10, stream=True)
        mock_response.raise_for_status.assert_called_once()
    
    @patch('ui.visualizador_imagenes.requests.get')
    def test_descargar_imagen_temporal_content_type_invalido(self, mock_get):
        """Test que verifica el manejo de content-type inválido."""
        mock_response = MagicMock()
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        resultado = VisualizadorImagenes._descargar_imagen_temporal("https://example.com/page.html")
        
        self.assertIsNone(resultado)
    
    @patch('ui.visualizador_imagenes.requests.get')
    def test_descargar_imagen_temporal_request_exception(self, mock_get):
        """Test que verifica el manejo de RequestException."""
        mock_get.side_effect = requests.RequestException("Error de conexión")
        
        resultado = VisualizadorImagenes._descargar_imagen_temporal("https://example.com/image.jpg")
        
        self.assertIsNone(resultado)
    
    @patch('ui.visualizador_imagenes.requests.get')
    def test_descargar_imagen_temporal_excepcion_general(self, mock_get):
        """Test que verifica el manejo de excepciones generales en descarga."""
        mock_get.side_effect = Exception("Error inesperado")
        
        resultado = VisualizadorImagenes._descargar_imagen_temporal("https://example.com/image.jpg")
        
        self.assertIsNone(resultado)
    
    @patch('ui.visualizador_imagenes.tk.Label')
    @patch('ui.visualizador_imagenes.ImageTk.PhotoImage')
    @patch('ui.visualizador_imagenes.Image.open')
    @patch('ui.visualizador_imagenes.tk.Toplevel')
    def test_crear_ventana_imagen_exitoso(self, mock_toplevel, mock_image_open, 
                                        mock_photo_image, mock_label):
        """Test de creación exitosa de ventana de imagen."""
        # Configurar mocks
        mock_ventana = MagicMock()
        mock_toplevel.return_value = mock_ventana
        
        mock_imagen_pil = MagicMock()
        mock_imagen_pil.size = (1000, 800)
        mock_imagen_redimensionada = MagicMock()
        mock_imagen_pil.resize.return_value = mock_imagen_redimensionada
        mock_image_open.return_value = mock_imagen_pil
        
        mock_imagen_tk = MagicMock()
        mock_photo_image.return_value = mock_imagen_tk
        
        mock_label_imagen = MagicMock()
        mock_label_titulo = MagicMock()
        mock_label.side_effect = [mock_label_imagen, mock_label_titulo]
        
        # Ejecutar método
        VisualizadorImagenes._crear_ventana_imagen("/tmp/test.jpg", "Obra Test")
        
        # Verificar llamadas
        mock_ventana.title.assert_called_once_with("Imagen - Obra Test")
        mock_ventana.geometry.assert_called_once_with("800x600")
        mock_image_open.assert_called_once_with("/tmp/test.jpg")
        mock_imagen_pil.resize.assert_called_once()
        mock_photo_image.assert_called_once_with(mock_imagen_redimensionada)
        
        # Verificar que se crearon los labels
        self.assertEqual(mock_label.call_count, 2)
        mock_label_imagen.pack.assert_called_once_with(expand=True)
        mock_label_titulo.pack.assert_called_once_with(pady=10)
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.Image.open')
    @patch('ui.visualizador_imagenes.tk.Toplevel')
    def test_crear_ventana_imagen_error_carga(self, mock_toplevel, mock_image_open, mock_messagebox):
        """Test que verifica el manejo de error al cargar imagen."""
        mock_ventana = MagicMock()
        mock_toplevel.return_value = mock_ventana
        mock_image_open.side_effect = Exception("Error al abrir imagen")
        
        VisualizadorImagenes._crear_ventana_imagen("/tmp/test.jpg", "Obra Test")
        
        mock_messagebox.showerror.assert_called_once_with(
            "Error", 
            "No se pudo cargar la imagen: Error al abrir imagen"
        )
        mock_ventana.destroy.assert_called_once()
    
    @patch('ui.visualizador_imagenes.os.path.exists')
    @patch('ui.visualizador_imagenes.os.remove')
    def test_limpiar_archivos_temporales(self, mock_remove, mock_exists):
        """Test de limpieza de archivos temporales."""
        # Agregar archivos temporales de prueba
        VisualizadorImagenes._archivos_temporales = [
            "/tmp/file1.jpg", 
            "/tmp/file2.jpg", 
            "/tmp/file3.jpg"
        ]
        
        mock_exists.return_value = True
        
        VisualizadorImagenes._limpiar_archivos_temporales()
        
        # Verificar que se intentó eliminar cada archivo
        expected_calls = [call("/tmp/file1.jpg"), call("/tmp/file2.jpg"), call("/tmp/file3.jpg")]
        mock_remove.assert_has_calls(expected_calls)
        
        # Verificar que la lista se limpió
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 0)
    
    @patch('ui.visualizador_imagenes.os.path.exists')
    @patch('ui.visualizador_imagenes.os.remove')
    def test_limpiar_archivos_temporales_archivo_no_existe(self, mock_remove, mock_exists):
        """Test de limpieza cuando el archivo no existe."""
        VisualizadorImagenes._archivos_temporales = ["/tmp/nonexistent.jpg"]
        mock_exists.return_value = False
        
        VisualizadorImagenes._limpiar_archivos_temporales()
        
        # No debería intentar eliminar archivo que no existe
        mock_remove.assert_not_called()
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 0)
    
    @patch('ui.visualizador_imagenes.os.path.exists')
    @patch('ui.visualizador_imagenes.os.remove')
    def test_limpiar_archivos_temporales_os_error(self, mock_remove, mock_exists):
        """Test de limpieza con error de OS."""
        VisualizadorImagenes._archivos_temporales = ["/tmp/protected.jpg"]
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        
        # No debería lanzar excepción
        VisualizadorImagenes._limpiar_archivos_temporales()
        
        # La lista debería limpiarse aunque haya error
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 0)
    
    @patch('ui.visualizador_imagenes.VisualizadorImagenes._limpiar_archivos_temporales')
    def test_limpiar_cache_publico(self, mock_limpiar):
        """Test del método público limpiar_cache."""
        VisualizadorImagenes.limpiar_cache()
        mock_limpiar.assert_called_once()


if __name__ == '__main__':
    unittest.main()
"""
Tests de integración para el módulo VisualizadorImagenes.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from ui.visualizador_imagenes import VisualizadorImagenes


class TestIntegracionVisualizadorImagenes(unittest.TestCase):
    """Tests de integración para VisualizadorImagenes."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        VisualizadorImagenes._archivos_temporales.clear()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        VisualizadorImagenes.limpiar_cache()
    
    @patch('ui.visualizador_imagenes.tk.Toplevel')
    @patch('ui.visualizador_imagenes.tk.Label')
    @patch('ui.visualizador_imagenes.ImageTk.PhotoImage')
    @patch('ui.visualizador_imagenes.Image.open')
    @patch('ui.visualizador_imagenes.tempfile.NamedTemporaryFile')
    @patch('ui.visualizador_imagenes.requests.get')
    def test_flujo_completo_visualizacion_exitosa(self, mock_get, mock_tempfile, 
                                                 mock_image_open, mock_photo_image, 
                                                 mock_label, mock_toplevel):
        """Test del flujo completo de visualización exitosa."""
        # Configurar mock de respuesta HTTP
        mock_response = MagicMock()
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_get.return_value = mock_response
        
        # Configurar mock de archivo temporal
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_image.jpg"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Configurar mock de ventana Tkinter
        mock_ventana = MagicMock()
        mock_toplevel.return_value = mock_ventana
        
        # Configurar mock de imagen PIL
        mock_imagen_pil = MagicMock()
        mock_imagen_pil.size = (800, 600)
        mock_imagen_redimensionada = MagicMock()
        mock_imagen_pil.resize.return_value = mock_imagen_redimensionada
        mock_image_open.return_value = mock_imagen_pil
        
        # Configurar mock de ImageTk
        mock_imagen_tk = MagicMock()
        mock_photo_image.return_value = mock_imagen_tk
        
        # Configurar mock de labels
        mock_label_imagen = MagicMock()
        mock_label_titulo = MagicMock()
        mock_label.side_effect = [mock_label_imagen, mock_label_titulo]
        
        # Ejecutar el flujo completo
        url_test = "https://images.metmuseum.org/CRDImages/ep/original/DT1567.jpg"
        titulo_test = "The Harvesters"
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(url_test, titulo_test)
        
        # Verificar que se realizó la descarga
        mock_get.assert_called_once_with(url_test, timeout=10, stream=True)
        mock_response.raise_for_status.assert_called_once()
        
        # Verificar que se creó el archivo temporal
        mock_tempfile.assert_called_once()
        mock_file.write.assert_called_once_with(b'fake_image_data')
        
        # Verificar que se agregó a la lista de archivos temporales
        self.assertIn("/tmp/test_image.jpg", VisualizadorImagenes._archivos_temporales)
        
        # Verificar que se creó la ventana
        mock_ventana.title.assert_called_once_with(f"Imagen - {titulo_test}")
        mock_ventana.geometry.assert_called_once_with("800x600")
        
        # Verificar que se cargó y procesó la imagen
        mock_image_open.assert_called_once_with("/tmp/test_image.jpg")
        mock_imagen_pil.resize.assert_called_once()
        mock_photo_image.assert_called_once_with(mock_imagen_redimensionada)
        
        # Verificar que se crearon los elementos de UI
        self.assertEqual(mock_label.call_count, 2)
        mock_label_imagen.pack.assert_called_once_with(expand=True)
        mock_label_titulo.pack.assert_called_once_with(pady=10)
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.requests.get')
    def test_flujo_completo_error_conexion(self, mock_get, mock_messagebox):
        """Test del flujo completo con error de conexión."""
        # Simular error de conexión - esto hace que _descargar_imagen_temporal retorne None
        mock_get.side_effect = Exception("Connection timeout")
        
        url_test = "https://images.metmuseum.org/invalid.jpg"
        titulo_test = "Obra Inexistente"
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(url_test, titulo_test)
        
        # Verificar que se mostró el mensaje de error de descarga (no de visualización)
        # porque el error ocurre en la descarga, no en la visualización
        mock_messagebox.showerror.assert_called_once_with(
            "Error de descarga", 
            "No se pudo descargar la imagen de: Obra Inexistente"
        )
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.requests.get')
    def test_flujo_completo_contenido_no_imagen(self, mock_get, mock_messagebox):
        """Test del flujo completo con contenido que no es imagen."""
        # Configurar respuesta que no es imagen
        mock_response = MagicMock()
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        url_test = "https://example.com/notanimage.html"
        titulo_test = "No es imagen"
        
        VisualizadorImagenes.mostrar_imagen_en_ventana(url_test, titulo_test)
        
        # Verificar que se mostró el mensaje de error de descarga
        mock_messagebox.showerror.assert_called_once_with(
            "Error de descarga", 
            "No se pudo descargar la imagen de: No es imagen"
        )
    
    def test_limpieza_archivos_multiples_llamadas(self):
        """Test de limpieza de archivos con múltiples llamadas."""
        # Simular archivos temporales
        archivos_test = ["/tmp/file1.jpg", "/tmp/file2.jpg", "/tmp/file3.jpg"]
        VisualizadorImagenes._archivos_temporales.extend(archivos_test)
        
        # Verificar que hay archivos en la lista
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 3)
        
        # Limpiar cache
        with patch('ui.visualizador_imagenes.os.path.exists', return_value=False):
            VisualizadorImagenes.limpiar_cache()
        
        # Verificar que se limpió la lista
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 0)
        
        # Llamar limpiar_cache nuevamente no debería causar error
        VisualizadorImagenes.limpiar_cache()
        self.assertEqual(len(VisualizadorImagenes._archivos_temporales), 0)
    
    @patch('ui.visualizador_imagenes.messagebox')
    @patch('ui.visualizador_imagenes.requests.get')
    def test_casos_edge_urls(self, mock_get, mock_messagebox):
        """Test de casos edge con diferentes tipos de URLs."""
        casos_test = [
            ("", "URL vacía"),
            ("   ", "URL con espacios"),
            (None, "URL None")
        ]
        
        for url, descripcion in casos_test:
            with self.subTest(url=url, descripcion=descripcion):
                VisualizadorImagenes.mostrar_imagen_en_ventana(url, f"Obra {descripcion}")
                
                # Estos casos deberían mostrar el warning de imagen no disponible
                mock_messagebox.showwarning.assert_called_with(
                    "Imagen no disponible", 
                    f"No hay imagen disponible para la obra: Obra {descripcion}"
                )
                mock_messagebox.reset_mock()
        
        # Caso especial: URL inválida que intenta hacer request
        mock_get.side_effect = Exception("Invalid URL")
        VisualizadorImagenes.mostrar_imagen_en_ventana("not_a_url", "Obra URL inválida")
        
        # Este caso debería mostrar error de descarga
        mock_messagebox.showerror.assert_called_with(
            "Error de descarga", 
            "No se pudo descargar la imagen de: Obra URL inválida"
        )


if __name__ == '__main__':
    unittest.main()
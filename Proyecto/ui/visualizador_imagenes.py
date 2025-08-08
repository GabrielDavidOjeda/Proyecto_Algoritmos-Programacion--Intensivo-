"""
Módulo para visualización de imágenes de obras de arte.
Permite mostrar imágenes en ventanas separadas descargándolas temporalmente desde URLs.
"""

import os
import tempfile
import requests
from typing import Optional
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox


class VisualizadorImagenes:
    """
    Clase para visualizar imágenes de obras de arte en ventanas separadas.
    Maneja la descarga temporal de imágenes y su limpieza automática.
    """
    
    _archivos_temporales = []
    
    @classmethod
    def mostrar_imagen_en_ventana(cls, url_imagen: str, titulo_obra: str) -> None:
        """
        Muestra una imagen en una ventana separada.
        
        Args:
            url_imagen: URL de la imagen a mostrar
            titulo_obra: Título de la obra para mostrar en la ventana
            
        Raises:
            Exception: Si hay error en la descarga o visualización
        """
        if not url_imagen or url_imagen.strip() == "":
            messagebox.showwarning("Imagen no disponible", 
                                 f"No hay imagen disponible para la obra: {titulo_obra}")
            return
            
        try:
            # Descargar imagen temporal
            ruta_temporal = cls._descargar_imagen_temporal(url_imagen)
            if not ruta_temporal:
                messagebox.showerror("Error de descarga", 
                                   f"No se pudo descargar la imagen de: {titulo_obra}")
                return
            
            # Crear ventana para mostrar la imagen
            cls._crear_ventana_imagen(ruta_temporal, titulo_obra)
            
        except Exception as e:
            messagebox.showerror("Error de visualización", 
                               f"Error al mostrar la imagen: {str(e)}")
    
    @classmethod
    def _descargar_imagen_temporal(cls, url: str) -> Optional[str]:
        """
        Descarga una imagen desde una URL a un archivo temporal.
        
        Args:
            url: URL de la imagen a descargar
            
        Returns:
            Ruta del archivo temporal o None si hay error
        """
        try:
            # Realizar petición HTTP con timeout
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Verificar que el contenido sea una imagen
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return None
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                
                ruta_temporal = temp_file.name
                cls._archivos_temporales.append(ruta_temporal)
                return ruta_temporal
                
        except requests.RequestException:
            return None
        except Exception:
            return None
    
    @classmethod
    def _crear_ventana_imagen(cls, ruta_imagen: str, titulo_obra: str) -> None:
        """
        Crea una ventana Tkinter para mostrar la imagen.
        
        Args:
            ruta_imagen: Ruta del archivo de imagen
            titulo_obra: Título para la ventana
        """
        # Crear ventana principal
        ventana = tk.Toplevel()
        ventana.title(f"Imagen - {titulo_obra}")
        ventana.geometry("800x600")
        
        try:
            # Cargar y redimensionar imagen
            imagen_pil = Image.open(ruta_imagen)
            
            # Calcular dimensiones manteniendo proporción
            ancho_max, alto_max = 750, 550
            ancho_orig, alto_orig = imagen_pil.size
            
            ratio = min(ancho_max/ancho_orig, alto_max/alto_orig)
            nuevo_ancho = int(ancho_orig * ratio)
            nuevo_alto = int(alto_orig * ratio)
            
            imagen_redimensionada = imagen_pil.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
            
            # Crear label para mostrar la imagen
            label_imagen = tk.Label(ventana, image=imagen_tk)
            label_imagen.image = imagen_tk  # Mantener referencia
            label_imagen.pack(expand=True)
            
            # Agregar título debajo de la imagen
            label_titulo = tk.Label(ventana, text=titulo_obra, font=("Arial", 12, "bold"))
            label_titulo.pack(pady=10)
            
            # Configurar cierre de ventana para limpiar archivos
            def al_cerrar():
                cls._limpiar_archivos_temporales()
                ventana.destroy()
            
            ventana.protocol("WM_DELETE_WINDOW", al_cerrar)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
            ventana.destroy()
    
    @classmethod
    def _limpiar_archivos_temporales(cls) -> None:
        """
        Elimina todos los archivos temporales creados.
        """
        for archivo in cls._archivos_temporales:
            try:
                if os.path.exists(archivo):
                    os.remove(archivo)
            except OSError:
                pass  # Ignorar errores de eliminación
        
        cls._archivos_temporales.clear()
    
    @classmethod
    def limpiar_cache(cls) -> None:
        """
        Método público para limpiar el cache de archivos temporales.
        Útil para llamar al finalizar la aplicación.
        """
        cls._limpiar_archivos_temporales()
"""
Modelo de datos para representar una obra de arte en el sistema de catálogo del museo.
"""

from typing import Optional
from .artista import Artista


class ObraArte:
    """
    Clase que representa una obra de arte con relación a un artista.
    
    Attributes:
        _id_obra (int): ID único de la obra
        _titulo (str): Título de la obra
        _artista (Artista): Artista que creó la obra
        _clasificacion (str): Clasificación o tipo de obra
        _fecha_creacion (str): Fecha de creación de la obra
        _url_imagen (str): URL de la imagen de la obra
        _departamento (str): Departamento del museo donde se encuentra
    """
    
    def __init__(self, id_obra: int, titulo: str, artista: Artista,
                 clasificacion: str = None, fecha_creacion: str = None,
                 url_imagen: str = None, departamento: str = None):
        """
        Inicializa una nueva obra de arte.
        
        Args:
            id_obra (int): ID único de la obra (requerido)
            titulo (str): Título de la obra (requerido)
            artista (Artista): Artista que creó la obra (requerido)
            clasificacion (str, optional): Clasificación de la obra
            fecha_creacion (str, optional): Fecha de creación
            url_imagen (str, optional): URL de la imagen
            departamento (str, optional): Departamento del museo
        """
        if not isinstance(id_obra, int) or id_obra <= 0:
            raise ValueError("El ID de la obra debe ser un entero positivo")
        
        if not titulo or not isinstance(titulo, str):
            raise ValueError("El título de la obra es requerido y debe ser una cadena")
        
        titulo_limpio = titulo.strip()
        if not titulo_limpio:
            raise ValueError("El título de la obra es requerido y debe ser una cadena")
        
        if not isinstance(artista, Artista):
            raise ValueError("El artista debe ser una instancia de la clase Artista")
        
        self._id_obra = id_obra
        self._titulo = titulo_limpio
        self._artista = artista
        self._clasificacion = clasificacion.strip() if clasificacion else None
        self._fecha_creacion = fecha_creacion.strip() if fecha_creacion else None
        self._url_imagen = url_imagen.strip() if url_imagen else None
        self._departamento = departamento.strip() if departamento else None
    
    @property
    def id_obra(self) -> int:
        """Obtiene el ID de la obra."""
        return self._id_obra
    
    @property
    def titulo(self) -> str:
        """Obtiene el título de la obra."""
        return self._titulo
    
    @property
    def artista(self) -> Artista:
        """Obtiene el artista de la obra."""
        return self._artista
    
    @property
    def clasificacion(self) -> Optional[str]:
        """Obtiene la clasificación de la obra."""
        return self._clasificacion
    
    @property
    def fecha_creacion(self) -> Optional[str]:
        """Obtiene la fecha de creación de la obra."""
        return self._fecha_creacion
    
    @property
    def url_imagen(self) -> Optional[str]:
        """Obtiene la URL de la imagen de la obra."""
        return self._url_imagen
    
    @property
    def departamento(self) -> Optional[str]:
        """Obtiene el departamento de la obra."""
        return self._departamento
    
    @titulo.setter
    def titulo(self, valor: str):
        """Establece el título de la obra."""
        if not valor or not isinstance(valor, str):
            raise ValueError("El título de la obra es requerido y debe ser una cadena")
        titulo_limpio = valor.strip()
        if not titulo_limpio:
            raise ValueError("El título de la obra es requerido y debe ser una cadena")
        self._titulo = titulo_limpio
    
    @artista.setter
    def artista(self, valor: Artista):
        """Establece el artista de la obra."""
        if not isinstance(valor, Artista):
            raise ValueError("El artista debe ser una instancia de la clase Artista")
        self._artista = valor
    
    @clasificacion.setter
    def clasificacion(self, valor: str):
        """Establece la clasificación de la obra."""
        self._clasificacion = valor.strip() if valor else None
    
    @fecha_creacion.setter
    def fecha_creacion(self, valor: str):
        """Establece la fecha de creación de la obra."""
        self._fecha_creacion = valor.strip() if valor else None
    
    @url_imagen.setter
    def url_imagen(self, valor: str):
        """Establece la URL de la imagen de la obra."""
        self._url_imagen = valor.strip() if valor else None
    
    @departamento.setter
    def departamento(self, valor: str):
        """Establece el departamento de la obra."""
        self._departamento = valor.strip() if valor else None
    
    def mostrar_resumen(self) -> str:
        """
        Muestra un resumen de la obra para listados.
        
        Returns:
            str: Resumen formateado con ID, título y nombre del artista
        """
        return f"ID: {self._id_obra} | {self._titulo} | {self._artista.nombre}"
    
    def mostrar_detalles_completos(self) -> str:
        """
        Muestra los detalles completos de la obra.
        
        Returns:
            str: Detalles completos formateados de la obra
        """
        detalles = []
        detalles.append(f"ID de la Obra: {self._id_obra}")
        detalles.append(f"Título: {self._titulo}")
        detalles.append(f"Artista: {self._artista}")
        
        if self._clasificacion:
            detalles.append(f"Tipo: {self._clasificacion}")
        
        if self._fecha_creacion:
            detalles.append(f"Año de creación: {self._fecha_creacion}")
        
        if self._departamento:
            detalles.append(f"Departamento: {self._departamento}")
        
        if self._url_imagen:
            detalles.append(f"Imagen disponible: Sí")
        else:
            detalles.append(f"Imagen disponible: No")
        
        return "\n".join(detalles)
    
    def tiene_imagen(self) -> bool:
        """
        Verifica si la obra tiene una imagen disponible.
        
        Returns:
            bool: True si tiene imagen, False en caso contrario
        """
        return self._url_imagen is not None and len(self._url_imagen) > 0
    
    def obtener_info_artista(self) -> dict:
        """
        Obtiene información del artista en formato diccionario.
        
        Returns:
            dict: Información del artista
        """
        return {
            'nombre': self._artista.nombre,
            'nacionalidad': self._artista.nacionalidad,
            'fecha_nacimiento': self._artista.fecha_nacimiento,
            'fecha_muerte': self._artista.fecha_muerte,
            'periodo_vida': self._artista.obtener_periodo_vida()
        }
    
    def __str__(self) -> str:
        """Representación en cadena de la obra."""
        return f'"{self._titulo}" por {self._artista.nombre} (ID: {self._id_obra})'
    
    def __repr__(self) -> str:
        """Representación técnica de la obra."""
        return (f"ObraArte(id_obra={self._id_obra}, titulo='{self._titulo}', "
                f"artista={repr(self._artista)}, clasificacion='{self._clasificacion}', "
                f"fecha_creacion='{self._fecha_creacion}')")
    
    def __eq__(self, other) -> bool:
        """Compara dos obras por igualdad."""
        if not isinstance(other, ObraArte):
            return False
        return self._id_obra == other._id_obra
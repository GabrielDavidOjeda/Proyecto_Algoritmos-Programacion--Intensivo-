"""
Gestor de Nacionalidades para el sistema de catálogo del museo.
Maneja la carga y validación de nacionalidades desde archivo externo.
"""

import os
import logging
from typing import List, Optional


class ErrorArchivoNacionalidades(Exception):
    """Excepción personalizada para errores relacionados con el archivo de nacionalidades."""
    pass


class GestorNacionalidades:
    """
    Clase para gestionar la carga y validación de nacionalidades desde archivo.
    
    Esta clase se encarga de:
    - Cargar nacionalidades desde un archivo de texto
    - Validar nacionalidades contra la lista cargada
    - Proporcionar acceso a las nacionalidades disponibles
    """
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el gestor con la ruta del archivo de nacionalidades.
        
        Args:
            ruta_archivo (str): Ruta al archivo que contiene las nacionalidades
        """
        self._ruta_archivo = ruta_archivo
        self._nacionalidades: List[str] = []
        self._archivo_cargado = False
        self.logger = logging.getLogger(__name__)
    
    def cargar_nacionalidades(self) -> None:
        """
        Carga las nacionalidades desde el archivo especificado.
        
        Raises:
            ErrorArchivoNacionalidades: Si el archivo no existe, no se puede leer,
                                      o está vacío
        """
        self.logger.info(f"Cargando nacionalidades desde: {self._ruta_archivo}")
        
        try:
            if not os.path.exists(self._ruta_archivo):
                raise ErrorArchivoNacionalidades(
                    f"El archivo de nacionalidades no existe: {self._ruta_archivo}"
                )
            
            if not os.path.isfile(self._ruta_archivo):
                raise ErrorArchivoNacionalidades(
                    f"La ruta especificada no es un archivo: {self._ruta_archivo}"
                )
            
            self._nacionalidades = self._procesar_archivo_nacionalidades()
            
            if not self._nacionalidades:
                raise ErrorArchivoNacionalidades(
                    f"El archivo de nacionalidades está vacío: {self._ruta_archivo}"
                )
            
            self._archivo_cargado = True
            self.logger.info(f"Nacionalidades cargadas exitosamente: {len(self._nacionalidades)} elementos")
            
        except IOError as e:
            raise ErrorArchivoNacionalidades(
                f"Error al leer el archivo de nacionalidades: {str(e)}"
            )
        except Exception as e:
            raise ErrorArchivoNacionalidades(
                f"Error inesperado al cargar nacionalidades: {str(e)}"
            )
    
    def obtener_nacionalidades_disponibles(self) -> List[str]:
        """
        Obtiene la lista de nacionalidades disponibles.
        
        Returns:
            List[str]: Lista de nacionalidades cargadas desde el archivo
            
        Raises:
            ErrorArchivoNacionalidades: Si las nacionalidades no han sido cargadas
        """
        if not self._archivo_cargado:
            raise ErrorArchivoNacionalidades(
                "Las nacionalidades no han sido cargadas. "
                "Llame a cargar_nacionalidades() primero."
            )
        
        return self._nacionalidades.copy()
    
    def validar_nacionalidad(self, nacionalidad: str) -> bool:
        """
        Valida si una nacionalidad específica está en la lista cargada.
        
        Args:
            nacionalidad (str): La nacionalidad a validar
            
        Returns:
            bool: True si la nacionalidad es válida, False en caso contrario
            
        Raises:
            ErrorArchivoNacionalidades: Si las nacionalidades no han sido cargadas
        """
        if not self._archivo_cargado:
            raise ErrorArchivoNacionalidades(
                "Las nacionalidades no han sido cargadas. "
                "Llame a cargar_nacionalidades() primero."
            )
        
        if not nacionalidad:
            return False
        
        # Búsqueda case-insensitive para mayor flexibilidad
        nacionalidad_normalizada = nacionalidad.strip().lower()
        return any(
            nac.lower() == nacionalidad_normalizada 
            for nac in self._nacionalidades
        )
    
    def _procesar_archivo_nacionalidades(self) -> List[str]:
        """
        Procesa el archivo de nacionalidades y extrae las nacionalidades.
        
        Returns:
            List[str]: Lista de nacionalidades procesadas
            
        Raises:
            IOError: Si hay problemas al leer el archivo
        """
        nacionalidades = []
        
        with open(self._ruta_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                # Limpiar espacios en blanco y saltos de línea
                nacionalidad = linea.strip()
                
                # Ignorar líneas vacías y comentarios (líneas que empiezan con #)
                if nacionalidad and not nacionalidad.startswith('#'):
                    nacionalidades.append(nacionalidad)
        
        # Eliminar duplicados manteniendo el orden
        nacionalidades_unicas = []
        for nacionalidad in nacionalidades:
            if nacionalidad not in nacionalidades_unicas:
                nacionalidades_unicas.append(nacionalidad)
        
        return nacionalidades_unicas
    
    @property
    def archivo_cargado(self) -> bool:
        """
        Indica si el archivo de nacionalidades ha sido cargado exitosamente.
        
        Returns:
            bool: True si el archivo ha sido cargado, False en caso contrario
        """
        return self._archivo_cargado
    
    @property
    def ruta_archivo(self) -> str:
        """
        Obtiene la ruta del archivo de nacionalidades.
        
        Returns:
            str: Ruta del archivo de nacionalidades
        """
        return self._ruta_archivo
    
    def __len__(self) -> int:
        """
        Obtiene el número de nacionalidades cargadas.
        
        Returns:
            int: Número de nacionalidades disponibles
        """
        return len(self._nacionalidades) if self._archivo_cargado else 0
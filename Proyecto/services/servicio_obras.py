"""
Servicio para gestionar detalles de obras de arte.
Proporciona funcionalidades para obtener y validar información completa de obras.
Incluye sistema de cache para optimizar rendimiento.
"""

from typing import Optional
from models.obra_arte import ObraArte
from models.artista import Artista
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from ui.visualizador_imagenes import VisualizadorImagenes
from utils.almacen_datos import AlmacenDatos


class ServicioObras:
    """
    Servicio para gestionar detalles completos de obras de arte.
    
    Este servicio se encarga de obtener información detallada de obras específicas,
    validar los datos recibidos de la API y formatear la información para visualización.
    """
    
    def __init__(self, cliente_api: ClienteAPIMetMuseum, 
                 visualizador_imagenes: Optional[VisualizadorImagenes] = None,
                 almacen_datos: Optional[AlmacenDatos] = None):
        """
        Inicializa el servicio de obras.
        
        Args:
            cliente_api (ClienteAPIMetMuseum): Cliente para acceder a la API del museo
            visualizador_imagenes (Optional[VisualizadorImagenes]): Visualizador de imágenes
            almacen_datos (Optional[AlmacenDatos]): Sistema de cache de datos
        """
        if not isinstance(cliente_api, ClienteAPIMetMuseum):
            raise ValueError("cliente_api debe ser una instancia de ClienteAPIMetMuseum")
        
        self._cliente_api = cliente_api
        self._visualizador_imagenes = visualizador_imagenes or VisualizadorImagenes()
        self._almacen_datos = almacen_datos or AlmacenDatos()
    
    def obtener_detalles_obra(self, id_obra: int) -> ObraArte:
        """
        Obtiene los detalles completos de una obra específica con cache optimizado.
        
        Args:
            id_obra (int): ID único de la obra
            
        Returns:
            ObraArte: Objeto con los detalles completos de la obra
            
        Raises:
            ValueError: Si el ID de obra no es válido
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado: Si la obra no existe
            ExcepcionesAPIMetMuseum.ErrorConexionAPI: Si hay problemas de conexión
            ExcepcionesAPIMetMuseum.ErrorDatosIncompletos: Si los datos están incompletos
        """
        # Validar ID de obra
        if not isinstance(id_obra, int) or id_obra <= 0:
            raise ValueError("El ID de la obra debe ser un entero positivo")
        
        try:
            # Intentar obtener obra del cache primero
            obra = self._almacen_datos.obtener_obra(id_obra)
            
            if obra is not None:
                return obra
            
            # No está en cache, obtener de la API
            datos_api = self._cliente_api.obtener_detalles_obra(id_obra)
            
            # Validar datos completos
            if not self._validar_datos_obra(datos_api):
                raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                    f"Datos incompletos para la obra {id_obra}"
                )
            
            # Convertir datos de API a objeto ObraArte
            obra = self._convertir_datos_api_a_obra(datos_api)
            
            # Almacenar en cache para futuras consultas
            self._almacen_datos.almacenar_obra(obra)
            
            return obra
            
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum:
            # Re-lanzar excepciones específicas de la API
            raise
        except Exception as e:
            # Convertir otras excepciones en errores de datos incompletos
            raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                f"Error al procesar datos de la obra {id_obra}: {str(e)}"
            )
    
    def formatear_detalles_completos(self, obra: ObraArte) -> str:
        """
        Formatea los detalles completos de una obra para visualización.
        
        Args:
            obra (ObraArte): Obra a formatear
            
        Returns:
            str: Detalles formateados para mostrar al usuario
            
        Raises:
            ValueError: Si la obra no es válida
        """
        if not isinstance(obra, ObraArte):
            raise ValueError("El parámetro debe ser una instancia de ObraArte")
        
        lineas = []
        lineas.append("=" * 60)
        lineas.append("DETALLES DE LA OBRA")
        lineas.append("=" * 60)
        lineas.append("")
        
        # Información básica de la obra
        lineas.append(f"ID de la Obra: {obra.id_obra}")
        lineas.append(f"Título: {obra.titulo}")
        lineas.append("")
        
        # Información del artista
        lineas.append("INFORMACIÓN DEL ARTISTA:")
        lineas.append(f"  Nombre: {obra.artista.nombre}")
        
        if obra.artista.nacionalidad:
            lineas.append(f"  Nacionalidad: {obra.artista.nacionalidad}")
        
        if obra.artista.fecha_nacimiento or obra.artista.fecha_muerte:
            periodo = obra.artista.obtener_periodo_vida()
            lineas.append(f"  Período de vida: {periodo}")
        
        lineas.append("")
        
        # Información adicional de la obra
        if obra.clasificacion:
            lineas.append(f"Tipo: {obra.clasificacion}")
        
        if obra.fecha_creacion:
            lineas.append(f"Año de creación: {obra.fecha_creacion}")
        
        if obra.departamento:
            lineas.append(f"Departamento: {obra.departamento}")
        
        # Estado de imagen
        if obra.tiene_imagen():
            lineas.append("Imagen: Disponible")
        else:
            lineas.append("Imagen: No disponible")
        
        lineas.append("")
        lineas.append("=" * 60)
        
        return "\n".join(lineas)
    
    def mostrar_imagen_obra(self, obra: ObraArte) -> None:
        """
        Muestra la imagen de una obra de arte en una ventana separada.
        
        Args:
            obra (ObraArte): Obra de arte cuya imagen se desea mostrar
            
        Raises:
            ValueError: Si la obra no es válida
            Exception: Si hay error en la visualización de la imagen
        """
        if not isinstance(obra, ObraArte):
            raise ValueError("El parámetro debe ser una instancia de ObraArte")
        
        if not obra.tiene_imagen():
            raise ValueError(f"La obra '{obra.titulo}' no tiene imagen disponible")
        
        try:
            titulo_completo = f"{obra.titulo} - {obra.artista.nombre}"
            self._visualizador_imagenes.mostrar_imagen_en_ventana(obra.url_imagen, titulo_completo)
        except Exception as e:
            raise Exception(f"Error al mostrar imagen de la obra: {str(e)}")
    
    def _validar_datos_obra(self, datos: dict) -> bool:
        """
        Valida que los datos de una obra contengan la información mínima requerida.
        
        Args:
            datos (dict): Datos de la obra obtenidos de la API
            
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        if not isinstance(datos, dict):
            return False
        
        # Campos obligatorios
        campos_obligatorios = ['objectID', 'title']
        for campo in campos_obligatorios:
            if campo not in datos or datos[campo] is None:
                return False
            
            # Validar que los campos de texto no estén vacíos
            if campo == 'title' and not str(datos[campo]).strip():
                return False
        
        # Validar que objectID sea un entero positivo
        try:
            object_id = int(datos['objectID'])
            if object_id <= 0:
                return False
        except (ValueError, TypeError):
            return False
        
        return True
    
    def _convertir_datos_api_a_obra(self, datos_api: dict) -> ObraArte:
        """
        Convierte los datos de la API en un objeto ObraArte.
        
        Args:
            datos_api (dict): Datos de la obra obtenidos de la API
            
        Returns:
            ObraArte: Objeto obra de arte creado a partir de los datos
            
        Raises:
            ValueError: Si los datos no pueden ser convertidos
        """
        try:
            # Extraer información del artista
            nombre_artista = self._extraer_nombre_artista(datos_api)
            nacionalidad = self._extraer_campo_opcional(datos_api, 'artistNationality')
            fecha_nacimiento = self._extraer_campo_opcional(datos_api, 'artistBeginDate')
            fecha_muerte = self._extraer_campo_opcional(datos_api, 'artistEndDate')
            
            # Crear objeto Artista
            artista = Artista(
                nombre=nombre_artista,
                nacionalidad=nacionalidad,
                fecha_nacimiento=fecha_nacimiento,
                fecha_muerte=fecha_muerte
            )
            
            # Extraer información de la obra
            id_obra = int(datos_api['objectID'])
            titulo = str(datos_api['title']).strip()
            clasificacion = self._extraer_campo_opcional(datos_api, 'classification')
            fecha_creacion = self._extraer_campo_opcional(datos_api, 'objectDate')
            url_imagen = self._extraer_url_imagen(datos_api)
            departamento = self._extraer_campo_opcional(datos_api, 'department')
            
            # Crear y retornar objeto ObraArte
            return ObraArte(
                id_obra=id_obra,
                titulo=titulo,
                artista=artista,
                clasificacion=clasificacion,
                fecha_creacion=fecha_creacion,
                url_imagen=url_imagen,
                departamento=departamento
            )
            
        except Exception as e:
            raise ValueError(f"Error al convertir datos de API a ObraArte: {str(e)}")
    
    def _extraer_nombre_artista(self, datos_api: dict) -> str:
        """
        Extrae el nombre del artista de los datos de la API.
        
        Args:
            datos_api (dict): Datos de la API
            
        Returns:
            str: Nombre del artista o "Artista desconocido" si no está disponible
        """
        # Intentar diferentes campos para el nombre del artista
        campos_nombre = ['artistDisplayName', 'artistName', 'artist']
        
        for campo in campos_nombre:
            if campo in datos_api and datos_api[campo]:
                nombre = str(datos_api[campo]).strip()
                if nombre:
                    return nombre
        
        return "Artista desconocido"
    
    def _extraer_campo_opcional(self, datos_api: dict, campo: str) -> Optional[str]:
        """
        Extrae un campo opcional de los datos de la API.
        
        Args:
            datos_api (dict): Datos de la API
            campo (str): Nombre del campo a extraer
            
        Returns:
            Optional[str]: Valor del campo o None si no está disponible
        """
        if campo in datos_api and datos_api[campo]:
            valor = str(datos_api[campo]).strip()
            return valor if valor else None
        return None
    
    def _extraer_url_imagen(self, datos_api: dict) -> Optional[str]:
        """
        Extrae la URL de la imagen de los datos de la API.
        
        Args:
            datos_api (dict): Datos de la API
            
        Returns:
            Optional[str]: URL de la imagen o None si no está disponible
        """
        # Intentar diferentes campos para la imagen
        campos_imagen = ['primaryImage', 'primaryImageSmall', 'image']
        
        for campo in campos_imagen:
            if campo in datos_api and datos_api[campo]:
                url = str(datos_api[campo]).strip()
                if url and url.startswith(('http://', 'https://')):
                    return url
        
        return None
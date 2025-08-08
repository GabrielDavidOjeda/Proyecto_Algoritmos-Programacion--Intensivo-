"""
Servicio de búsqueda para el sistema de catálogo del museo.
Proporciona funcionalidades de búsqueda por departamento, nacionalidad y artista.
Incluye sistema de cache para optimizar rendimiento.
"""

import logging
from typing import List, Optional
from models.artista import Artista
from models.obra_arte import ObraArte
from models.departamento import Departamento
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from utils.gestor_nacionalidades import GestorNacionalidades
from utils.almacen_datos import AlmacenDatos


class ExcepcionesServicioBusqueda:
    """Excepciones específicas del servicio de búsqueda"""
    
    class ErrorServicioBusqueda(Exception):
        """Excepción base para errores del servicio de búsqueda"""
        pass
    
    class ErrorDepartamentoInvalido(ErrorServicioBusqueda):
        """Error cuando se proporciona un ID de departamento inválido"""
        pass
    
    class ErrorNacionalidadInvalida(ErrorServicioBusqueda):
        """Error cuando se proporciona una nacionalidad inválida"""
        pass
    
    class ErrorConversionDatos(ErrorServicioBusqueda):
        """Error al convertir datos de la API a objetos del modelo"""
        pass


class ServicioBusqueda:
    """
    Servicio que proporciona funcionalidades de búsqueda de obras de arte.
    
    Utiliza inyección de dependencias para el cliente API y gestor de nacionalidades.
    """
    
    def __init__(self, cliente_api: ClienteAPIMetMuseum, 
                 gestor_nacionalidades: GestorNacionalidades,
                 almacen_datos: Optional[AlmacenDatos] = None):
        """
        Inicializa el servicio de búsqueda con sus dependencias.
        
        Args:
            cliente_api (ClienteAPIMetMuseum): Cliente para acceder a la API del museo
            gestor_nacionalidades (GestorNacionalidades): Gestor de nacionalidades
            almacen_datos (Optional[AlmacenDatos]): Sistema de cache de datos
        """
        if not isinstance(cliente_api, ClienteAPIMetMuseum):
            raise ValueError("cliente_api debe ser una instancia de ClienteAPIMetMuseum")
        
        if not isinstance(gestor_nacionalidades, GestorNacionalidades):
            raise ValueError("gestor_nacionalidades debe ser una instancia de GestorNacionalidades")
        
        self._cliente_api = cliente_api
        self._gestor_nacionalidades = gestor_nacionalidades
        self._almacen_datos = almacen_datos or AlmacenDatos()
        self.logger = logging.getLogger(__name__)
    
    def buscar_por_departamento(self, id_departamento: int) -> List[ObraArte]:
        """
        Busca obras de arte por departamento específico con cache optimizado.
        
        Args:
            id_departamento (int): ID del departamento a buscar
            
        Returns:
            List[ObraArte]: Lista de obras del departamento
            
        Raises:
            ErrorDepartamentoInvalido: Si el ID del departamento no es válido
            ErrorServicioBusqueda: Si hay errores en la búsqueda o conversión
        """
        if not isinstance(id_departamento, int) or id_departamento <= 0:
            raise ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido(
                f"ID de departamento inválido: {id_departamento}. Debe ser un entero positivo."
            )
        
        self.logger.info(f"Iniciando búsqueda por departamento ID: {id_departamento}")
        
        try:
            # Intentar obtener IDs del cache primero
            ids_obras = self._almacen_datos.obtener_ids_departamento(id_departamento)
            
            if ids_obras is None:
                self.logger.info(f"Departamento {id_departamento} no encontrado en cache, consultando API")
                # No está en cache, obtener de la API
                ids_obras = self._cliente_api.obtener_obras_por_departamento(id_departamento)
                # Almacenar en cache para futuras consultas
                self._almacen_datos.almacenar_ids_departamento(id_departamento, ids_obras)
            else:
                self.logger.info(f"Departamento {id_departamento} encontrado en cache con {len(ids_obras)} obras")
            
            if not ids_obras:
                return []
            
            # Convertir IDs a objetos ObraArte con lazy loading optimizado
            obras = []
            errores_conversion = []
            
            # Limitar a las primeras 20 obras para evitar demasiadas llamadas a la API
            ids_limitados = ids_obras[:20]
            
            for id_obra in ids_limitados:
                try:
                    # Intentar obtener obra del cache primero
                    obra = self._almacen_datos.obtener_obra(id_obra)
                    
                    if obra is None:
                        # No está en cache, obtener de la API
                        datos_obra = self._cliente_api.obtener_detalles_obra(id_obra)
                        obra = self._convertir_datos_api_a_obra(datos_obra)
                        # Almacenar en cache
                        self._almacen_datos.almacenar_obra(obra)
                    
                    obras.append(obra)
                except Exception as e:
                    errores_conversion.append(f"Error al procesar obra {id_obra}: {str(e)}")
                    continue
            
            # Si hay muchos errores de conversión, reportar el problema
            if len(errores_conversion) > len(ids_limitados) * 0.5:
                raise ExcepcionesServicioBusqueda.ErrorConversionDatos(
                    f"Demasiados errores al convertir obras del departamento {id_departamento}. "
                    f"Errores: {'; '.join(errores_conversion[:3])}"
                )
            
            return obras
            
        except ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado:
            raise ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido(
                f"Departamento con ID {id_departamento} no encontrado"
            )
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                f"Error al buscar obras del departamento {id_departamento}: {str(e)}"
            )
    
    def obtener_departamentos_disponibles(self) -> List[Departamento]:
        """
        Obtiene la lista de departamentos disponibles en el museo con cache.
        
        Returns:
            List[Departamento]: Lista de departamentos disponibles
            
        Raises:
            ErrorServicioBusqueda: Si hay errores al obtener los departamentos
        """
        try:
            # Intentar obtener del cache primero
            departamentos = self._almacen_datos.obtener_departamentos()
            
            if departamentos is None:
                # No está en cache, obtener de la API
                departamentos = self._cliente_api.obtener_departamentos()
                # Almacenar en cache
                self._almacen_datos.almacenar_departamentos(departamentos)
            
            # Ordenar departamentos por nombre para mejor experiencia de usuario
            departamentos_ordenados = sorted(departamentos, key=lambda d: d.nombre.lower())
            
            return departamentos_ordenados
            
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                f"Error al obtener departamentos disponibles: {str(e)}"
            )
    
    def buscar_por_nacionalidad(self, nacionalidad: str) -> List[ObraArte]:
        """
        Busca obras de arte por nacionalidad del artista con cache optimizado.
        
        Args:
            nacionalidad (str): Nacionalidad a buscar
            
        Returns:
            List[ObraArte]: Lista de obras de artistas de la nacionalidad especificada
            
        Raises:
            ErrorNacionalidadInvalida: Si la nacionalidad no es válida
            ErrorServicioBusqueda: Si hay errores en la búsqueda
        """
        if not nacionalidad or not isinstance(nacionalidad, str):
            raise ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida(
                "La nacionalidad debe ser una cadena no vacía"
            )
        
        nacionalidad_limpia = nacionalidad.strip()
        if not nacionalidad_limpia:
            raise ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida(
                "La nacionalidad no puede estar vacía"
            )
        
        # Validar que la nacionalidad esté en la lista disponible
        if not self._gestor_nacionalidades.validar_nacionalidad(nacionalidad_limpia):
            raise ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida(
                f"Nacionalidad '{nacionalidad_limpia}' no encontrada en la lista de nacionalidades disponibles"
            )
        
        try:
            # Crear clave de cache para esta búsqueda
            clave_busqueda = f"nacionalidad:{nacionalidad_limpia.lower()}"
            
            # Intentar obtener IDs del cache
            ids_obras = self._almacen_datos.obtener_resultado_busqueda(clave_busqueda)
            
            if ids_obras is None:
                # No está en cache, buscar en la API
                ids_obras = self._cliente_api.buscar_obras_por_query(nacionalidad_limpia)
                # Almacenar resultado en cache
                self._almacen_datos.almacenar_resultado_busqueda(clave_busqueda, ids_obras)
            
            if not ids_obras:
                return []
            
            # Convertir IDs a objetos ObraArte y filtrar por nacionalidad del artista
            obras_filtradas = []
            ids_limitados = ids_obras[:30]  # Limitar para evitar demasiadas llamadas
            
            for id_obra in ids_limitados:
                try:
                    # Intentar obtener obra del cache primero
                    obra = self._almacen_datos.obtener_obra(id_obra)
                    
                    if obra is None:
                        # No está en cache, obtener de la API
                        datos_obra = self._cliente_api.obtener_detalles_obra(id_obra)
                        obra = self._convertir_datos_api_a_obra(datos_obra)
                        # Almacenar en cache
                        self._almacen_datos.almacenar_obra(obra)
                    
                    # Filtrar por nacionalidad exacta del artista
                    if (obra.artista.nacionalidad and 
                        nacionalidad_limpia.lower() in obra.artista.nacionalidad.lower()):
                        obras_filtradas.append(obra)
                        
                except Exception:
                    continue  # Ignorar obras con errores de conversión
            
            return obras_filtradas
            
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                f"Error al buscar obras por nacionalidad '{nacionalidad_limpia}': {str(e)}"
            )
    
    def buscar_por_nombre_artista(self, nombre_artista: str) -> List[ObraArte]:
        """
        Busca obras de arte por nombre del artista con coincidencia parcial y cache optimizado.
        
        Args:
            nombre_artista (str): Nombre del artista a buscar
            
        Returns:
            List[ObraArte]: Lista de obras del artista especificado
            
        Raises:
            ErrorServicioBusqueda: Si hay errores en la búsqueda o validación
        """
        # Validación de entrada
        if not nombre_artista or not isinstance(nombre_artista, str):
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                "El nombre del artista debe ser una cadena no vacía"
            )
        
        # Sanitización del nombre
        nombre_limpio = self._sanitizar_nombre_artista(nombre_artista)
        if not nombre_limpio:
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                "El nombre del artista no puede estar vacío después de la sanitización"
            )
        
        try:
            # Crear clave de cache para esta búsqueda
            clave_busqueda = f"artista:{nombre_limpio.lower()}"
            
            # Intentar obtener IDs del cache
            ids_obras = self._almacen_datos.obtener_resultado_busqueda(clave_busqueda)
            
            if ids_obras is None:
                # No está en cache, buscar en la API
                ids_obras = self._cliente_api.buscar_obras_por_query(nombre_limpio)
                # Almacenar resultado en cache
                self._almacen_datos.almacenar_resultado_busqueda(clave_busqueda, ids_obras)
            
            if not ids_obras:
                return []
            
            # Convertir IDs a objetos ObraArte con filtrado por nombre
            obras_coincidentes = []
            ids_limitados = ids_obras[:25]  # Limitar para evitar demasiadas llamadas
            errores_conversion = []
            
            for id_obra in ids_limitados:
                try:
                    # Intentar obtener obra del cache primero
                    obra = self._almacen_datos.obtener_obra(id_obra)
                    
                    if obra is None:
                        # No está en cache, obtener de la API
                        datos_obra = self._cliente_api.obtener_detalles_obra(id_obra)
                        obra = self._convertir_datos_api_a_obra(datos_obra)
                        # Almacenar en cache
                        self._almacen_datos.almacenar_obra(obra)
                    
                    # Verificar coincidencia parcial del nombre del artista
                    if self._verificar_coincidencia_nombre_artista(obra.artista.nombre, nombre_limpio):
                        obras_coincidentes.append(obra)
                        
                except Exception as e:
                    errores_conversion.append(f"Error al procesar obra {id_obra}: {str(e)}")
                    continue
            
            # Log de errores si hay demasiados (para debugging)
            if len(errores_conversion) > len(ids_limitados) * 0.3:
                # Si más del 30% de las conversiones fallan, podría indicar un problema
                pass  # En una implementación real, aquí se haría logging
            
            return obras_coincidentes
            
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise ExcepcionesServicioBusqueda.ErrorServicioBusqueda(
                f"Error al buscar obras por artista '{nombre_limpio}': {str(e)}"
            )
    
    def _sanitizar_nombre_artista(self, nombre: str) -> str:
        """
        Sanitiza el nombre del artista para la búsqueda.
        
        Args:
            nombre (str): Nombre original del artista
            
        Returns:
            str: Nombre sanitizado
        """
        if not nombre:
            return ""
        
        # Eliminar espacios al inicio y final
        nombre_limpio = nombre.strip()
        
        # Eliminar caracteres especiales problemáticos pero mantener espacios internos
        # y caracteres comunes en nombres de artistas
        caracteres_permitidos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-'"
        nombre_sanitizado = ''.join(c for c in nombre_limpio if c in caracteres_permitidos)
        
        # Eliminar espacios múltiples
        while '  ' in nombre_sanitizado:
            nombre_sanitizado = nombre_sanitizado.replace('  ', ' ')
        
        return nombre_sanitizado.strip()
    
    def _verificar_coincidencia_nombre_artista(self, nombre_obra: str, nombre_busqueda: str) -> bool:
        """
        Verifica si hay coincidencia parcial entre el nombre del artista de la obra
        y el nombre buscado.
        
        Args:
            nombre_obra (str): Nombre del artista en la obra
            nombre_busqueda (str): Nombre buscado por el usuario
            
        Returns:
            bool: True si hay coincidencia, False en caso contrario
        """
        if not nombre_obra or not nombre_busqueda:
            return False
        
        # Convertir a minúsculas para comparación insensible a mayúsculas
        nombre_obra_lower = nombre_obra.lower()
        nombre_busqueda_lower = nombre_busqueda.lower()
        
        # Verificar coincidencia parcial
        return nombre_busqueda_lower in nombre_obra_lower
    
    def _convertir_datos_api_a_obra(self, datos_api: dict) -> ObraArte:
        """
        Convierte datos de la API a un objeto ObraArte.
        
        Args:
            datos_api (dict): Datos de la obra desde la API
            
        Returns:
            ObraArte: Objeto ObraArte creado a partir de los datos
            
        Raises:
            ErrorConversionDatos: Si hay errores en la conversión
        """
        try:
            # Validar campos requeridos
            if 'objectID' not in datos_api or 'title' not in datos_api:
                raise ExcepcionesServicioBusqueda.ErrorConversionDatos(
                    "Datos de obra incompletos: falta objectID o title"
                )
            
            id_obra = datos_api['objectID']
            titulo = datos_api['title'] or "Título desconocido"
            
            # Crear objeto Artista
            nombre_artista = datos_api.get('artistDisplayName') or "Artista desconocido"
            nacionalidad = datos_api.get('artistNationality')
            fecha_nacimiento = datos_api.get('artistBeginDate')
            fecha_muerte = datos_api.get('artistEndDate')
            
            artista = Artista(
                nombre=nombre_artista,
                nacionalidad=nacionalidad,
                fecha_nacimiento=fecha_nacimiento,
                fecha_muerte=fecha_muerte
            )
            
            # Crear objeto ObraArte
            clasificacion = datos_api.get('classification')
            fecha_creacion = datos_api.get('objectDate')
            url_imagen = datos_api.get('primaryImage')
            departamento = datos_api.get('department')
            
            # Limpiar URL de imagen vacía
            if url_imagen and not url_imagen.strip():
                url_imagen = None
            
            obra = ObraArte(
                id_obra=id_obra,
                titulo=titulo,
                artista=artista,
                clasificacion=clasificacion,
                fecha_creacion=fecha_creacion,
                url_imagen=url_imagen,
                departamento=departamento
            )
            
            return obra
            
        except (ValueError, KeyError, TypeError) as e:
            raise ExcepcionesServicioBusqueda.ErrorConversionDatos(
                f"Error al convertir datos de obra: {str(e)}"
            )
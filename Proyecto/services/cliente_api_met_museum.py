"""
Cliente API para el Metropolitan Museum of Art
Proporciona acceso a los endpoints principales de la API del museo.
"""

import requests
import time
import logging
from typing import List, Dict, Optional
from models.departamento import Departamento


class ExcepcionesAPIMetMuseum:
    """Excepciones personalizadas para el cliente API del Metropolitan Museum"""
    
    class ErrorAPIMetMuseum(Exception):
        """Excepción base para errores de la API"""
        pass
    
    class ErrorConexionAPI(ErrorAPIMetMuseum):
        """Error de conexión con la API"""
        pass
    
    class ErrorDatosIncompletos(ErrorAPIMetMuseum):
        """Datos de obra incompletos o inválidos"""
        pass
    
    class ErrorRecursoNoEncontrado(ErrorAPIMetMuseum):
        """Recurso solicitado no encontrado"""
        pass
    
    class ErrorRateLimitAPI(ErrorAPIMetMuseum):
        """Error de límite de velocidad de la API"""
        pass


class ClienteAPIMetMuseum:
    """Cliente para interactuar con la API del Metropolitan Museum of Art"""
    
    BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"
    TIMEOUT = 30  # segundos
    MAX_REINTENTOS = 3
    DELAY_ENTRE_REINTENTOS = 1  # segundos
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Museo-Catalogo-Arte/1.0'
        })
        self.logger = logging.getLogger(__name__)
    
    def obtener_departamentos(self) -> List[Departamento]:
        """
        Obtiene la lista completa de departamentos del museo.
        
        Returns:
            List[Departamento]: Lista de objetos Departamento
            
        Raises:
            ErrorConexionAPI: Si hay problemas de conexión
            ErrorDatosIncompletos: Si la respuesta no tiene el formato esperado
        """
        endpoint = "/departments"
        self.logger.info(f"Obteniendo departamentos desde {self.BASE_URL}{endpoint}")
        
        try:
            datos = self._realizar_peticion(endpoint)
            
            if 'departments' not in datos:
                raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                    "La respuesta no contiene la lista de departamentos"
                )
            
            departamentos = []
            for dept_data in datos['departments']:
                if 'departmentId' not in dept_data or 'displayName' not in dept_data:
                    continue  # Saltar departamentos con datos incompletos
                
                departamento = Departamento(
                    id_departamento=dept_data['departmentId'],
                    nombre=dept_data['displayName']
                )
                departamentos.append(departamento)
            
            self.logger.info(f"Obtenidos {len(departamentos)} departamentos exitosamente")
            return departamentos
            
        except requests.RequestException as e:
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error al obtener departamentos: {str(e)}"
            )
    
    def obtener_detalles_obra(self, id_obra: int) -> Dict:
        """
        Obtiene los detalles completos de una obra específica.
        
        Args:
            id_obra (int): ID único de la obra
            
        Returns:
            Dict: Diccionario con los datos completos de la obra
            
        Raises:
            ErrorConexionAPI: Si hay problemas de conexión
            ErrorRecursoNoEncontrado: Si la obra no existe
            ErrorDatosIncompletos: Si los datos están incompletos
        """
        endpoint = f"/objects/{id_obra}"
        self.logger.info(f"Obteniendo detalles de obra ID: {id_obra}")
        
        try:
            datos = self._realizar_peticion(endpoint)
            
            # Validar que la respuesta contenga los campos mínimos requeridos
            campos_requeridos = ['objectID', 'title']
            for campo in campos_requeridos:
                if campo not in datos or datos[campo] is None:
                    raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                        f"Campo requerido '{campo}' faltante o nulo en la obra {id_obra}"
                    )
            
            # Verificar que el objectID coincida con el solicitado
            if datos['objectID'] != id_obra:
                raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                    f"ID de obra no coincide: esperado {id_obra}, recibido {datos['objectID']}"
                )
            
            self.logger.info(f"Detalles de obra {id_obra} obtenidos exitosamente: '{datos.get('title', 'Sin título')}'")
            return datos
            
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    raise ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado(
                        f"Obra con ID {id_obra} no encontrada"
                    )
            
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error al obtener detalles de obra {id_obra}: {str(e)}"
            )
    
    def buscar_obras_por_query(self, query: str, departamento_id: Optional[int] = None) -> List[int]:
        """
        Busca obras usando una consulta de texto general.
        
        Args:
            query (str): Término de búsqueda
            departamento_id (Optional[int]): ID del departamento para filtrar resultados
            
        Returns:
            List[int]: Lista de IDs de obras que coinciden con la búsqueda
            
        Raises:
            ErrorConexionAPI: Si hay problemas de conexión
            ErrorDatosIncompletos: Si la respuesta no tiene el formato esperado
        """
        if not query or not query.strip():
            return []
        
        endpoint = "/search"
        params = {'q': query.strip()}
        
        if departamento_id is not None:
            params['departmentId'] = departamento_id
        
        try:
            datos = self._realizar_peticion(endpoint, params=params)
            
            # Si no hay resultados, la API retorna {"total": 0, "objectIDs": null}
            if datos.get('total', 0) == 0 or datos.get('objectIDs') is None:
                return []
            
            # Validar que objectIDs sea una lista
            object_ids = datos.get('objectIDs', [])
            if not isinstance(object_ids, list):
                raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                    "La respuesta de búsqueda no contiene una lista válida de IDs"
                )
            
            # Filtrar IDs válidos (enteros positivos)
            ids_validos = []
            for obj_id in object_ids:
                if isinstance(obj_id, int) and obj_id > 0:
                    ids_validos.append(obj_id)
            
            return ids_validos
            
        except requests.RequestException as e:
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error al buscar obras con query '{query}': {str(e)}"
            )
    
    def obtener_obras_por_departamento(self, id_departamento: int) -> List[int]:
        """
        Obtiene todas las obras de un departamento específico.
        
        Args:
            id_departamento (int): ID del departamento
            
        Returns:
            List[int]: Lista de IDs de obras del departamento
            
        Raises:
            ErrorConexionAPI: Si hay problemas de conexión
            ErrorRecursoNoEncontrado: Si el departamento no existe
            ErrorDatosIncompletos: Si la respuesta no tiene el formato esperado
        """
        endpoint = f"/objects"
        params = {'departmentIds': id_departamento}
        
        try:
            datos = self._realizar_peticion(endpoint, params=params)
            
            # Si no hay obras en el departamento
            if datos.get('total', 0) == 0 or datos.get('objectIDs') is None:
                return []
            
            # Validar que objectIDs sea una lista
            object_ids = datos.get('objectIDs', [])
            if not isinstance(object_ids, list):
                raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                    f"La respuesta del departamento {id_departamento} no contiene una lista válida de IDs"
                )
            
            # Filtrar IDs válidos
            ids_validos = []
            for obj_id in object_ids:
                if isinstance(obj_id, int) and obj_id > 0:
                    ids_validos.append(obj_id)
            
            return ids_validos
            
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    raise ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado(
                        f"Departamento con ID {id_departamento} no encontrado"
                    )
            
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error al obtener obras del departamento {id_departamento}: {str(e)}"
            )
    
    def _realizar_peticion(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Realiza una petición HTTP a la API con manejo de errores y reintentos.
        
        Args:
            endpoint (str): Endpoint de la API (debe empezar con /)
            params (Optional[Dict]): Parámetros de consulta
            
        Returns:
            Dict: Respuesta JSON de la API
            
        Raises:
            ErrorConexionAPI: Si hay problemas de conexión
            ErrorRateLimitAPI: Si se excede el límite de velocidad
            ErrorDatosIncompletos: Si la respuesta no es JSON válido
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for intento in range(self.MAX_REINTENTOS):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.TIMEOUT
                )
                
                # Manejar errores HTTP específicos
                self._manejar_errores_api(response)
                
                # Intentar parsear JSON
                try:
                    return response.json()
                except ValueError as e:
                    raise ExcepcionesAPIMetMuseum.ErrorDatosIncompletos(
                        f"Respuesta no es JSON válido: {str(e)}"
                    )
                
            except (requests.ConnectionError, requests.Timeout) as e:
                if intento < self.MAX_REINTENTOS - 1:
                    time.sleep(self.DELAY_ENTRE_REINTENTOS * (intento + 1))
                    continue
                else:
                    raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                        f"Error de conexión después de {self.MAX_REINTENTOS} intentos: {str(e)}"
                    )
            
            except requests.RequestException as e:
                raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                    f"Error en petición HTTP: {str(e)}"
                )
        
        # Este punto no debería alcanzarse nunca
        raise ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error inesperado en petición")
    
    def _manejar_errores_api(self, response: requests.Response) -> None:
        """
        Maneja errores HTTP específicos de la API.
        
        Args:
            response (requests.Response): Respuesta HTTP
            
        Raises:
            ErrorRateLimitAPI: Si se excede el límite de velocidad (429)
            ErrorRecursoNoEncontrado: Si el recurso no existe (404)
            ErrorConexionAPI: Para otros errores HTTP
        """
        if response.status_code == 200:
            return
        
        if response.status_code == 429:
            raise ExcepcionesAPIMetMuseum.ErrorRateLimitAPI(
                "Límite de velocidad de API excedido. Intente más tarde."
            )
        
        if response.status_code == 404:
            raise ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado(
                "Recurso no encontrado en la API"
            )
        
        if response.status_code >= 500:
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error del servidor de la API: {response.status_code}"
            )
        
        if response.status_code >= 400:
            raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
                f"Error del cliente en petición: {response.status_code}"
            )
        
        # Para cualquier otro código de estado no exitoso
        raise ExcepcionesAPIMetMuseum.ErrorConexionAPI(
            f"Error HTTP inesperado: {response.status_code}"
        )
    
    def __del__(self):
        """Cierra la sesión HTTP al destruir el objeto"""
        if hasattr(self, 'session'):
            self.session.close()
"""
Sistema de almacenamiento y cache de datos para el catálogo del museo.
Proporciona cache en memoria con invalidación basada en tiempo para optimizar rendimiento.
"""

import time
from typing import List, Dict, Optional, Callable, Any
from threading import Lock
from models.obra_arte import ObraArte
from models.departamento import Departamento


class EntradaCache:
    """Representa una entrada individual en el cache con timestamp"""
    
    def __init__(self, datos: Any, tiempo_vida: int = 300):
        """
        Inicializa una entrada de cache.
        
        Args:
            datos (Any): Datos a almacenar en cache
            tiempo_vida (int): Tiempo de vida en segundos (default: 5 minutos)
        """
        self.datos = datos
        self.timestamp = time.time()
        self.tiempo_vida = tiempo_vida
    
    def es_valida(self) -> bool:
        """
        Verifica si la entrada de cache sigue siendo válida.
        
        Returns:
            bool: True si la entrada es válida, False si ha expirado
        """
        return (time.time() - self.timestamp) < self.tiempo_vida
    
    def obtener_datos(self) -> Any:
        """
        Obtiene los datos si la entrada es válida.
        
        Returns:
            Any: Datos almacenados o None si ha expirado
        """
        return self.datos if self.es_valida() else None


class AlmacenDatos:
    """
    Sistema de almacenamiento y cache de datos para optimizar el rendimiento.
    
    Proporciona cache en memoria con invalidación automática basada en tiempo
    para obras de arte, departamentos y resultados de búsqueda.
    """
    
    # Tiempos de vida por defecto en segundos
    TIEMPO_VIDA_OBRAS = 600  # 10 minutos
    TIEMPO_VIDA_DEPARTAMENTOS = 1800  # 30 minutos
    TIEMPO_VIDA_BUSQUEDAS = 300  # 5 minutos
    TIEMPO_VIDA_LISTAS_IDS = 180  # 3 minutos
    
    def __init__(self):
        """Inicializa el almacén de datos con estructuras de cache vacías."""
        # Cache de obras individuales por ID
        self._cache_obras: Dict[int, EntradaCache] = {}
        
        # Cache de departamentos
        self._cache_departamentos: Optional[EntradaCache] = None
        
        # Cache de resultados de búsqueda por query
        self._cache_busquedas: Dict[str, EntradaCache] = {}
        
        # Cache de listas de IDs por departamento
        self._cache_ids_departamento: Dict[int, EntradaCache] = {}
        
        # Lock para operaciones thread-safe
        self._lock = Lock()
        
        # Estadísticas de cache
        self._estadisticas = {
            'hits_obras': 0,
            'misses_obras': 0,
            'hits_departamentos': 0,
            'misses_departamentos': 0,
            'hits_busquedas': 0,
            'misses_busquedas': 0,
            'limpiezas_automaticas': 0
        }
    
    def obtener_obra(self, id_obra: int) -> Optional[ObraArte]:
        """
        Obtiene una obra del cache si está disponible y válida.
        
        Args:
            id_obra (int): ID de la obra a buscar
            
        Returns:
            Optional[ObraArte]: Obra si está en cache y válida, None en caso contrario
        """
        with self._lock:
            if id_obra in self._cache_obras:
                entrada = self._cache_obras[id_obra]
                obra = entrada.obtener_datos()
                
                if obra is not None:
                    self._estadisticas['hits_obras'] += 1
                    return obra
                else:
                    # Entrada expirada, eliminar del cache
                    del self._cache_obras[id_obra]
            
            self._estadisticas['misses_obras'] += 1
            return None
    
    def almacenar_obra(self, obra: ObraArte) -> None:
        """
        Almacena una obra en el cache.
        
        Args:
            obra (ObraArte): Obra a almacenar
        """
        if not isinstance(obra, ObraArte):
            raise ValueError("El parámetro debe ser una instancia de ObraArte")
        
        with self._lock:
            entrada = EntradaCache(obra, self.TIEMPO_VIDA_OBRAS)
            self._cache_obras[obra.id_obra] = entrada
            
            # Limpiar cache si es necesario
            self._limpiar_cache_si_necesario()
    
    def obtener_departamentos(self) -> Optional[List[Departamento]]:
        """
        Obtiene la lista de departamentos del cache si está disponible y válida.
        
        Returns:
            Optional[List[Departamento]]: Lista de departamentos o None si no está en cache
        """
        with self._lock:
            if self._cache_departamentos is not None:
                departamentos = self._cache_departamentos.obtener_datos()
                
                if departamentos is not None:
                    self._estadisticas['hits_departamentos'] += 1
                    return departamentos
                else:
                    # Entrada expirada
                    self._cache_departamentos = None
            
            self._estadisticas['misses_departamentos'] += 1
            return None
    
    def almacenar_departamentos(self, departamentos: List[Departamento]) -> None:
        """
        Almacena la lista de departamentos en el cache.
        
        Args:
            departamentos (List[Departamento]): Lista de departamentos a almacenar
        """
        if not isinstance(departamentos, list):
            raise ValueError("El parámetro debe ser una lista de departamentos")
        
        with self._lock:
            entrada = EntradaCache(departamentos, self.TIEMPO_VIDA_DEPARTAMENTOS)
            self._cache_departamentos = entrada
    
    def obtener_resultado_busqueda(self, clave_busqueda: str) -> Optional[List[int]]:
        """
        Obtiene el resultado de una búsqueda del cache.
        
        Args:
            clave_busqueda (str): Clave única que identifica la búsqueda
            
        Returns:
            Optional[List[int]]: Lista de IDs de obras o None si no está en cache
        """
        with self._lock:
            if clave_busqueda in self._cache_busquedas:
                entrada = self._cache_busquedas[clave_busqueda]
                resultado = entrada.obtener_datos()
                
                if resultado is not None:
                    self._estadisticas['hits_busquedas'] += 1
                    return resultado
                else:
                    # Entrada expirada
                    del self._cache_busquedas[clave_busqueda]
            
            self._estadisticas['misses_busquedas'] += 1
            return None
    
    def almacenar_resultado_busqueda(self, clave_busqueda: str, ids_obras: List[int]) -> None:
        """
        Almacena el resultado de una búsqueda en el cache.
        
        Args:
            clave_busqueda (str): Clave única que identifica la búsqueda
            ids_obras (List[int]): Lista de IDs de obras resultado de la búsqueda
        """
        if not isinstance(ids_obras, list):
            raise ValueError("ids_obras debe ser una lista")
        
        with self._lock:
            entrada = EntradaCache(ids_obras, self.TIEMPO_VIDA_BUSQUEDAS)
            self._cache_busquedas[clave_busqueda] = entrada
            
            # Limpiar cache si es necesario
            self._limpiar_cache_si_necesario()
    
    def obtener_ids_departamento(self, id_departamento: int) -> Optional[List[int]]:
        """
        Obtiene la lista de IDs de obras de un departamento del cache.
        
        Args:
            id_departamento (int): ID del departamento
            
        Returns:
            Optional[List[int]]: Lista de IDs de obras o None si no está en cache
        """
        with self._lock:
            if id_departamento in self._cache_ids_departamento:
                entrada = self._cache_ids_departamento[id_departamento]
                ids = entrada.obtener_datos()
                
                if ids is not None:
                    return ids
                else:
                    # Entrada expirada
                    del self._cache_ids_departamento[id_departamento]
            
            return None
    
    def almacenar_ids_departamento(self, id_departamento: int, ids_obras: List[int]) -> None:
        """
        Almacena la lista de IDs de obras de un departamento en el cache.
        
        Args:
            id_departamento (int): ID del departamento
            ids_obras (List[int]): Lista de IDs de obras del departamento
        """
        if not isinstance(ids_obras, list):
            raise ValueError("ids_obras debe ser una lista")
        
        with self._lock:
            entrada = EntradaCache(ids_obras, self.TIEMPO_VIDA_LISTAS_IDS)
            self._cache_ids_departamento[id_departamento] = entrada
    
    def buscar_obras_por_criterio(self, criterio: Callable[[ObraArte], bool]) -> List[ObraArte]:
        """
        Busca obras en el cache que cumplan un criterio específico.
        
        Args:
            criterio (Callable[[ObraArte], bool]): Función que evalúa si una obra cumple el criterio
            
        Returns:
            List[ObraArte]: Lista de obras que cumplen el criterio
        """
        obras_encontradas = []
        
        with self._lock:
            for entrada in self._cache_obras.values():
                obra = entrada.obtener_datos()
                if obra is not None and criterio(obra):
                    obras_encontradas.append(obra)
        
        return obras_encontradas
    
    def invalidar_cache_obras(self) -> None:
        """Invalida todo el cache de obras."""
        with self._lock:
            self._cache_obras.clear()
    
    def invalidar_cache_departamentos(self) -> None:
        """Invalida el cache de departamentos."""
        with self._lock:
            self._cache_departamentos = None
    
    def invalidar_cache_busquedas(self) -> None:
        """Invalida todo el cache de búsquedas."""
        with self._lock:
            self._cache_busquedas.clear()
    
    def invalidar_todo_cache(self) -> None:
        """Invalida todo el cache."""
        with self._lock:
            self._cache_obras.clear()
            self._cache_departamentos = None
            self._cache_busquedas.clear()
            self._cache_ids_departamento.clear()
    
    def obtener_estadisticas_cache(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del uso del cache.
        
        Returns:
            Dict[str, Any]: Diccionario con estadísticas del cache
        """
        with self._lock:
            estadisticas = self._estadisticas.copy()
            
            # Agregar información adicional
            estadisticas.update({
                'obras_en_cache': len(self._cache_obras),
                'busquedas_en_cache': len(self._cache_busquedas),
                'departamentos_en_cache': 1 if self._cache_departamentos else 0,
                'ids_departamentos_en_cache': len(self._cache_ids_departamento),
                'memoria_estimada_kb': self._estimar_uso_memoria()
            })
            
            # Calcular ratios de hit
            total_obras = estadisticas['hits_obras'] + estadisticas['misses_obras']
            total_departamentos = estadisticas['hits_departamentos'] + estadisticas['misses_departamentos']
            total_busquedas = estadisticas['hits_busquedas'] + estadisticas['misses_busquedas']
            
            estadisticas['hit_ratio_obras'] = (
                estadisticas['hits_obras'] / total_obras if total_obras > 0 else 0
            )
            estadisticas['hit_ratio_departamentos'] = (
                estadisticas['hits_departamentos'] / total_departamentos if total_departamentos > 0 else 0
            )
            estadisticas['hit_ratio_busquedas'] = (
                estadisticas['hits_busquedas'] / total_busquedas if total_busquedas > 0 else 0
            )
            
            return estadisticas
    
    def _limpiar_cache_si_necesario(self) -> None:
        """
        Limpia entradas expiradas del cache si es necesario.
        Se ejecuta automáticamente cuando el cache crece demasiado.
        """
        # Limpiar si hay más de 1000 entradas en total
        total_entradas = len(self._cache_obras) + len(self._cache_busquedas) + len(self._cache_ids_departamento)
        
        if total_entradas > 1000:
            self._limpiar_entradas_expiradas()
            self._estadisticas['limpiezas_automaticas'] += 1
    
    def _limpiar_entradas_expiradas(self) -> None:
        """Elimina todas las entradas expiradas del cache."""
        # Limpiar obras expiradas
        ids_expirados = [
            id_obra for id_obra, entrada in self._cache_obras.items()
            if not entrada.es_valida()
        ]
        for id_obra in ids_expirados:
            del self._cache_obras[id_obra]
        
        # Limpiar búsquedas expiradas
        claves_expiradas = [
            clave for clave, entrada in self._cache_busquedas.items()
            if not entrada.es_valida()
        ]
        for clave in claves_expiradas:
            del self._cache_busquedas[clave]
        
        # Limpiar IDs de departamentos expirados
        ids_dept_expirados = [
            id_dept for id_dept, entrada in self._cache_ids_departamento.items()
            if not entrada.es_valida()
        ]
        for id_dept in ids_dept_expirados:
            del self._cache_ids_departamento[id_dept]
        
        # Limpiar departamentos si están expirados
        if self._cache_departamentos and not self._cache_departamentos.es_valida():
            self._cache_departamentos = None
    
    def _estimar_uso_memoria(self) -> int:
        """
        Estima el uso de memoria del cache en KB.
        
        Returns:
            int: Estimación del uso de memoria en KB
        """
        # Estimación aproximada basada en el número de objetos
        # Cada obra: ~2KB, cada departamento: ~0.1KB, cada búsqueda: ~0.5KB
        memoria_obras = len(self._cache_obras) * 2
        memoria_departamentos = 5 if self._cache_departamentos else 0  # ~50 departamentos * 0.1KB
        memoria_busquedas = len(self._cache_busquedas) * 0.5
        memoria_ids_dept = len(self._cache_ids_departamento) * 1  # ~1KB por lista de IDs
        
        return int(memoria_obras + memoria_departamentos + memoria_busquedas + memoria_ids_dept)
    
    def limpiar_cache_manual(self) -> Dict[str, int]:
        """
        Realiza una limpieza manual del cache eliminando entradas expiradas.
        
        Returns:
            Dict[str, int]: Estadísticas de la limpieza realizada
        """
        with self._lock:
            # Contar entradas antes de la limpieza
            antes = {
                'obras': len(self._cache_obras),
                'busquedas': len(self._cache_busquedas),
                'ids_departamentos': len(self._cache_ids_departamento),
                'departamentos': 1 if self._cache_departamentos else 0
            }
            
            # Realizar limpieza
            self._limpiar_entradas_expiradas()
            
            # Contar entradas después de la limpieza
            despues = {
                'obras': len(self._cache_obras),
                'busquedas': len(self._cache_busquedas),
                'ids_departamentos': len(self._cache_ids_departamento),
                'departamentos': 1 if self._cache_departamentos else 0
            }
            
            # Calcular elementos eliminados
            eliminados = {
                'obras_eliminadas': antes['obras'] - despues['obras'],
                'busquedas_eliminadas': antes['busquedas'] - despues['busquedas'],
                'ids_departamentos_eliminados': antes['ids_departamentos'] - despues['ids_departamentos'],
                'departamentos_eliminados': antes['departamentos'] - despues['departamentos']
            }
            
            return eliminados
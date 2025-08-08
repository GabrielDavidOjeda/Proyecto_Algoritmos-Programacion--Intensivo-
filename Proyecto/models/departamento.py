"""
Modelo de datos para representar un departamento del museo.
"""


class Departamento:
    """
    Clase que representa un departamento del museo con validación de datos.
    
    Attributes:
        _id_departamento (int): ID único del departamento
        _nombre (str): Nombre del departamento
    """
    
    def __init__(self, id_departamento: int, nombre: str):
        """
        Inicializa un nuevo departamento.
        
        Args:
            id_departamento (int): ID único del departamento (requerido)
            nombre (str): Nombre del departamento (requerido)
        
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not isinstance(id_departamento, int) or id_departamento <= 0:
            raise ValueError("El ID del departamento debe ser un entero positivo")
        
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del departamento es requerido y debe ser una cadena")
        
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del departamento no puede estar vacío")
        
        self._id_departamento = id_departamento
        self._nombre = nombre_limpio
    
    @property
    def id_departamento(self) -> int:
        """Obtiene el ID del departamento."""
        return self._id_departamento
    
    @property
    def nombre(self) -> str:
        """Obtiene el nombre del departamento."""
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor: str):
        """
        Establece el nombre del departamento con validación.
        
        Args:
            valor (str): Nuevo nombre del departamento
        
        Raises:
            ValueError: Si el nombre no es válido
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("El nombre del departamento es requerido y debe ser una cadena")
        
        nombre_limpio = valor.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del departamento no puede estar vacío")
        
        self._nombre = nombre_limpio
    
    def validar_datos(self) -> bool:
        """
        Valida que los datos del departamento sean correctos.
        
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        try:
            # Validar ID
            if not isinstance(self._id_departamento, int) or self._id_departamento <= 0:
                return False
            
            # Validar nombre
            if not self._nombre or not isinstance(self._nombre, str) or not self._nombre.strip():
                return False
            
            return True
        except:
            return False
    
    def obtener_info_completa(self) -> dict:
        """
        Obtiene la información completa del departamento.
        
        Returns:
            dict: Diccionario con la información del departamento
        """
        return {
            'id': self._id_departamento,
            'nombre': self._nombre,
            'valido': self.validar_datos()
        }
    
    def __str__(self) -> str:
        """Representación en cadena del departamento."""
        return f"{self._nombre} (ID: {self._id_departamento})"
    
    def __repr__(self) -> str:
        """Representación técnica del departamento."""
        return f"Departamento(id_departamento={self._id_departamento}, nombre='{self._nombre}')"
    
    def __eq__(self, other) -> bool:
        """Compara dos departamentos por igualdad."""
        if not isinstance(other, Departamento):
            return False
        return self._id_departamento == other._id_departamento
    
    def __hash__(self) -> int:
        """Hash del departamento basado en su ID."""
        return hash(self._id_departamento)
    
    def __lt__(self, other) -> bool:
        """Comparación menor que para ordenamiento."""
        if not isinstance(other, Departamento):
            return NotImplemented
        return self._nombre.lower() < other._nombre.lower()
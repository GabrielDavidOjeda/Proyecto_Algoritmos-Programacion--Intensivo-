"""
Modelo de datos para representar un artista en el sistema de catálogo del museo.
"""

class Artista:
    """
    Clase que representa un artista con propiedades encapsuladas.
    
    Attributes:
        _nombre (str): Nombre del artista
        _nacionalidad (str): Nacionalidad del artista
        _fecha_nacimiento (str): Fecha de nacimiento del artista
        _fecha_muerte (str): Fecha de muerte del artista
    """
    
    def __init__(self, nombre: str, nacionalidad: str = None, 
                 fecha_nacimiento: str = None, fecha_muerte: str = None):
        """
        Inicializa un nuevo artista.
        
        Args:
            nombre (str): Nombre del artista (requerido)
            nacionalidad (str, optional): Nacionalidad del artista
            fecha_nacimiento (str, optional): Fecha de nacimiento
            fecha_muerte (str, optional): Fecha de muerte
        """
        if not nombre or not isinstance(nombre, str):
            raise ValueError("El nombre del artista es requerido y debe ser una cadena")
        
        nombre_limpio = nombre.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del artista es requerido y debe ser una cadena")
        
        self._nombre = nombre_limpio
        self._nacionalidad = nacionalidad.strip() if nacionalidad else None
        self._fecha_nacimiento = fecha_nacimiento.strip() if fecha_nacimiento else None
        self._fecha_muerte = fecha_muerte.strip() if fecha_muerte else None
    
    @property
    def nombre(self) -> str:
        """Obtiene el nombre del artista."""
        return self._nombre
    
    @property
    def nacionalidad(self) -> str:
        """Obtiene la nacionalidad del artista."""
        return self._nacionalidad
    
    @property
    def fecha_nacimiento(self) -> str:
        """Obtiene la fecha de nacimiento del artista."""
        return self._fecha_nacimiento
    
    @property
    def fecha_muerte(self) -> str:
        """Obtiene la fecha de muerte del artista."""
        return self._fecha_muerte
    
    @nombre.setter
    def nombre(self, valor: str):
        """Establece el nombre del artista."""
        if not valor or not isinstance(valor, str):
            raise ValueError("El nombre del artista es requerido y debe ser una cadena")
        nombre_limpio = valor.strip()
        if not nombre_limpio:
            raise ValueError("El nombre del artista es requerido y debe ser una cadena")
        self._nombre = nombre_limpio
    
    @nacionalidad.setter
    def nacionalidad(self, valor: str):
        """Establece la nacionalidad del artista."""
        self._nacionalidad = valor.strip() if valor else None
    
    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor: str):
        """Establece la fecha de nacimiento del artista."""
        self._fecha_nacimiento = valor.strip() if valor else None
    
    @fecha_muerte.setter
    def fecha_muerte(self, valor: str):
        """Establece la fecha de muerte del artista."""
        self._fecha_muerte = valor.strip() if valor else None
    
    def obtener_periodo_vida(self) -> str:
        """
        Obtiene el período de vida del artista en formato legible.
        
        Returns:
            str: Período de vida formateado (ej: "1525-1569" o "1525-presente")
        """
        if not self._fecha_nacimiento:
            return "Fechas desconocidas"
        
        inicio = self._fecha_nacimiento
        fin = self._fecha_muerte if self._fecha_muerte else "presente"
        return f"{inicio}-{fin}"
    
    def __str__(self) -> str:
        """Representación en cadena del artista."""
        info = [self._nombre]
        if self._nacionalidad:
            info.append(f"({self._nacionalidad})")
        if self._fecha_nacimiento or self._fecha_muerte:
            info.append(f"[{self.obtener_periodo_vida()}]")
        return " ".join(info)
    
    def __repr__(self) -> str:
        """Representación técnica del artista."""
        return (f"Artista(nombre='{self._nombre}', nacionalidad='{self._nacionalidad}', "
                f"fecha_nacimiento='{self._fecha_nacimiento}', fecha_muerte='{self._fecha_muerte}')")
    
    def __eq__(self, other) -> bool:
        """Compara dos artistas por igualdad."""
        if not isinstance(other, Artista):
            return False
        return (self._nombre == other._nombre and 
                self._nacionalidad == other._nacionalidad and
                self._fecha_nacimiento == other._fecha_nacimiento and
                self._fecha_muerte == other._fecha_muerte)
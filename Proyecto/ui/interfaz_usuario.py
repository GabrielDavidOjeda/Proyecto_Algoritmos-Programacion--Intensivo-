"""
Módulo de interfaz de usuario por consola para el sistema de catálogo del museo.
Proporciona menús interactivos y métodos de visualización de datos.
"""

from typing import List, Optional
from models.obra_arte import ObraArte
from models.departamento import Departamento


class InterfazUsuario:
    """
    Clase que maneja la interfaz de usuario por consola.
    Proporciona menús interactivos y métodos de visualización.
    """
    
    def __init__(self):
        """Inicializa la interfaz de usuario."""
        pass
    
    def mostrar_menu_principal(self) -> int:
        """
        Muestra el menú principal con opciones de búsqueda y gestión de cache.
        
        Returns:
            int: Opción seleccionada por el usuario (1-7)
        """
        print("\n" + "="*60)
        print("    CATÁLOGO DEL MUSEO METROPOLITANO DE ARTE")
        print("="*60)
        print("\nOpciones de búsqueda:")
        print("1. Buscar obras por departamento")
        print("2. Buscar obras por nacionalidad del artista")
        print("3. Buscar obras por nombre del artista")
        print("4. Ver detalles de una obra específica")
        print("\nGestión del sistema:")
        print("5. Ver estadísticas de cache")
        print("6. Limpiar cache manualmente")
        print("7. Salir")
        print("-"*60)
        
        while True:
            try:
                opcion = input("Seleccione una opción (1-7): ").strip()
                if opcion in ['1', '2', '3', '4', '5', '6', '7']:
                    return int(opcion)
                else:
                    print("Por favor, ingrese un número entre 1 y 7.")
            except (ValueError, KeyboardInterrupt):
                print("Entrada inválida. Por favor, ingrese un número entre 1 y 7.")
    
    def solicitar_seleccion_departamento(self, departamentos: List[Departamento]) -> int:
        """
        Solicita al usuario que seleccione un departamento de la lista.
        
        Args:
            departamentos: Lista de departamentos disponibles
            
        Returns:
            int: ID del departamento seleccionado
        """
        print("\n" + "="*50)
        print("    DEPARTAMENTOS DISPONIBLES")
        print("="*50)
        
        for i, departamento in enumerate(departamentos, 1):
            print(f"{i:2d}. {departamento.nombre}")
        
        print("-"*50)
        
        while True:
            try:
                seleccion = input(f"Seleccione un departamento (1-{len(departamentos)}): ").strip()
                indice = int(seleccion) - 1
                
                if 0 <= indice < len(departamentos):
                    return departamentos[indice].id_departamento
                else:
                    print(f"Por favor, ingrese un número entre 1 y {len(departamentos)}.")
            except (ValueError, KeyboardInterrupt):
                print("Entrada inválida. Por favor, ingrese un número válido.")
    
    def solicitar_seleccion_nacionalidad(self, nacionalidades: List[str]) -> str:
        """
        Solicita al usuario que seleccione una nacionalidad de la lista.
        
        Args:
            nacionalidades: Lista de nacionalidades disponibles
            
        Returns:
            str: Nacionalidad seleccionada
        """
        print("\n" + "="*50)
        print("    NACIONALIDADES DISPONIBLES")
        print("="*50)
        
        # Mostrar nacionalidades en columnas para mejor visualización
        for i, nacionalidad in enumerate(nacionalidades, 1):
            print(f"{i:2d}. {nacionalidad}")
            if i % 20 == 0:  # Pausa cada 20 elementos
                input("Presione Enter para continuar...")
        
        print("-"*50)
        
        while True:
            try:
                seleccion = input(f"Seleccione una nacionalidad (1-{len(nacionalidades)}): ").strip()
                indice = int(seleccion) - 1
                
                if 0 <= indice < len(nacionalidades):
                    return nacionalidades[indice]
                else:
                    print(f"Por favor, ingrese un número entre 1 y {len(nacionalidades)}.")
            except (ValueError, KeyboardInterrupt):
                print("Entrada inválida. Por favor, ingrese un número válido.")
    
    def solicitar_nombre_artista(self) -> str:
        """
        Solicita al usuario que ingrese el nombre de un artista.
        
        Returns:
            str: Nombre del artista ingresado
        """
        print("\n" + "="*50)
        print("    BÚSQUEDA POR NOMBRE DE ARTISTA")
        print("="*50)
        print("Puede ingresar el nombre completo o parcial del artista.")
        print("Ejemplo: 'Van Gogh', 'Leonardo', 'Picasso'")
        print("-"*50)
        
        while True:
            nombre = input("Ingrese el nombre del artista: ").strip()
            if nombre:
                return nombre
            else:
                print("Por favor, ingrese un nombre válido.")
    
    def solicitar_id_obra(self) -> int:
        """
        Solicita al usuario que ingrese el ID de una obra.
        
        Returns:
            int: ID de la obra ingresado
        """
        print("\n" + "="*50)
        print("    CONSULTA DE OBRA ESPECÍFICA")
        print("="*50)
        print("Ingrese el ID de la obra que desea consultar.")
        print("Ejemplo: 436535, 459055, 437853")
        print("-"*50)
        
        while True:
            try:
                id_obra = input("Ingrese el ID de la obra: ").strip()
                return int(id_obra)
            except ValueError:
                print("Por favor, ingrese un número válido.")
    
    def mostrar_lista_obras(self, obras: List[ObraArte]) -> None:
        """
        Muestra una lista de obras en formato tabular claro.
        
        Args:
            obras: Lista de obras a mostrar
        """
        if not obras:
            self.mostrar_mensaje_info("No se encontraron obras que coincidan con los criterios de búsqueda.")
            return
        
        print("\n" + "="*95)
        print(f"    RESULTADOS DE BÚSQUEDA ({len(obras)} obra{'s' if len(obras) != 1 else ''} encontrada{'s' if len(obras) != 1 else ''})")
        print("="*95)
        
        # Encabezados de la tabla
        print(f"{'ID':>8} | {'TÍTULO':<35} | {'ARTISTA':<30} | {'DEPTO':<12}")
        print("-"*95)
        
        for obra in obras:
            # Truncar títulos y nombres largos para mantener formato
            titulo = obra.titulo[:32] + "..." if len(obra.titulo) > 35 else obra.titulo
            artista = obra.artista.nombre[:27] + "..." if len(obra.artista.nombre) > 30 else obra.artista.nombre
            departamento = obra.departamento[:9] + "..." if obra.departamento and len(obra.departamento) > 12 else (obra.departamento or "N/A")
            
            print(f"{obra.id_obra:>8} | {titulo:<35} | {artista:<30} | {departamento:<12}")
        
        print("-"*95)
        print(f"Total: {len(obras)} obra{'s' if len(obras) != 1 else ''}")
    
    def mostrar_detalles_obra(self, obra: ObraArte) -> None:
        """
        Muestra los detalles completos de una obra con formato estructurado.
        
        Args:
            obra: Obra de arte a mostrar
        """
        print("\n" + "="*70)
        print("    DETALLES DE LA OBRA")
        print("="*70)
        
        print(f"ID de la Obra:      {obra.id_obra}")
        print(f"Título:             {obra.titulo}")
        print("-"*70)
        
        print("INFORMACIÓN DEL ARTISTA:")
        print(f"  Nombre:           {obra.artista.nombre}")
        
        if obra.artista.nacionalidad:
            print(f"  Nacionalidad:     {obra.artista.nacionalidad}")
        
        if obra.artista.fecha_nacimiento:
            print(f"  Fecha Nacimiento: {obra.artista.fecha_nacimiento}")
        
        if obra.artista.fecha_muerte:
            print(f"  Fecha Muerte:     {obra.artista.fecha_muerte}")
        
        print("-"*70)
        
        print("INFORMACIÓN DE LA OBRA:")
        
        if obra.clasificacion:
            print(f"  Tipo:             {obra.clasificacion}")
        
        if obra.fecha_creacion:
            print(f"  Año de Creación:  {obra.fecha_creacion}")
        
        if obra.departamento:
            print(f"  Departamento:     {obra.departamento}")
        
        if obra.url_imagen:
            print(f"  Imagen:           Disponible")
            print("                    (Use la opción de visualización para ver la imagen)")
        else:
            print(f"  Imagen:           No disponible")
        
        print("="*70)
    
    def mostrar_detalles_obra_con_opciones(self, obra: ObraArte) -> None:
        """
        Muestra los detalles completos de una obra con opciones adicionales.
        
        Args:
            obra: Obra de arte a mostrar
        """
        self.mostrar_detalles_obra(obra)
        
        if obra.tiene_imagen():
            print("\n" + "-"*70)
            print("OPCIONES ADICIONALES:")
            print("  La obra tiene imagen disponible")
            print("  Puede visualizar la imagen usando la opción correspondiente")
            print("-"*70)
    
    def mostrar_mensaje_error(self, mensaje: str) -> None:
        """
        Muestra un mensaje de error con formato destacado.
        
        Args:
            mensaje: Mensaje de error a mostrar
        """
        print("\n" + "!"*60)
        print("    ERROR")
        print("!"*60)
        print(f"  {mensaje}")
        print("!"*60)
    
    def mostrar_mensaje_info(self, mensaje: str) -> None:
        """
        Muestra un mensaje informativo con formato destacado.
        
        Args:
            mensaje: Mensaje informativo a mostrar
        """
        print("\n" + "*"*60)
        print("    INFORMACIÓN")
        print("*"*60)
        print(f"  {mensaje}")
        print("*"*60)
    
    def mostrar_mensaje_exito(self, mensaje: str) -> None:
        """
        Muestra un mensaje de éxito con formato destacado.
        
        Args:
            mensaje: Mensaje de éxito a mostrar
        """
        print("\n" + "+"*60)
        print("    ÉXITO")
        print("+"*60)
        print(f"  {mensaje}")
        print("+"*60)
    
    def confirmar_accion(self, mensaje: str) -> bool:
        """
        Solicita confirmación del usuario para una acción.
        
        Args:
            mensaje: Mensaje de confirmación
            
        Returns:
            bool: True si el usuario confirma, False en caso contrario
        """
        while True:
            respuesta = input(f"{mensaje} (s/n): ").strip().lower()
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                return True
            elif respuesta in ['n', 'no']:
                return False
            else:
                print("Por favor, responda 's' para sí o 'n' para no.")
    
    def pausar_para_continuar(self) -> None:
        """Pausa la ejecución hasta que el usuario presione Enter."""
        input("\nPresione Enter para continuar...")
    
    def limpiar_pantalla(self) -> None:
        """Limpia la pantalla de la consola."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
#!/usr/bin/env python3
"""
Sistema de Catálogo del Museo Metropolitano de Arte

Aplicación Python para buscar y visualizar obras de arte del Metropolitan Museum of Art
utilizando su API oficial. Permite búsquedas por departamento, nacionalidad del artista
y nombre del artista, con visualización de detalles completos e imágenes.

Uso:
    python main.py [opciones]

Opciones:
    -h, --help              Mostrar esta ayuda y salir
    -v, --version           Mostrar versión del programa
    --check-resources       Verificar recursos necesarios sin iniciar la aplicación
    --nacionalidades FILE   Especificar archivo de nacionalidades personalizado
    --debug                 Activar modo debug con información adicional

Ejemplos:
    python main.py                                    # Ejecutar aplicación normal
    python main.py --check-resources                  # Solo verificar recursos
    python main.py --nacionalidades mi_archivo.txt   # Usar archivo personalizado
    python main.py --debug                           # Ejecutar con información debug

Requisitos del sistema:
    - Python 3.7 o superior
    - Conexión a internet para acceder a la API del Metropolitan Museum
    - Archivo 'nacionalidades.txt' en el directorio de la aplicación
    - Bibliotecas: requests, Pillow, tkinter (incluidas en Python estándar)

Autor: Sistema de Catálogo del Museo
Versión: 1.0.0
"""

import sys
import os
import argparse
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Importar componentes principales
from controlador_principal import ControladorPrincipal
from utils.gestor_nacionalidades import GestorNacionalidades, ErrorArchivoNacionalidades
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum


# Información de la aplicación
APP_NAME = "Sistema de Catálogo del Museo Metropolitano"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Sistema de Catálogo del Museo"
DEFAULT_NACIONALIDADES_FILE = "nacionalidades.txt"


class ConfiguracionAplicacion:
    """
    Maneja la configuración y inicialización de la aplicación.
    
    Centraliza la configuración de parámetros, validación de recursos
    y preparación del entorno de ejecución.
    """
    
    def __init__(self):
        """Inicializa la configuración con valores por defecto."""
        self.archivo_nacionalidades = DEFAULT_NACIONALIDADES_FILE
        self.modo_debug = False
        self.solo_verificar_recursos = False
        self._logger = None
    
    def configurar_desde_argumentos(self, args: argparse.Namespace) -> None:
        """
        Configura la aplicación basándose en los argumentos de línea de comandos.
        
        Args:
            args: Argumentos parseados de línea de comandos
        """
        if args.nacionalidades:
            self.archivo_nacionalidades = args.nacionalidades
        
        self.modo_debug = args.debug
        self.solo_verificar_recursos = args.check_resources
        
        # Configurar logging si está en modo debug
        if self.modo_debug:
            self._configurar_logging()
    
    def _configurar_logging(self) -> None:
        """Configura el sistema de logging para modo debug."""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('museo_catalogo_debug.log', encoding='utf-8')
            ]
        )
        self._logger = logging.getLogger(__name__)
        self._logger.info("Modo debug activado")
    
    def validar_recursos(self) -> Dict[str, Any]:
        """
        Valida que todos los recursos necesarios estén disponibles.
        
        Returns:
            Dict con el resultado de la validación y detalles de cada recurso
            
        Raises:
            Exception: Si hay errores críticos en la validación
        """
        resultado = {
            'valido': True,
            'errores': [],
            'advertencias': [],
            'recursos': {}
        }
        
        # Validar archivo de nacionalidades
        try:
            self._validar_archivo_nacionalidades(resultado)
        except Exception as e:
            resultado['errores'].append(f"Error crítico con nacionalidades: {str(e)}")
            resultado['valido'] = False
        
        # Validar conectividad con API
        try:
            self._validar_conectividad_api(resultado)
        except Exception as e:
            resultado['errores'].append(f"Error crítico con API: {str(e)}")
            resultado['valido'] = False
        
        # Validar dependencias de Python
        try:
            self._validar_dependencias_python(resultado)
        except Exception as e:
            resultado['errores'].append(f"Error con dependencias: {str(e)}")
            resultado['valido'] = False
        
        return resultado
    
    def _validar_archivo_nacionalidades(self, resultado: Dict[str, Any]) -> None:
        """
        Valida la existencia y contenido del archivo de nacionalidades.
        
        Args:
            resultado: Diccionario para almacenar resultados de validación
        """
        archivo_path = Path(self.archivo_nacionalidades)
        
        if not archivo_path.exists():
            raise FileNotFoundError(f"Archivo de nacionalidades no encontrado: {self.archivo_nacionalidades}")
        
        if not archivo_path.is_file():
            raise ValueError(f"La ruta especificada no es un archivo: {self.archivo_nacionalidades}")
        
        # Intentar cargar nacionalidades
        try:
            gestor = GestorNacionalidades(self.archivo_nacionalidades)
            gestor.cargar_nacionalidades()
            nacionalidades = gestor.obtener_nacionalidades_disponibles()
            
            if not nacionalidades:
                resultado['advertencias'].append("El archivo de nacionalidades está vacío")
            
            resultado['recursos']['nacionalidades'] = {
                'archivo': str(archivo_path.absolute()),
                'cantidad': len(nacionalidades),
                'valido': True
            }
            
            if self._logger:
                self._logger.info(f"Nacionalidades cargadas: {len(nacionalidades)}")
                
        except ErrorArchivoNacionalidades as e:
            raise Exception(f"Error al procesar archivo de nacionalidades: {str(e)}")
    
    def _validar_conectividad_api(self, resultado: Dict[str, Any]) -> None:
        """
        Valida la conectividad con la API del Metropolitan Museum.
        
        Args:
            resultado: Diccionario para almacenar resultados de validación
        """
        try:
            cliente_api = ClienteAPIMetMuseum()
            
            # Intentar obtener departamentos como test de conectividad
            departamentos = cliente_api.obtener_departamentos()
            
            if not departamentos:
                resultado['advertencias'].append("La API no devolvió departamentos")
            
            resultado['recursos']['api'] = {
                'url_base': cliente_api.BASE_URL,
                'departamentos_disponibles': len(departamentos),
                'conectividad': True
            }
            
            if self._logger:
                self._logger.info(f"API conectada - Departamentos disponibles: {len(departamentos)}")
                
        except ExcepcionesAPIMetMuseum.ErrorConexionAPI as e:
            raise Exception(f"No se puede conectar con la API del museo: {str(e)}")
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise Exception(f"Error de la API del museo: {str(e)}")
    
    def _validar_dependencias_python(self, resultado: Dict[str, Any]) -> None:
        """
        Valida que las dependencias de Python estén disponibles.
        
        Args:
            resultado: Diccionario para almacenar resultados de validación
        """
        dependencias_requeridas = [
            ('requests', 'Comunicación con API HTTP'),
            ('PIL', 'Procesamiento de imágenes'),
            ('tkinter', 'Interfaz gráfica para imágenes')
        ]
        
        dependencias_info = {}
        
        for nombre_modulo, descripcion in dependencias_requeridas:
            try:
                if nombre_modulo == 'PIL':
                    import PIL
                    version = PIL.__version__
                elif nombre_modulo == 'tkinter':
                    import tkinter
                    version = tkinter.TkVersion
                else:
                    modulo = __import__(nombre_modulo)
                    version = getattr(modulo, '__version__', 'Desconocida')
                
                dependencias_info[nombre_modulo] = {
                    'disponible': True,
                    'version': str(version),
                    'descripcion': descripcion
                }
                
                if self._logger:
                    self._logger.info(f"Dependencia {nombre_modulo} v{version} - OK")
                    
            except ImportError:
                dependencias_info[nombre_modulo] = {
                    'disponible': False,
                    'version': None,
                    'descripcion': descripcion
                }
                raise ImportError(f"Dependencia requerida no encontrada: {nombre_modulo} ({descripcion})")
        
        resultado['recursos']['dependencias'] = dependencias_info


def crear_parser_argumentos() -> argparse.ArgumentParser:
    """
    Crea y configura el parser de argumentos de línea de comandos.
    
    Returns:
        ArgumentParser configurado con todas las opciones disponibles
    """
    parser = argparse.ArgumentParser(
        prog='main.py',
        description=f'{APP_NAME} v{APP_VERSION}',
        epilog=f'Desarrollado por {APP_AUTHOR}',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{APP_NAME} v{APP_VERSION}'
    )
    
    parser.add_argument(
        '--check-resources',
        action='store_true',
        help='Verificar recursos necesarios sin iniciar la aplicación'
    )
    
    parser.add_argument(
        '--nacionalidades',
        type=str,
        metavar='FILE',
        help=f'Especificar archivo de nacionalidades personalizado (por defecto: {DEFAULT_NACIONALIDADES_FILE})'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activar modo debug con información adicional'
    )
    
    return parser


def mostrar_banner() -> None:
    """Muestra el banner de bienvenida de la aplicación."""
    print("=" * 70)
    print(f"    {APP_NAME}")
    print(f"    Versión {APP_VERSION}")
    print("=" * 70)
    print("    Explora la colección del Metropolitan Museum of Art")
    print("    Busca obras por departamento, nacionalidad o artista")
    print("=" * 70)
    print()


def mostrar_resultado_validacion(resultado: Dict[str, Any]) -> None:
    """
    Muestra el resultado de la validación de recursos de forma detallada.
    
    Args:
        resultado: Diccionario con los resultados de validación
    """
    print("\n" + "="*50)
    print("    VERIFICACIÓN DE RECURSOS DEL SISTEMA")
    print("="*50)
    
    # Mostrar estado general
    if resultado['valido']:
        print("✓ Estado general: TODOS LOS RECURSOS DISPONIBLES")
    else:
        print("✗ Estado general: ERRORES ENCONTRADOS")
    
    # Mostrar detalles de recursos
    if 'recursos' in resultado:
        print("\nDetalles de recursos:")
        
        # Nacionalidades
        if 'nacionalidades' in resultado['recursos']:
            nac = resultado['recursos']['nacionalidades']
            print(f"  • Nacionalidades: ✓ {nac['cantidad']} disponibles")
            print(f"    Archivo: {nac['archivo']}")
        
        # API
        if 'api' in resultado['recursos']:
            api = resultado['recursos']['api']
            print(f"  • API del Museo: ✓ Conectada")
            print(f"    URL: {api['url_base']}")
            print(f"    Departamentos: {api['departamentos_disponibles']}")
        
        # Dependencias
        if 'dependencias' in resultado['recursos']:
            print("  • Dependencias de Python:")
            for nombre, info in resultado['recursos']['dependencias'].items():
                estado = "✓" if info['disponible'] else "✗"
                version = f"v{info['version']}" if info['version'] else "No disponible"
                print(f"    - {nombre}: {estado} {version}")
    
    # Mostrar advertencias
    if resultado['advertencias']:
        print("\nAdvertencias:")
        for advertencia in resultado['advertencias']:
            print(f"  ⚠ {advertencia}")
    
    # Mostrar errores
    if resultado['errores']:
        print("\nErrores encontrados:")
        for error in resultado['errores']:
            print(f"  ✗ {error}")
    
    print("="*50)


def main() -> int:
    """
    Función principal de la aplicación.
    
    Maneja la inicialización, configuración y ejecución de la aplicación
    basándose en los argumentos de línea de comandos.
    
    Returns:
        int: Código de salida (0 = éxito, 1 = error)
    """
    try:
        # Parsear argumentos de línea de comandos
        parser = crear_parser_argumentos()
        args = parser.parse_args()
        
        # Crear y configurar la aplicación
        config = ConfiguracionAplicacion()
        config.configurar_desde_argumentos(args)
        
        # Mostrar banner si no es solo verificación
        if not config.solo_verificar_recursos:
            mostrar_banner()
        
        # Validar recursos del sistema
        print("Verificando recursos del sistema...")
        resultado_validacion = config.validar_recursos()
        
        # Si solo se solicita verificación, mostrar resultados y salir
        if config.solo_verificar_recursos:
            mostrar_resultado_validacion(resultado_validacion)
            return 0 if resultado_validacion['valido'] else 1
        
        # Verificar que los recursos estén disponibles antes de continuar
        if not resultado_validacion['valido']:
            print("\n✗ Error: No se pueden inicializar los recursos necesarios")
            mostrar_resultado_validacion(resultado_validacion)
            print("\nUse 'python main.py --check-resources' para más detalles")
            return 1
        
        # Mostrar advertencias si las hay
        if resultado_validacion['advertencias']:
            print("\nAdvertencias encontradas:")
            for advertencia in resultado_validacion['advertencias']:
                print(f"  ⚠ {advertencia}")
            print()
        
        # Inicializar y ejecutar la aplicación principal
        print("Iniciando aplicación...")
        controlador = ControladorPrincipal()
        controlador.iniciar_aplicacion()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nAplicación interrumpida por el usuario.")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error crítico al iniciar la aplicación: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifique que el archivo 'nacionalidades.txt' existe y es válido")
        print("2. Verifique su conexión a internet")
        print("3. Ejecute 'python main.py --check-resources' para diagnóstico detallado")
        print("4. Use 'python main.py --help' para ver todas las opciones disponibles")
        
        return 1


if __name__ == "__main__":
    # Configurar la codificación de salida para caracteres especiales
    if sys.stdout.encoding != 'utf-8':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    # Ejecutar aplicación principal
    exit_code = main()
    sys.exit(exit_code)
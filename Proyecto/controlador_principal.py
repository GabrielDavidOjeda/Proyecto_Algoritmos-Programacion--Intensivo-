"""
Controlador principal del sistema de catálogo del museo.
Coordina las operaciones entre la interfaz de usuario y los servicios de negocio.
Incluye sistema de cache compartido para optimizar rendimiento.
"""

import sys
import logging
from typing import Optional
from ui.interfaz_usuario import InterfazUsuario
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from services.servicio_busqueda import ServicioBusqueda, ExcepcionesServicioBusqueda
from services.servicio_obras import ServicioObras
from utils.gestor_nacionalidades import GestorNacionalidades, ErrorArchivoNacionalidades
from ui.visualizador_imagenes import VisualizadorImagenes
from utils.almacen_datos import AlmacenDatos


class ControladorPrincipal:
    """
    Controlador principal que coordina el flujo de la aplicación.
    
    Maneja la inicialización de dependencias, el bucle principal de la aplicación
    y la coordinación entre los diferentes servicios y la interfaz de usuario.
    """
    
    def __init__(self):
        """Inicializa el controlador con todas sus dependencias y cache compartido."""
        # Inicializar logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando ControladorPrincipal")
        
        # Inicializar sistema de cache compartido
        self._almacen_datos = AlmacenDatos()
        
        # Inicializar componentes principales
        self._cliente_api = ClienteAPIMetMuseum()
        self._gestor_nacionalidades = GestorNacionalidades("nacionalidades.txt")
        self._visualizador_imagenes = VisualizadorImagenes()
        
        # Inicializar servicios con cache compartido
        self._servicio_busqueda = ServicioBusqueda(
            self._cliente_api, 
            self._gestor_nacionalidades,
            self._almacen_datos
        )
        self._servicio_obras = ServicioObras(
            self._cliente_api, 
            self._visualizador_imagenes,
            self._almacen_datos
        )
        self._interfaz = InterfazUsuario()
        
        # Estado de la aplicación
        self._aplicacion_iniciada = False
    
    def iniciar_aplicacion(self) -> None:
        """
        Inicia la aplicación con el bucle principal.
        
        Inicializa los recursos necesarios y ejecuta el bucle principal
        hasta que el usuario decida salir.
        """
        try:
            # Inicializar recursos
            self._inicializar_recursos()
            
            # Mostrar mensaje de bienvenida
            self._interfaz.mostrar_mensaje_exito(
                "Sistema de Catálogo del Museo Metropolitano iniciado correctamente"
            )
            
            self._aplicacion_iniciada = True
            
            # Bucle principal de la aplicación
            while True:
                try:
                    opcion = self._interfaz.mostrar_menu_principal()
                    
                    if opcion == 1:
                        self.procesar_busqueda_por_departamento()
                    elif opcion == 2:
                        self.procesar_busqueda_por_nacionalidad()
                    elif opcion == 3:
                        self.procesar_busqueda_por_artista()
                    elif opcion == 4:
                        self.procesar_mostrar_detalles_obra()
                    elif opcion == 5:
                        self._mostrar_estadisticas_cache()
                    elif opcion == 6:
                        self._limpiar_cache_manual()
                    elif opcion == 7:
                        self._interfaz.mostrar_mensaje_info("¡Gracias por usar el sistema!")
                        break
                    
                    # Pausa para que el usuario pueda leer los resultados
                    self._interfaz.pausar_para_continuar()
                    
                except KeyboardInterrupt:
                    if self._interfaz.confirmar_accion("¿Desea salir de la aplicación?"):
                        break
                except Exception as e:
                    self._manejar_excepcion(e)
                    self._interfaz.pausar_para_continuar()
        
        except Exception as e:
            self._manejar_excepcion_critica(e)
        finally:
            self._finalizar_aplicacion()
    
    def procesar_busqueda_por_departamento(self) -> None:
        """
        Procesa la búsqueda de obras por departamento integrando servicios y UI.
        
        Obtiene la lista de departamentos, permite al usuario seleccionar uno,
        y muestra las obras correspondientes.
        """
        try:
            # Obtener departamentos disponibles
            departamentos = self._servicio_busqueda.obtener_departamentos_disponibles()
            
            if not departamentos:
                self._interfaz.mostrar_mensaje_info(
                    "No hay departamentos disponibles en este momento."
                )
                return
            
            # Solicitar selección de departamento
            id_departamento = self._interfaz.solicitar_seleccion_departamento(departamentos)
            
            # Buscar obras del departamento
            self._interfaz.mostrar_mensaje_info("Buscando obras del departamento...")
            obras = self._servicio_busqueda.buscar_por_departamento(id_departamento)
            
            # Mostrar resultados
            self._interfaz.mostrar_lista_obras(obras)
            
            # Ofrecer ver detalles de una obra específica
            if obras:
                self._ofrecer_ver_detalles_obra()
        
        except ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido as e:
            self._interfaz.mostrar_mensaje_error(f"Departamento inválido: {str(e)}")
        except ExcepcionesServicioBusqueda.ErrorServicioBusqueda as e:
            self._interfaz.mostrar_mensaje_error(f"Error en búsqueda: {str(e)}")
        except Exception as e:
            self._manejar_excepcion(e)
    
    def procesar_busqueda_por_nacionalidad(self) -> None:
        """
        Procesa la búsqueda de obras por nacionalidad con validación.
        
        Obtiene las nacionalidades disponibles, permite al usuario seleccionar una,
        valida la selección y muestra las obras correspondientes.
        """
        try:
            # Obtener nacionalidades disponibles
            nacionalidades = self._gestor_nacionalidades.obtener_nacionalidades_disponibles()
            
            if not nacionalidades:
                self._interfaz.mostrar_mensaje_error(
                    "No hay nacionalidades disponibles. Verifique el archivo de nacionalidades."
                )
                return
            
            # Solicitar selección de nacionalidad
            nacionalidad_seleccionada = self._interfaz.solicitar_seleccion_nacionalidad(nacionalidades)
            
            # Buscar obras por nacionalidad
            self._interfaz.mostrar_mensaje_info(f"Buscando obras de artistas de nacionalidad '{nacionalidad_seleccionada}'...")
            obras = self._servicio_busqueda.buscar_por_nacionalidad(nacionalidad_seleccionada)
            
            # Mostrar resultados
            self._interfaz.mostrar_lista_obras(obras)
            
            # Ofrecer ver detalles de una obra específica
            if obras:
                self._ofrecer_ver_detalles_obra()
        
        except ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida as e:
            self._interfaz.mostrar_mensaje_error(f"Nacionalidad inválida: {str(e)}")
        except ExcepcionesServicioBusqueda.ErrorServicioBusqueda as e:
            self._interfaz.mostrar_mensaje_error(f"Error en búsqueda: {str(e)}")
        except ErrorArchivoNacionalidades as e:
            self._interfaz.mostrar_mensaje_error(f"Error con archivo de nacionalidades: {str(e)}")
        except Exception as e:
            self._manejar_excepcion(e)
    
    def procesar_busqueda_por_artista(self) -> None:
        """
        Procesa la búsqueda de obras por nombre de artista con manejo de entrada.
        
        Solicita el nombre del artista, sanitiza la entrada y muestra las obras
        que coinciden con el criterio de búsqueda.
        """
        try:
            # Solicitar nombre del artista
            nombre_artista = self._interfaz.solicitar_nombre_artista()
            
            # Buscar obras por nombre de artista
            self._interfaz.mostrar_mensaje_info(f"Buscando obras del artista '{nombre_artista}'...")
            obras = self._servicio_busqueda.buscar_por_nombre_artista(nombre_artista)
            
            # Mostrar resultados
            self._interfaz.mostrar_lista_obras(obras)
            
            # Ofrecer ver detalles de una obra específica
            if obras:
                self._ofrecer_ver_detalles_obra()
        
        except ExcepcionesServicioBusqueda.ErrorServicioBusqueda as e:
            self._interfaz.mostrar_mensaje_error(f"Error en búsqueda por artista: {str(e)}")
        except Exception as e:
            self._manejar_excepcion(e)
    
    def procesar_mostrar_detalles_obra(self) -> None:
        """
        Procesa la solicitud de mostrar detalles de una obra específica con validación de ID.
        
        Solicita el ID de la obra, valida que sea un número válido,
        obtiene los detalles y los muestra al usuario.
        """
        try:
            # Solicitar ID de obra
            id_obra = self._interfaz.solicitar_id_obra()
            
            # Obtener detalles de la obra
            self._interfaz.mostrar_mensaje_info(f"Obteniendo detalles de la obra {id_obra}...")
            obra = self._servicio_obras.obtener_detalles_obra(id_obra)
            
            # Mostrar detalles completos con opciones
            self._interfaz.mostrar_detalles_obra_con_opciones(obra)
            
            # Ofrecer visualizar imagen si está disponible
            if obra.tiene_imagen():
                if self._interfaz.confirmar_accion("¿Desea ver la imagen de la obra?"):
                    self._mostrar_imagen_obra(obra)
        
        except ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado:
            self._interfaz.mostrar_mensaje_error(f"No se encontró una obra con ID {id_obra}")
        except ExcepcionesAPIMetMuseum.ErrorDatosIncompletos as e:
            self._interfaz.mostrar_mensaje_error(f"Datos incompletos para la obra: {str(e)}")
        except ValueError as e:
            self._interfaz.mostrar_mensaje_error(f"ID de obra inválido: {str(e)}")
        except Exception as e:
            self._manejar_excepcion(e)
    
    def _inicializar_recursos(self) -> None:
        """
        Inicializa los recursos necesarios para la aplicación.
        
        Carga el archivo de nacionalidades y verifica la conectividad con la API.
        
        Raises:
            Exception: Si hay errores críticos en la inicialización
        """
        try:
            # Cargar archivo de nacionalidades
            self._interfaz.mostrar_mensaje_info("Cargando archivo de nacionalidades...")
            self._gestor_nacionalidades.cargar_nacionalidades()
            
            # Verificar conectividad con la API
            self._interfaz.mostrar_mensaje_info("Verificando conectividad con la API del museo...")
            departamentos = self._cliente_api.obtener_departamentos()
            
            if not departamentos:
                raise Exception("No se pudieron obtener departamentos de la API")
            
        except ErrorArchivoNacionalidades as e:
            raise Exception(f"Error al cargar nacionalidades: {str(e)}")
        except ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum as e:
            raise Exception(f"Error de conectividad con la API: {str(e)}")
    
    def _ofrecer_ver_detalles_obra(self) -> None:
        """
        Ofrece al usuario la opción de ver detalles de una obra específica.
        
        Solicita el ID de una obra de los resultados mostrados y muestra sus detalles.
        """
        if self._interfaz.confirmar_accion("¿Desea ver los detalles de alguna obra específica?"):
            try:
                id_obra = self._interfaz.solicitar_id_obra()
                obra = self._servicio_obras.obtener_detalles_obra(id_obra)
                self._interfaz.mostrar_detalles_obra_con_opciones(obra)
                
                # Ofrecer visualizar imagen
                if obra.tiene_imagen():
                    if self._interfaz.confirmar_accion("¿Desea ver la imagen de la obra?"):
                        self._mostrar_imagen_obra(obra)
                        
            except Exception as e:
                self._interfaz.mostrar_mensaje_error(f"Error al obtener detalles: {str(e)}")
    
    def _mostrar_imagen_obra(self, obra) -> None:
        """
        Muestra la imagen de una obra usando el servicio de obras integrado.
        
        Args:
            obra: Obra de arte con imagen a mostrar
        """
        try:
            self._interfaz.mostrar_mensaje_info("Abriendo imagen de la obra...")
            self._servicio_obras.mostrar_imagen_obra(obra)
            self._interfaz.mostrar_mensaje_exito("Imagen mostrada correctamente")
            
        except ValueError as e:
            self._interfaz.mostrar_mensaje_error(f"Error de validación: {str(e)}")
        except Exception as e:
            self._interfaz.mostrar_mensaje_error(f"Error al mostrar imagen: {str(e)}")
    
    def _manejar_excepcion(self, excepcion: Exception) -> None:
        """
        Maneja excepciones de manera centralizada durante la ejecución normal.
        
        Args:
            excepcion (Exception): Excepción a manejar
        """
        # Determinar el tipo de error y mostrar mensaje apropiado
        if isinstance(excepcion, ExcepcionesAPIMetMuseum.ErrorConexionAPI):
            self._interfaz.mostrar_mensaje_error(
                "Error de conexión con la API del museo. "
                "Verifique su conexión a internet e intente nuevamente."
            )
        elif isinstance(excepcion, ExcepcionesAPIMetMuseum.ErrorRateLimitAPI):
            self._interfaz.mostrar_mensaje_error(
                "Se ha excedido el límite de consultas a la API. "
                "Por favor, espere unos momentos antes de continuar."
            )
        elif isinstance(excepcion, (ExcepcionesServicioBusqueda.ErrorServicioBusqueda, 
                                   ExcepcionesAPIMetMuseum.ErrorAPIMetMuseum)):
            self._interfaz.mostrar_mensaje_error(f"Error del servicio: {str(excepcion)}")
        elif isinstance(excepcion, KeyboardInterrupt):
            # El KeyboardInterrupt se maneja en el bucle principal
            raise excepcion
        else:
            # Error inesperado
            self._interfaz.mostrar_mensaje_error(
                f"Error inesperado: {str(excepcion)}. "
                "Si el problema persiste, contacte al administrador del sistema."
            )
    
    def _manejar_excepcion_critica(self, excepcion: Exception) -> None:
        """
        Maneja excepciones críticas que impiden el inicio de la aplicación.
        
        Args:
            excepcion (Exception): Excepción crítica a manejar
        """
        print("\n" + "!"*70)
        print("    ERROR CRÍTICO - NO SE PUEDE INICIAR LA APLICACIÓN")
        print("!"*70)
        print(f"  Error: {str(excepcion)}")
        print("!"*70)
        print("\nPosibles soluciones:")
        print("1. Verifique que el archivo 'nacionalidades.txt' existe")
        print("2. Verifique su conexión a internet")
        print("3. Intente ejecutar la aplicación más tarde")
        print("4. Contacte al administrador del sistema si el problema persiste")
    
    def _mostrar_estadisticas_cache(self) -> None:
        """
        Muestra las estadísticas del sistema de cache.
        """
        try:
            estadisticas = self._almacen_datos.obtener_estadisticas_cache()
            
            print("\n" + "="*60)
            print("    ESTADÍSTICAS DEL SISTEMA DE CACHE")
            print("="*60)
            
            print(f"\nDatos en cache:")
            print(f"  Obras almacenadas: {estadisticas['obras_en_cache']}")
            print(f"  Búsquedas almacenadas: {estadisticas['busquedas_en_cache']}")
            print(f"  Departamentos en cache: {estadisticas['departamentos_en_cache']}")
            print(f"  IDs de departamentos: {estadisticas['ids_departamentos_en_cache']}")
            
            print(f"\nRendimiento del cache:")
            print(f"  Hit ratio obras: {estadisticas['hit_ratio_obras']:.2%}")
            print(f"  Hit ratio departamentos: {estadisticas['hit_ratio_departamentos']:.2%}")
            print(f"  Hit ratio búsquedas: {estadisticas['hit_ratio_busquedas']:.2%}")
            
            print(f"\nUso de memoria:")
            print(f"  Memoria estimada: {estadisticas['memoria_estimada_kb']} KB")
            
            print(f"\nOperaciones:")
            print(f"  Hits obras: {estadisticas['hits_obras']}")
            print(f"  Misses obras: {estadisticas['misses_obras']}")
            print(f"  Limpiezas automáticas: {estadisticas['limpiezas_automaticas']}")
            
            print("="*60)
            
        except Exception as e:
            self._interfaz.mostrar_mensaje_error(f"Error al obtener estadísticas: {str(e)}")
    
    def _limpiar_cache_manual(self) -> None:
        """
        Realiza una limpieza manual del cache.
        """
        try:
            if self._interfaz.confirmar_accion("¿Desea limpiar el cache del sistema?"):
                resultado = self._almacen_datos.limpiar_cache_manual()
                
                print("\n" + "="*50)
                print("    RESULTADO DE LIMPIEZA DE CACHE")
                print("="*50)
                print(f"Obras eliminadas: {resultado['obras_eliminadas']}")
                print(f"Búsquedas eliminadas: {resultado['busquedas_eliminadas']}")
                print(f"IDs departamentos eliminados: {resultado['ids_departamentos_eliminados']}")
                print(f"Departamentos eliminados: {resultado['departamentos_eliminados']}")
                print("="*50)
                
                self._interfaz.mostrar_mensaje_exito("Cache limpiado correctamente")
            
        except Exception as e:
            self._interfaz.mostrar_mensaje_error(f"Error al limpiar cache: {str(e)}")
    
    def _finalizar_aplicacion(self) -> None:
        """
        Realiza tareas de limpieza al finalizar la aplicación.
        """
        if self._aplicacion_iniciada:
            try:
                # Limpiar recursos del visualizador de imágenes
                self._visualizador_imagenes.limpiar_cache()
                
                # Mostrar estadísticas finales del cache
                estadisticas = self._almacen_datos.obtener_estadisticas_cache()
                print(f"\nEstadísticas finales del cache:")
                print(f"  Obras consultadas: {estadisticas['hits_obras'] + estadisticas['misses_obras']}")
                print(f"  Eficiencia del cache: {estadisticas['hit_ratio_obras']:.1%}")
                
            except Exception:
                pass  # Ignorar errores de limpieza
        
        print("\nAplicación finalizada.")


def main():
    """Función principal para ejecutar la aplicación."""
    controlador = ControladorPrincipal()
    controlador.iniciar_aplicacion()


if __name__ == "__main__":
    main()
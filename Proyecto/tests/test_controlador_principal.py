"""
Tests unitarios para el controlador principal del sistema de catálogo del museo.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controlador_principal import ControladorPrincipal
from services.cliente_api_met_museum import ExcepcionesAPIMetMuseum
from services.servicio_busqueda import ExcepcionesServicioBusqueda
from utils.gestor_nacionalidades import ErrorArchivoNacionalidades
from models.obra_arte import ObraArte
from models.artista import Artista
from models.departamento import Departamento


class TestControladorPrincipal(unittest.TestCase):
    """Tests para la clase ControladorPrincipal"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear mocks para todas las dependencias
        self.mock_cliente_api = Mock()
        self.mock_gestor_nacionalidades = Mock()
        self.mock_servicio_busqueda = Mock()
        self.mock_servicio_obras = Mock()
        self.mock_visualizador_imagenes = Mock()
        self.mock_interfaz = Mock()
        
        # Configurar el controlador con mocks
        with patch('controlador_principal.ClienteAPIMetMuseum', return_value=self.mock_cliente_api), \
             patch('controlador_principal.GestorNacionalidades', return_value=self.mock_gestor_nacionalidades), \
             patch('controlador_principal.ServicioBusqueda', return_value=self.mock_servicio_busqueda), \
             patch('controlador_principal.ServicioObras', return_value=self.mock_servicio_obras), \
             patch('controlador_principal.VisualizadorImagenes', return_value=self.mock_visualizador_imagenes), \
             patch('controlador_principal.InterfazUsuario', return_value=self.mock_interfaz):
            
            self.controlador = ControladorPrincipal()
    
    def test_inicializacion_controlador(self):
        """Test de inicialización correcta del controlador"""
        # Verificar que el controlador se inicializa correctamente
        self.assertIsNotNone(self.controlador._cliente_api)
        self.assertIsNotNone(self.controlador._gestor_nacionalidades)
        self.assertIsNotNone(self.controlador._servicio_busqueda)
        self.assertIsNotNone(self.controlador._servicio_obras)
        self.assertIsNotNone(self.controlador._visualizador_imagenes)
        self.assertIsNotNone(self.controlador._interfaz)
        self.assertFalse(self.controlador._aplicacion_iniciada)
    
    @patch('controlador_principal.ControladorPrincipal._inicializar_recursos')
    def test_iniciar_aplicacion_salida_inmediata(self, mock_inicializar):
        """Test de inicio de aplicación con salida inmediata"""
        # Configurar mock para salir inmediatamente (opción 5)
        self.mock_interfaz.mostrar_menu_principal.return_value = 5
        
        # Ejecutar
        self.controlador.iniciar_aplicacion()
        
        # Verificar
        mock_inicializar.assert_called_once()
        self.mock_interfaz.mostrar_mensaje_exito.assert_called_once()
        self.mock_interfaz.mostrar_menu_principal.assert_called_once()
        self.mock_interfaz.mostrar_mensaje_info.assert_called_with("¡Gracias por usar el sistema!")
        self.assertTrue(self.controlador._aplicacion_iniciada)
    
    @patch('controlador_principal.ControladorPrincipal._inicializar_recursos')
    def test_iniciar_aplicacion_con_opciones_menu(self, mock_inicializar):
        """Test de inicio de aplicación con diferentes opciones del menú"""
        # Configurar secuencia de opciones: 1, 2, 3, 4, 5 (salir)
        self.mock_interfaz.mostrar_menu_principal.side_effect = [1, 2, 3, 4, 5]
        
        # Configurar mocks para evitar errores en los métodos de procesamiento
        self.mock_servicio_busqueda.obtener_departamentos_disponibles.return_value = []
        self.mock_gestor_nacionalidades.obtener_nacionalidades_disponibles.return_value = []
        self.mock_interfaz.solicitar_nombre_artista.return_value = "Test Artist"
        self.mock_servicio_busqueda.buscar_por_nombre_artista.return_value = []
        self.mock_interfaz.solicitar_id_obra.return_value = 12345
        
        # Ejecutar
        self.controlador.iniciar_aplicacion()
        
        # Verificar que se llamaron todos los métodos de procesamiento
        self.assertEqual(self.mock_interfaz.mostrar_menu_principal.call_count, 5)
        self.mock_interfaz.pausar_para_continuar.assert_called()
    
    def test_procesar_busqueda_por_departamento_exitosa(self):
        """Test de búsqueda por departamento exitosa"""
        # Configurar datos de prueba
        departamentos = [
            Departamento(1, "American Decorative Arts"),
            Departamento(3, "Ancient Near Eastern Art")
        ]
        artista = Artista("Test Artist", "American")
        obras = [ObraArte(12345, "Test Artwork", artista)]
        
        # Configurar mocks
        self.mock_servicio_busqueda.obtener_departamentos_disponibles.return_value = departamentos
        self.mock_interfaz.solicitar_seleccion_departamento.return_value = 1
        self.mock_servicio_busqueda.buscar_por_departamento.return_value = obras
        self.mock_interfaz.confirmar_accion.return_value = False
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_departamento()
        
        # Verificar
        self.mock_servicio_busqueda.obtener_departamentos_disponibles.assert_called_once()
        self.mock_interfaz.solicitar_seleccion_departamento.assert_called_once_with(departamentos)
        self.mock_servicio_busqueda.buscar_por_departamento.assert_called_once_with(1)
        self.mock_interfaz.mostrar_lista_obras.assert_called_once_with(obras)
    
    def test_procesar_busqueda_por_departamento_sin_departamentos(self):
        """Test de búsqueda por departamento cuando no hay departamentos"""
        # Configurar mock para retornar lista vacía
        self.mock_servicio_busqueda.obtener_departamentos_disponibles.return_value = []
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_departamento()
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_info.assert_called_with(
            "No hay departamentos disponibles en este momento."
        )
        self.mock_interfaz.solicitar_seleccion_departamento.assert_not_called()
    
    def test_procesar_busqueda_por_departamento_error_departamento_invalido(self):
        """Test de manejo de error de departamento inválido"""
        # Configurar mocks
        departamentos = [Departamento(1, "Test Department")]
        self.mock_servicio_busqueda.obtener_departamentos_disponibles.return_value = departamentos
        self.mock_interfaz.solicitar_seleccion_departamento.return_value = 999
        self.mock_servicio_busqueda.buscar_por_departamento.side_effect = \
            ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido("Departamento inválido")
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_departamento()
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Departamento inválido: Departamento inválido"
        )
    
    def test_procesar_busqueda_por_nacionalidad_exitosa(self):
        """Test de búsqueda por nacionalidad exitosa"""
        # Configurar datos de prueba
        nacionalidades = ["American", "French", "Italian"]
        artista = Artista("Test Artist", "American")
        obras = [ObraArte(12345, "Test Artwork", artista)]
        
        # Configurar mocks
        self.mock_gestor_nacionalidades.obtener_nacionalidades_disponibles.return_value = nacionalidades
        self.mock_interfaz.solicitar_seleccion_nacionalidad.return_value = "American"
        self.mock_servicio_busqueda.buscar_por_nacionalidad.return_value = obras
        self.mock_interfaz.confirmar_accion.return_value = False
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_nacionalidad()
        
        # Verificar
        self.mock_gestor_nacionalidades.obtener_nacionalidades_disponibles.assert_called_once()
        self.mock_interfaz.solicitar_seleccion_nacionalidad.assert_called_once_with(nacionalidades)
        self.mock_servicio_busqueda.buscar_por_nacionalidad.assert_called_once_with("American")
        self.mock_interfaz.mostrar_lista_obras.assert_called_once_with(obras)
    
    def test_procesar_busqueda_por_nacionalidad_sin_nacionalidades(self):
        """Test de búsqueda por nacionalidad cuando no hay nacionalidades"""
        # Configurar mock para retornar lista vacía
        self.mock_gestor_nacionalidades.obtener_nacionalidades_disponibles.return_value = []
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_nacionalidad()
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "No hay nacionalidades disponibles. Verifique el archivo de nacionalidades."
        )
        self.mock_interfaz.solicitar_seleccion_nacionalidad.assert_not_called()
    
    def test_procesar_busqueda_por_artista_exitosa(self):
        """Test de búsqueda por artista exitosa"""
        # Configurar datos de prueba
        artista = Artista("Van Gogh", "Dutch")
        obras = [ObraArte(12345, "Starry Night", artista)]
        
        # Configurar mocks
        self.mock_interfaz.solicitar_nombre_artista.return_value = "Van Gogh"
        self.mock_servicio_busqueda.buscar_por_nombre_artista.return_value = obras
        self.mock_interfaz.confirmar_accion.return_value = False
        
        # Ejecutar
        self.controlador.procesar_busqueda_por_artista()
        
        # Verificar
        self.mock_interfaz.solicitar_nombre_artista.assert_called_once()
        self.mock_servicio_busqueda.buscar_por_nombre_artista.assert_called_once_with("Van Gogh")
        self.mock_interfaz.mostrar_lista_obras.assert_called_once_with(obras)
    
    def test_procesar_mostrar_detalles_obra_exitosa(self):
        """Test de mostrar detalles de obra exitosa"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, url_imagen="http://example.com/image.jpg")
        
        # Configurar mocks
        self.mock_interfaz.solicitar_id_obra.return_value = 12345
        self.mock_servicio_obras.obtener_detalles_obra.return_value = obra
        self.mock_interfaz.confirmar_accion.return_value = False
        
        # Ejecutar
        self.controlador.procesar_mostrar_detalles_obra()
        
        # Verificar
        self.mock_interfaz.solicitar_id_obra.assert_called_once()
        self.mock_servicio_obras.obtener_detalles_obra.assert_called_once_with(12345)
        self.mock_interfaz.mostrar_detalles_obra_con_opciones.assert_called_once_with(obra)
    
    def test_procesar_mostrar_detalles_obra_con_imagen(self):
        """Test de mostrar detalles de obra con visualización de imagen"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, url_imagen="http://example.com/image.jpg")
        
        # Configurar mocks
        self.mock_interfaz.solicitar_id_obra.return_value = 12345
        self.mock_servicio_obras.obtener_detalles_obra.return_value = obra
        self.mock_interfaz.confirmar_accion.return_value = True
        
        # Ejecutar
        self.controlador.procesar_mostrar_detalles_obra()
        
        # Verificar
        self.mock_servicio_obras.mostrar_imagen_obra.assert_called_once_with(obra)
    
    def test_procesar_mostrar_detalles_obra_no_encontrada(self):
        """Test de manejo de obra no encontrada"""
        # Configurar mock para lanzar excepción
        self.mock_interfaz.solicitar_id_obra.return_value = 99999
        self.mock_servicio_obras.obtener_detalles_obra.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado("Obra no encontrada")
        
        # Ejecutar
        self.controlador.procesar_mostrar_detalles_obra()
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "No se encontró una obra con ID 99999"
        )
    
    def test_inicializar_recursos_exitoso(self):
        """Test de inicialización exitosa de recursos"""
        # Configurar mocks
        departamentos = [Departamento(1, "Test Department")]
        self.mock_cliente_api.obtener_departamentos.return_value = departamentos
        
        # Ejecutar
        self.controlador._inicializar_recursos()
        
        # Verificar
        self.mock_gestor_nacionalidades.cargar_nacionalidades.assert_called_once()
        self.mock_cliente_api.obtener_departamentos.assert_called_once()
    
    def test_inicializar_recursos_error_nacionalidades(self):
        """Test de error al inicializar recursos por archivo de nacionalidades"""
        # Configurar mock para lanzar excepción
        self.mock_gestor_nacionalidades.cargar_nacionalidades.side_effect = \
            ErrorArchivoNacionalidades("Archivo no encontrado")
        
        # Ejecutar y verificar excepción
        with self.assertRaises(Exception) as context:
            self.controlador._inicializar_recursos()
        
        self.assertIn("Error al cargar nacionalidades", str(context.exception))
    
    def test_inicializar_recursos_error_api(self):
        """Test de error al inicializar recursos por problema de API"""
        # Configurar mocks
        self.mock_cliente_api.obtener_departamentos.side_effect = \
            ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        # Ejecutar y verificar excepción
        with self.assertRaises(Exception) as context:
            self.controlador._inicializar_recursos()
        
        self.assertIn("Error de conectividad con la API", str(context.exception))
    
    def test_manejar_excepcion_error_conexion_api(self):
        """Test de manejo de excepción de conexión API"""
        excepcion = ExcepcionesAPIMetMuseum.ErrorConexionAPI("Error de conexión")
        
        # Ejecutar
        self.controlador._manejar_excepcion(excepcion)
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Error de conexión con la API del museo. "
            "Verifique su conexión a internet e intente nuevamente."
        )
    
    def test_manejar_excepcion_rate_limit(self):
        """Test de manejo de excepción de límite de velocidad"""
        excepcion = ExcepcionesAPIMetMuseum.ErrorRateLimitAPI("Rate limit excedido")
        
        # Ejecutar
        self.controlador._manejar_excepcion(excepcion)
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Se ha excedido el límite de consultas a la API. "
            "Por favor, espere unos momentos antes de continuar."
        )
    
    def test_manejar_excepcion_generica(self):
        """Test de manejo de excepción genérica"""
        excepcion = ValueError("Error genérico")
        
        # Ejecutar
        self.controlador._manejar_excepcion(excepcion)
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Error inesperado: Error genérico. "
            "Si el problema persiste, contacte al administrador del sistema."
        )
    
    def test_ofrecer_ver_detalles_obra_aceptado(self):
        """Test de ofrecer ver detalles cuando el usuario acepta"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista)
        
        # Configurar mocks
        self.mock_interfaz.confirmar_accion.return_value = True
        self.mock_interfaz.solicitar_id_obra.return_value = 12345
        self.mock_servicio_obras.obtener_detalles_obra.return_value = obra
        
        # Ejecutar
        self.controlador._ofrecer_ver_detalles_obra()
        
        # Verificar
        self.mock_interfaz.confirmar_accion.assert_called_with(
            "¿Desea ver los detalles de alguna obra específica?"
        )
        self.mock_servicio_obras.obtener_detalles_obra.assert_called_once_with(12345)
        self.mock_interfaz.mostrar_detalles_obra_con_opciones.assert_called_once_with(obra)
    
    def test_ofrecer_ver_detalles_obra_rechazado(self):
        """Test de ofrecer ver detalles cuando el usuario rechaza"""
        # Configurar mock
        self.mock_interfaz.confirmar_accion.return_value = False
        
        # Ejecutar
        self.controlador._ofrecer_ver_detalles_obra()
        
        # Verificar
        self.mock_interfaz.solicitar_id_obra.assert_not_called()
        self.mock_servicio_obras.obtener_detalles_obra.assert_not_called()
    
    def test_mostrar_imagen_obra_exitoso(self):
        """Test de mostrar imagen de obra exitoso"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, url_imagen="http://example.com/image.jpg")
        
        # Ejecutar
        self.controlador._mostrar_imagen_obra(obra)
        
        # Verificar
        self.mock_servicio_obras.mostrar_imagen_obra.assert_called_once_with(obra)
        self.mock_interfaz.mostrar_mensaje_exito.assert_called_with("Imagen mostrada correctamente")
    
    def test_mostrar_imagen_obra_error(self):
        """Test de error al mostrar imagen de obra"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista, url_imagen="http://example.com/image.jpg")
        
        # Configurar mock para lanzar excepción
        self.mock_servicio_obras.mostrar_imagen_obra.side_effect = \
            Exception("Error al mostrar imagen")
        
        # Ejecutar
        self.controlador._mostrar_imagen_obra(obra)
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Error al mostrar imagen: Error al mostrar imagen"
        )
    
    def test_mostrar_imagen_obra_error_validacion(self):
        """Test de error de validación al mostrar imagen de obra"""
        # Configurar datos de prueba
        artista = Artista("Test Artist", "American")
        obra = ObraArte(12345, "Test Artwork", artista)  # Sin imagen
        
        # Configurar mock para lanzar ValueError
        self.mock_servicio_obras.mostrar_imagen_obra.side_effect = \
            ValueError("La obra no tiene imagen disponible")
        
        # Ejecutar
        self.controlador._mostrar_imagen_obra(obra)
        
        # Verificar
        self.mock_interfaz.mostrar_mensaje_error.assert_called_with(
            "Error de validación: La obra no tiene imagen disponible"
        )
    
    def test_finalizar_aplicacion(self):
        """Test de finalización de aplicación"""
        # Configurar estado
        self.controlador._aplicacion_iniciada = True
        
        # Ejecutar
        with patch('builtins.print') as mock_print:
            self.controlador._finalizar_aplicacion()
        
        # Verificar
        self.mock_visualizador_imagenes.limpiar_cache.assert_called_once()
        mock_print.assert_called_with("\nAplicación finalizada.")


if __name__ == '__main__':
    unittest.main()
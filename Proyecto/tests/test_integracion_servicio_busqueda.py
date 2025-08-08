"""
Tests de integración para el servicio de búsqueda con el cliente API real.
"""

import pytest
from services.servicio_busqueda import ServicioBusqueda, ExcepcionesServicioBusqueda
from services.cliente_api_met_museum import ClienteAPIMetMuseum
from utils.gestor_nacionalidades import GestorNacionalidades
from models.obra_arte import ObraArte
from models.departamento import Departamento


@pytest.mark.slow
class TestIntegracionServicioBusqueda:
    """Tests de integración con la API real del Metropolitan Museum"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.cliente_api = ClienteAPIMetMuseum()
        self.gestor_nacionalidades = GestorNacionalidades("nacionalidades.txt")
        self.gestor_nacionalidades.cargar_nacionalidades()
        self.servicio = ServicioBusqueda(self.cliente_api, self.gestor_nacionalidades)
    
    def test_obtener_departamentos_disponibles_real(self):
        """Test de obtención de departamentos reales"""
        departamentos = self.servicio.obtener_departamentos_disponibles()
        
        # Verificar que se obtuvieron departamentos
        assert len(departamentos) > 0
        assert all(isinstance(dept, Departamento) for dept in departamentos)
        
        # Verificar que están ordenados por nombre
        nombres = [dept.nombre for dept in departamentos]
        assert nombres == sorted(nombres, key=str.lower)
        
        # Verificar que tienen IDs válidos
        assert all(dept.id_departamento > 0 for dept in departamentos)
    
    def test_buscar_por_departamento_real(self):
        """Test de búsqueda por departamento con API real"""
        # Usar departamento conocido (European Paintings = ID 11)
        try:
            obras = self.servicio.buscar_por_departamento(11)
            
            # Verificar que se obtuvieron obras
            assert len(obras) > 0
            assert all(isinstance(obra, ObraArte) for obra in obras)
            
            # Verificar que las obras tienen datos válidos
            for obra in obras:
                assert obra.id_obra > 0
                assert obra.titulo is not None
                assert obra.artista is not None
                assert obra.artista.nombre is not None
                
        except ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido:
            # El departamento podría no existir, esto es aceptable
            pytest.skip("Departamento no disponible en la API")
    
    def test_buscar_por_departamento_inexistente(self):
        """Test de búsqueda por departamento que no existe"""
        with pytest.raises(ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido):
            self.servicio.buscar_por_departamento(99999)
    
    def test_buscar_por_nacionalidad_real(self):
        """Test de búsqueda por nacionalidad con API real"""
        try:
            # Usar una nacionalidad común
            obras = self.servicio.buscar_por_nacionalidad("American")
            
            # Verificar resultados
            assert isinstance(obras, list)
            
            if obras:  # Si hay resultados
                assert all(isinstance(obra, ObraArte) for obra in obras)
                # Verificar que al menos algunas obras tienen artistas americanos
                artistas_americanos = [obra for obra in obras 
                                     if obra.artista.nacionalidad and 
                                     "american" in obra.artista.nacionalidad.lower()]
                assert len(artistas_americanos) > 0
                
                # Verificar que las obras tienen datos válidos
                for obra in obras:
                    assert obra.id_obra > 0
                    assert obra.titulo is not None
                    assert len(obra.titulo.strip()) > 0
                    assert obra.artista.nombre is not None
                    assert len(obra.artista.nombre.strip()) > 0
                
        except ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida:
            pytest.skip("Nacionalidad no disponible en el archivo")
    
    def test_buscar_por_nacionalidad_inexistente(self):
        """Test de búsqueda por nacionalidad que no existe en el archivo"""
        with pytest.raises(ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida):
            self.servicio.buscar_por_nacionalidad("NacionalidadInexistente")
    
    def test_buscar_por_nacionalidad_sin_resultados_real(self):
        """Test de búsqueda por nacionalidad válida pero sin obras en la API"""
        try:
            # Usar una nacionalidad que probablemente no tenga muchas obras
            obras = self.servicio.buscar_por_nacionalidad("Andorran")
            
            # Verificar que retorna lista vacía o con pocas obras
            assert isinstance(obras, list)
            # No hay garantía de que no haya obras, pero el método debe funcionar
            
        except ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida:
            pytest.skip("Nacionalidad no disponible en el archivo")
    
    def test_validacion_nacionalidades_disponibles(self):
        """Test que verifica la integración con el gestor de nacionalidades"""
        # Verificar que el gestor tiene nacionalidades cargadas
        nacionalidades = self.gestor_nacionalidades.obtener_nacionalidades_disponibles()
        assert len(nacionalidades) > 0
        
        # Probar con una nacionalidad que debería estar disponible
        nacionalidad_valida = nacionalidades[0] if nacionalidades else "American"
        
        try:
            # Esta búsqueda no debería lanzar ErrorNacionalidadInvalida
            obras = self.servicio.buscar_por_nacionalidad(nacionalidad_valida)
            assert isinstance(obras, list)
            
        except ExcepcionesServicioBusqueda.ErrorNacionalidadInvalida:
            pytest.fail(f"Nacionalidad '{nacionalidad_valida}' debería ser válida según el gestor")
    
    def test_buscar_por_nombre_artista_real(self):
        """Test de búsqueda por nombre de artista con API real"""
        # Usar un artista conocido
        obras = self.servicio.buscar_por_nombre_artista("Monet")
        
        # Verificar resultados
        assert isinstance(obras, list)
        
        if obras:  # Si hay resultados
            assert all(isinstance(obra, ObraArte) for obra in obras)
            # Verificar que al menos algunas obras son de Monet
            obras_monet = [obra for obra in obras 
                          if "monet" in obra.artista.nombre.lower()]
            assert len(obras_monet) > 0
    
    def test_conversion_datos_api_consistente(self):
        """Test que verifica la conversión consistente de datos de la API"""
        try:
            # Obtener algunas obras de un departamento
            obras = self.servicio.buscar_por_departamento(11)
            
            if obras:
                obra = obras[0]
                
                # Verificar que la conversión es consistente
                assert isinstance(obra.id_obra, int)
                assert isinstance(obra.titulo, str)
                assert len(obra.titulo.strip()) > 0
                
                # Verificar artista
                assert obra.artista.nombre is not None
                assert len(obra.artista.nombre.strip()) > 0
                
        except ExcepcionesServicioBusqueda.ErrorDepartamentoInvalido:
            pytest.skip("Departamento no disponible para test")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'slow'])
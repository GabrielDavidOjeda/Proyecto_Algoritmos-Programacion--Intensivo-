"""
Tests de integración para el cliente API del Metropolitan Museum of Art
Estos tests se ejecutan contra la API real y están marcados como 'slow'
"""

import pytest
from services.cliente_api_met_museum import ClienteAPIMetMuseum, ExcepcionesAPIMetMuseum
from models.departamento import Departamento


@pytest.mark.slow
class TestIntegracionAPIMetMuseum:
    """Tests de integración con la API real del Metropolitan Museum"""
    
    def setup_method(self):
        """Configuración para cada test"""
        self.cliente = ClienteAPIMetMuseum()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        if hasattr(self.cliente, 'session'):
            self.cliente.session.close()
    
    def test_obtener_departamentos_real(self):
        """Test de obtención real de departamentos"""
        try:
            departamentos = self.cliente.obtener_departamentos()
            
            # Verificar que se obtuvieron departamentos
            assert len(departamentos) > 0
            assert all(isinstance(dept, Departamento) for dept in departamentos)
            
            # Verificar que tienen los campos esperados
            primer_dept = departamentos[0]
            assert primer_dept.id_departamento > 0
            assert len(primer_dept.nombre) > 0
            
            print(f"✓ Se obtuvieron {len(departamentos)} departamentos")
            
        except ExcepcionesAPIMetMuseum.ErrorConexionAPI:
            pytest.skip("No se pudo conectar a la API del Metropolitan Museum")
    
    def test_obtener_detalles_obra_real(self):
        """Test de obtención real de detalles de obra"""
        # Usar un ID de obra conocido que debería existir
        id_obra_conocida = 436535  # "The Harvesters" de Pieter Bruegel
        
        try:
            detalles = self.cliente.obtener_detalles_obra(id_obra_conocida)
            
            # Verificar campos básicos
            assert detalles['objectID'] == id_obra_conocida
            assert 'title' in detalles
            assert detalles['title'] is not None
            
            print(f"✓ Obra obtenida: {detalles.get('title', 'Sin título')}")
            
        except ExcepcionesAPIMetMuseum.ErrorConexionAPI:
            pytest.skip("No se pudo conectar a la API del Metropolitan Museum")
        except ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado:
            pytest.skip(f"La obra {id_obra_conocida} ya no está disponible")
    
    def test_buscar_obras_por_query_real(self):
        """Test de búsqueda real por query"""
        query = "sunflowers"
        
        try:
            ids = self.cliente.buscar_obras_por_query(query)
            
            # Verificar que se obtuvieron resultados
            assert isinstance(ids, list)
            
            if len(ids) > 0:
                # Verificar que son IDs válidos
                assert all(isinstance(id_obra, int) and id_obra > 0 for id_obra in ids)
                print(f"✓ Búsqueda '{query}' encontró {len(ids)} obras")
            else:
                print(f"✓ Búsqueda '{query}' no encontró resultados (válido)")
                
        except ExcepcionesAPIMetMuseum.ErrorConexionAPI:
            pytest.skip("No se pudo conectar a la API del Metropolitan Museum")
    
    def test_obtener_obras_por_departamento_real(self):
        """Test de obtención real de obras por departamento"""
        # Usar el departamento de European Paintings (ID 11)
        id_departamento = 11
        
        try:
            ids = self.cliente.obtener_obras_por_departamento(id_departamento)
            
            # Verificar que se obtuvieron resultados
            assert isinstance(ids, list)
            
            if len(ids) > 0:
                # Verificar que son IDs válidos
                assert all(isinstance(id_obra, int) and id_obra > 0 for id_obra in ids)
                print(f"✓ Departamento {id_departamento} tiene {len(ids)} obras")
                
                # Tomar una muestra pequeña para verificar que se pueden obtener detalles
                muestra = ids[:3]  # Solo los primeros 3
                for id_obra in muestra:
                    try:
                        detalles = self.cliente.obtener_detalles_obra(id_obra)
                        assert detalles['objectID'] == id_obra
                    except ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado:
                        # Algunas obras pueden no estar disponibles, es normal
                        continue
                        
                print(f"✓ Se verificaron detalles de muestra de obras")
            else:
                print(f"✓ Departamento {id_departamento} no tiene obras (válido)")
                
        except ExcepcionesAPIMetMuseum.ErrorConexionAPI:
            pytest.skip("No se pudo conectar a la API del Metropolitan Museum")
        except ExcepcionesAPIMetMuseum.ErrorRecursoNoEncontrado:
            pytest.skip(f"El departamento {id_departamento} no existe")


if __name__ == "__main__":
    # Ejecutar solo los tests de integración
    pytest.main([__file__, "-v", "-m", "slow"])
"""
Tests unitarios para la clase Departamento.
"""

import unittest
from models.departamento import Departamento


class TestDepartamento(unittest.TestCase):
    """Tests para la clase Departamento."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.departamento = Departamento(
            id_departamento=1,
            nombre="American Decorative Arts"
        )
    
    def test_creacion_departamento_valido(self):
        """Test de creación de departamento con datos válidos."""
        dept = Departamento(id_departamento=5, nombre="European Paintings")
        
        self.assertEqual(dept.id_departamento, 5)
        self.assertEqual(dept.nombre, "European Paintings")
    
    def test_id_departamento_debe_ser_entero_positivo(self):
        """Test que el ID debe ser un entero positivo."""
        with self.assertRaises(ValueError):
            Departamento(id_departamento=0, nombre="Test")
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=-1, nombre="Test")
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento="1", nombre="Test")
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1.5, nombre="Test")
    
    def test_nombre_requerido(self):
        """Test que el nombre es requerido."""
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre="")
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre=None)
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre="   ")
    
    def test_nombre_debe_ser_string(self):
        """Test que el nombre debe ser una cadena."""
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre=123)
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre=[])
        
        with self.assertRaises(ValueError):
            Departamento(id_departamento=1, nombre={})
    
    def test_propiedades_getter(self):
        """Test de los getters de propiedades."""
        self.assertEqual(self.departamento.id_departamento, 1)
        self.assertEqual(self.departamento.nombre, "American Decorative Arts")
    
    def test_propiedad_setter_nombre(self):
        """Test del setter de nombre."""
        self.departamento.nombre = "New Department Name"
        self.assertEqual(self.departamento.nombre, "New Department Name")
    
    def test_setter_nombre_invalido(self):
        """Test que el setter de nombre valida correctamente."""
        with self.assertRaises(ValueError):
            self.departamento.nombre = ""
        
        with self.assertRaises(ValueError):
            self.departamento.nombre = None
        
        with self.assertRaises(ValueError):
            self.departamento.nombre = "   "
        
        with self.assertRaises(ValueError):
            self.departamento.nombre = 123
    
    def test_validar_datos_departamento_valido(self):
        """Test de validación con datos válidos."""
        self.assertTrue(self.departamento.validar_datos())
    
    def test_validar_datos_departamento_invalido(self):
        """Test de validación con datos inválidos."""
        # Crear departamento y modificar internamente para simular datos inválidos
        dept = Departamento(id_departamento=1, nombre="Test")
        
        # Modificar directamente el atributo privado para test
        dept._id_departamento = 0
        self.assertFalse(dept.validar_datos())
        
        # Restaurar y probar con nombre inválido
        dept._id_departamento = 1
        dept._nombre = ""
        self.assertFalse(dept.validar_datos())
    
    def test_obtener_info_completa(self):
        """Test del método obtener_info_completa."""
        info = self.departamento.obtener_info_completa()
        
        self.assertEqual(info['id'], 1)
        self.assertEqual(info['nombre'], "American Decorative Arts")
        self.assertTrue(info['valido'])
    
    def test_str_representation(self):
        """Test de la representación en cadena."""
        str_repr = str(self.departamento)
        expected = "American Decorative Arts (ID: 1)"
        self.assertEqual(str_repr, expected)
    
    def test_repr_representation(self):
        """Test de la representación técnica."""
        repr_str = repr(self.departamento)
        expected = "Departamento(id_departamento=1, nombre='American Decorative Arts')"
        self.assertEqual(repr_str, expected)
    
    def test_equality(self):
        """Test de comparación de igualdad."""
        dept1 = Departamento(id_departamento=1, nombre="Test1")
        dept2 = Departamento(id_departamento=1, nombre="Test2")  # Mismo ID
        dept3 = Departamento(id_departamento=2, nombre="Test1")  # Diferente ID
        
        self.assertEqual(dept1, dept2)  # Mismo ID
        self.assertNotEqual(dept1, dept3)  # Diferente ID
        self.assertNotEqual(dept1, "not a department")
    
    def test_hash(self):
        """Test de la función hash."""
        dept1 = Departamento(id_departamento=1, nombre="Test1")
        dept2 = Departamento(id_departamento=1, nombre="Test2")  # Mismo ID
        dept3 = Departamento(id_departamento=2, nombre="Test1")  # Diferente ID
        
        self.assertEqual(hash(dept1), hash(dept2))  # Mismo ID, mismo hash
        self.assertNotEqual(hash(dept1), hash(dept3))  # Diferente ID, diferente hash
    
    def test_ordenamiento(self):
        """Test de ordenamiento de departamentos."""
        dept1 = Departamento(id_departamento=1, nombre="Zebra Department")
        dept2 = Departamento(id_departamento=2, nombre="Alpha Department")
        dept3 = Departamento(id_departamento=3, nombre="Beta Department")
        
        departamentos = [dept1, dept2, dept3]
        departamentos_ordenados = sorted(departamentos)
        
        # Debe ordenarse alfabéticamente por nombre
        self.assertEqual(departamentos_ordenados[0].nombre, "Alpha Department")
        self.assertEqual(departamentos_ordenados[1].nombre, "Beta Department")
        self.assertEqual(departamentos_ordenados[2].nombre, "Zebra Department")
    
    def test_ordenamiento_case_insensitive(self):
        """Test que el ordenamiento es insensible a mayúsculas."""
        dept1 = Departamento(id_departamento=1, nombre="zebra department")
        dept2 = Departamento(id_departamento=2, nombre="Alpha Department")
        
        departamentos = [dept1, dept2]
        departamentos_ordenados = sorted(departamentos)
        
        self.assertEqual(departamentos_ordenados[0].nombre, "Alpha Department")
        self.assertEqual(departamentos_ordenados[1].nombre, "zebra department")
    
    def test_espacios_en_blanco_eliminados(self):
        """Test que los espacios en blanco se eliminan correctamente."""
        dept = Departamento(id_departamento=1, nombre="  Test Department  ")
        self.assertEqual(dept.nombre, "Test Department")
    
    def test_setter_elimina_espacios(self):
        """Test que el setter elimina espacios en blanco."""
        self.departamento.nombre = "  New Name  "
        self.assertEqual(self.departamento.nombre, "New Name")
    
    def test_validar_datos_maneja_excepciones(self):
        """Test que validar_datos maneja excepciones correctamente."""
        dept = Departamento(id_departamento=1, nombre="Test")
        
        # Simular una situación que podría causar excepción
        original_id = dept._id_departamento
        dept._id_departamento = None  # Esto podría causar problemas en isinstance
        
        # El método debe retornar False en lugar de lanzar excepción
        self.assertFalse(dept.validar_datos())
        
        # Restaurar para limpieza
        dept._id_departamento = original_id


if __name__ == '__main__':
    unittest.main()
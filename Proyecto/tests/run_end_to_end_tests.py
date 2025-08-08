#!/usr/bin/env python3
"""
Script especializado para ejecutar tests end-to-end del sistema de catálogo del museo.

Este script ejecuta tests de integración completos que validan flujos end-to-end
del sistema, incluyendo manejo de errores y casos edge.
"""

import unittest
import sys
import os
import time
from typing import List, Dict, Any

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EndToEndTestResult(unittest.TextTestResult):
    """
    Resultado personalizado para tests end-to-end con métricas adicionales.
    """
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_times = {}
        self.start_time = None
        self.end_time = None
        self.total_start_time = time.time()
    
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
    
    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time:
            self.test_times[str(test)] = time.time() - self.start_time
    
    def stopTestRun(self):
        super().stopTestRun()
        self.end_time = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen detallado de la ejecución de tests."""
        total_time = self.end_time - self.total_start_time if self.end_time else 0
        
        return {
            'total_tests': self.testsRun,
            'successful': self.testsRun - len(self.failures) - len(self.errors),
            'failures': len(self.failures),
            'errors': len(self.errors),
            'skipped': len(self.skipped) if hasattr(self, 'skipped') else 0,
            'total_time': total_time,
            'average_time': total_time / self.testsRun if self.testsRun > 0 else 0,
            'slowest_tests': sorted(self.test_times.items(), key=lambda x: x[1], reverse=True)[:5]
        }


class EndToEndTestRunner:
    """
    Runner especializado para tests end-to-end con configuración y reportes avanzados.
    """
    
    def __init__(self, verbosity: int = 2):
        self.verbosity = verbosity
        self.test_categories = {
            'busqueda_departamento': 'TestEndToEndBusquedaDepartamento',
            'busqueda_nacionalidad': 'TestEndToEndBusquedaNacionalidad', 
            'busqueda_artista': 'TestEndToEndBusquedaArtista',
            'visualizacion_detalles': 'TestEndToEndVisualizacionDetalles',
            'manejo_errores_api': 'TestEndToEndManejoErroresAPI',
            'suite_regresion': 'TestEndToEndSuiteRegresion'
        }
    
    def run_all_tests(self) -> bool:
        """
        Ejecuta todos los tests end-to-end.
        
        Returns:
            bool: True si todos los tests pasaron, False en caso contrario
        """
        print("="*80)
        print("    EJECUTANDO TESTS END-TO-END DEL SISTEMA DE CATÁLOGO")
        print("="*80)
        print()
        
        # Descubrir tests end-to-end
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('test_end_to_end')
        
        # Ejecutar tests con resultado personalizado
        stream = sys.stdout
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=self.verbosity,
            resultclass=EndToEndTestResult
        )
        
        print(f"Ejecutando {suite.countTestCases()} tests end-to-end...")
        print("-" * 80)
        
        result = runner.run(suite)
        
        # Mostrar resumen detallado
        self._show_detailed_summary(result)
        
        return result.wasSuccessful()
    
    def run_category_tests(self, category: str) -> bool:
        """
        Ejecuta tests de una categoría específica.
        
        Args:
            category: Categoría de tests a ejecutar
            
        Returns:
            bool: True si todos los tests de la categoría pasaron
        """
        if category not in self.test_categories:
            print(f"Error: Categoría '{category}' no encontrada.")
            print(f"Categorías disponibles: {', '.join(self.test_categories.keys())}")
            return False
        
        class_name = self.test_categories[category]
        
        print(f"Ejecutando tests de categoría: {category}")
        print(f"Clase de test: {class_name}")
        print("-" * 60)
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'test_end_to_end.{class_name}')
        
        runner = unittest.TextTestRunner(
            verbosity=self.verbosity,
            resultclass=EndToEndTestResult
        )
        
        result = runner.run(suite)
        self._show_detailed_summary(result)
        
        return result.wasSuccessful()
    
    def run_regression_suite(self) -> bool:
        """
        Ejecuta solo la suite de tests de regresión.
        
        Returns:
            bool: True si todos los tests de regresión pasaron
        """
        return self.run_category_tests('suite_regresion')
    
    def _show_detailed_summary(self, result: EndToEndTestResult) -> None:
        """
        Muestra un resumen detallado de los resultados.
        
        Args:
            result: Resultado de la ejecución de tests
        """
        summary = result.get_summary()
        
        print("\n" + "="*80)
        print("    RESUMEN DETALLADO DE TESTS END-TO-END")
        print("="*80)
        
        # Estadísticas generales
        print(f"Tests ejecutados: {summary['total_tests']}")
        print(f"Exitosos: {summary['successful']}")
        print(f"Fallidos: {summary['failures']}")
        print(f"Errores: {summary['errors']}")
        print(f"Omitidos: {summary['skipped']}")
        print(f"Tiempo total: {summary['total_time']:.2f} segundos")
        print(f"Tiempo promedio por test: {summary['average_time']:.2f} segundos")
        
        # Tests más lentos
        if summary['slowest_tests']:
            print("\nTests más lentos:")
            for test_name, test_time in summary['slowest_tests']:
                print(f"  • {test_name}: {test_time:.2f}s")
        
        # Detalles de fallos
        if result.failures:
            print(f"\nDETALLES DE FALLOS ({len(result.failures)}):")
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"\n{i}. {test}")
                print("-" * 60)
                print(traceback)
        
        # Detalles de errores
        if result.errors:
            print(f"\nDETALLES DE ERRORES ({len(result.errors)}):")
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"\n{i}. {test}")
                print("-" * 60)
                print(traceback)
        
        # Estado final
        print("\n" + "="*80)
        if result.wasSuccessful():
            print("    ✓ TODOS LOS TESTS END-TO-END PASARON EXITOSAMENTE")
        else:
            print("    ✗ ALGUNOS TESTS END-TO-END FALLARON")
        print("="*80)


def main():
    """Función principal del script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ejecutar tests end-to-end del sistema de catálogo del museo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_end_to_end_tests.py                    # Ejecutar todos los tests
  python run_end_to_end_tests.py --category regresion  # Solo tests de regresión
  python run_end_to_end_tests.py --category busqueda_departamento  # Solo búsqueda por departamento
  python run_end_to_end_tests.py --quiet            # Ejecución silenciosa
        """
    )
    
    parser.add_argument(
        '--category',
        choices=['busqueda_departamento', 'busqueda_nacionalidad', 'busqueda_artista',
                'visualizacion_detalles', 'manejo_errores_api', 'suite_regresion'],
        help='Ejecutar solo tests de una categoría específica'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Ejecución silenciosa (verbosity = 1)'
    )
    
    parser.add_argument(
        '--regression-only',
        action='store_true',
        help='Ejecutar solo la suite de tests de regresión'
    )
    
    args = parser.parse_args()
    
    # Configurar verbosity
    verbosity = 1 if args.quiet else 2
    
    # Crear runner
    runner = EndToEndTestRunner(verbosity=verbosity)
    
    # Ejecutar tests según argumentos
    try:
        if args.regression_only:
            success = runner.run_regression_suite()
        elif args.category:
            success = runner.run_category_tests(args.category)
        else:
            success = runner.run_all_tests()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\nEjecución interrumpida por el usuario.")
        return 1
    except Exception as e:
        print(f"\nError inesperado durante la ejecución: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
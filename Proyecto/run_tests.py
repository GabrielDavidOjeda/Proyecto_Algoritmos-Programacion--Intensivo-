#!/usr/bin/env python3
"""
Script para ejecutar todos los tests del proyecto.

Incluye tests unitarios, de integración y end-to-end.
"""

import unittest
import sys
import os
import argparse
import time

def run_tests(include_e2e=False, verbosity=2, pattern='test_*.py'):
    """
    Ejecuta todos los tests del proyecto.
    
    Args:
        include_e2e (bool): Si incluir tests end-to-end
        verbosity (int): Nivel de verbosidad (1-2)
        pattern (str): Patrón de archivos de test a incluir
    """
    # Agregar el directorio actual al path para importar módulos
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("="*70)
    print("    EJECUTANDO SUITE COMPLETA DE TESTS")
    print("="*70)
    
    # Descubrir y ejecutar tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    
    if include_e2e:
        print("Incluyendo tests end-to-end...")
        suite = loader.discover(start_dir, pattern=pattern)
    else:
        print("Excluyendo tests end-to-end (usar --include-e2e para incluirlos)...")
        # Cargar todos los tests excepto end-to-end
        all_tests = loader.discover(start_dir, pattern=pattern)
        suite = unittest.TestSuite()
        
        for test_group in all_tests:
            for test_case in test_group:
                # Excluir tests end-to-end
                if hasattr(test_case, '_testMethodName'):
                    if 'end_to_end' not in str(test_case.__class__.__module__):
                        suite.addTest(test_case)
                else:
                    # Es un TestSuite, revisar recursivamente
                    for individual_test in test_case:
                        if 'end_to_end' not in str(individual_test.__class__.__module__):
                            suite.addTest(individual_test)
    
    print(f"Ejecutando {suite.countTestCases()} tests...")
    print("-" * 70)
    
    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    end_time = time.time()
    
    # Mostrar resumen
    print("\n" + "="*70)
    print("    RESUMEN DE EJECUCIÓN")
    print("="*70)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallidos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Tiempo total: {end_time - start_time:.2f} segundos")
    
    if result.wasSuccessful():
        print("✓ TODOS LOS TESTS PASARON EXITOSAMENTE")
    else:
        print("✗ ALGUNOS TESTS FALLARON")
    
    print("="*70)
    
    # Retornar código de salida apropiado
    return 0 if result.wasSuccessful() else 1

def run_unit_tests_only():
    """Ejecuta solo tests unitarios (excluyendo integración y e2e)."""
    print("Ejecutando solo tests unitarios...")
    return run_tests(include_e2e=False, pattern='test_[!i]*.py')

def run_integration_tests_only():
    """Ejecuta solo tests de integración."""
    print("Ejecutando solo tests de integración...")
    return run_tests(include_e2e=False, pattern='test_integracion_*.py')

def run_e2e_tests_only():
    """Ejecuta solo tests end-to-end."""
    print("Ejecutando solo tests end-to-end...")
    # Importar y usar el runner especializado
    try:
        from tests.run_end_to_end_tests import EndToEndTestRunner
        runner = EndToEndTestRunner(verbosity=2)
        success = runner.run_all_tests()
        return 0 if success else 1
    except ImportError:
        print("Error: No se pudo importar el runner de tests end-to-end")
        return 1

def main():
    """Función principal con argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Ejecutar tests del sistema de catálogo del museo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py                    # Tests unitarios e integración
  python run_tests.py --include-e2e      # Todos los tests incluyendo e2e
  python run_tests.py --unit-only        # Solo tests unitarios
  python run_tests.py --integration-only # Solo tests de integración
  python run_tests.py --e2e-only         # Solo tests end-to-end
  python run_tests.py --quiet            # Ejecución silenciosa
        """
    )
    
    parser.add_argument(
        '--include-e2e',
        action='store_true',
        help='Incluir tests end-to-end (pueden ser lentos)'
    )
    
    parser.add_argument(
        '--unit-only',
        action='store_true',
        help='Ejecutar solo tests unitarios'
    )
    
    parser.add_argument(
        '--integration-only',
        action='store_true',
        help='Ejecutar solo tests de integración'
    )
    
    parser.add_argument(
        '--e2e-only',
        action='store_true',
        help='Ejecutar solo tests end-to-end'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Ejecución silenciosa (verbosity = 1)'
    )
    
    args = parser.parse_args()
    
    # Configurar verbosity
    verbosity = 1 if args.quiet else 2
    
    try:
        # Ejecutar según argumentos
        if args.unit_only:
            return run_unit_tests_only()
        elif args.integration_only:
            return run_integration_tests_only()
        elif args.e2e_only:
            return run_e2e_tests_only()
        else:
            return run_tests(include_e2e=args.include_e2e, verbosity=verbosity)
            
    except KeyboardInterrupt:
        print("\n\nEjecución interrumpida por el usuario.")
        return 1
    except Exception as e:
        print(f"\nError inesperado durante la ejecución: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
# Guía de Uso Rápido

## Inicio Rápido

### 1. Verificar Sistema
```bash
python main.py --check-resources
```

### 2. Ejecutar Aplicación
```bash
python main.py
```

## Opciones del Menú Principal

1. **Buscar por departamento**
   - Selecciona un departamento de la lista
   - Ve las obras disponibles en ese departamento

2. **Buscar por nacionalidad del artista**
   - Selecciona una nacionalidad de la lista
   - Explora obras de artistas de esa nacionalidad

3. **Buscar por nombre del artista**
   - Ingresa el nombre del artista (puede ser parcial)
   - Ve las obras encontradas

4. **Ver detalles de una obra específica**
   - Ingresa el ID de la obra
   - Ve información completa e imagen (si está disponible)

5. **Salir**

## Ejemplos de Uso

### Búsqueda por Departamento
1. Ejecuta `python main.py`
2. Selecciona opción `1`
3. Elige un departamento (ej: "European Paintings")
4. Ve la lista de obras
5. Opcionalmente, ingresa un ID para ver detalles

### Búsqueda por Nacionalidad
1. Ejecuta `python main.py`
2. Selecciona opción `2`
3. Elige una nacionalidad (ej: "French")
4. Ve obras de artistas franceses

### Búsqueda por Artista
1. Ejecuta `python main.py`
2. Selecciona opción `3`
3. Ingresa nombre (ej: "Van Gogh" o "Vincent")
4. Ve obras encontradas

## Comandos Útiles

```bash
# Ver ayuda completa
python main.py --help

# Verificar recursos
python main.py --check-resources

# Usar archivo de nacionalidades personalizado
python main.py --nacionalidades mi_archivo.txt

# Modo debug (para desarrollo)
python main.py --debug
```

## Solución de Problemas

### Si no funciona la conexión:
- Verifica tu conexión a internet
- Ejecuta: `python main.py --check-resources`

### Si faltan dependencias:
- Ejecuta: `pip install -r requirements.txt`

### Si no encuentra nacionalidades.txt:
- Verifica que el archivo existe en el directorio
- O usa: `python main.py --nacionalidades ruta/al/archivo.txt`
# Set Covering Problem resuelto con Ant Colony Optimization

## Descripción

Este repositorio contiene un programa en Python diseñado para resolver el **Set Covering Problem (SCP)** utilizando la metaheurística **Ant Colony Optimization (ACO)**. El Set Covering Problem es un problema de optimización combinatoria que busca seleccionar el menor número de conjuntos de un universo de elementos, de modo que todos los elementos estén cubiertos al menos una vez al menor costo.

La metaheurística Ant Colony Optimization se basa en el comportamiento de búsqueda de alimento de las hormigas para encontrar soluciones óptimas en problemas de optimización complejos.

## Uso

Crear un entorno virtual

```bash
python -m venv .venv
```

Instalar las dependencias del archivo requeriments.txt.

```bash
pip install -r .\requirements.txt
```

En el archivo **.env** se debe tener una variable llamada PYTHON_ENV con el path del entorno virtual o del comando con el que ejecutamos python.

Ejecutar el archivo main.py

```bash
python main.py
```

Al ejecutar veremos la GUI, cargamos los valores para los parámetros de ACO, seleccionar el archivo de instancia, un directorio donde guardar las posibles soluciones generadas y apretamos el botón ejecutar.

Iremos viendo en la consola información sobre la ejecución.
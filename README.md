# mallador_v3
Interfaz para visualizar mallas U-Campus (fcfm por el momento)

Estado actual:
- La interfaz deja descargar y guardar catálogos (mediante fetcher.py).
- Todavía **no** se soluciona la incorporación de los ramos en la ventana principal.

En resumen, **de momento (2016-12-23) sólo sirve para descargar y guardar los catálogos en un formato interno de texto plano**.

Utiliza Python 2.x.
Las siguientes dependencias no forman parte de la librería estándar de Python:
- bs4 *(BeautifulSoup)*
- unidecode

Para instalarlas, se recomienda usar pip:
```
pip install [librería]
```

Si no está instalado, referirse a la página de [pip](https://pip.pypa.io/en/stable/installing/)


## Para colaboradores:

Para poder probar el panel inferior:
- Primero, importar el catálogo de prueba (Otoño 2016):
	Archivo > Gestionar catalogos > Importar catalogo desde archivo > "catalogo20161.fcfm"
- Luego, abrir la ventana de carga de cursos:
	Ventanas > Mostrar cursos disponibles
- Ahí, seleccionar algún ramo y "Agregar al horario". El resultado debería ser similar al de la maqueta del programa (maqueta.png)

Funciones problemáticas:

1 En malladorv_v3.py:
  - actualizar_ramos_inferior
  - poblar_widgets_ramo
  - Las funciones dibujar_bloques y relacionadas aún no ha sido probada
  
2  En fetcher.py:
	- cargarCatalogo
  
3  En structHorario.py:
	- clases Curso y Seccion

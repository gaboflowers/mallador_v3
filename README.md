# mallador_v3
Interfaz para visualizar horarios U-Campus (fcfm por el momento)

Estado actual:
- La interfaz deja descargar y guardar catálogos (mediante fetcher.py).
- Se pueden incorporar ramos a la ventana principal.
- Hay muchos problemas ocasionados la quitar los ramos de la ventana principal.
- No funciona el scrollbar la lista de sección de cada ramo

En resumen, **de momento (2017-01-03) sólo sirve para descargar y guardar los catálogos en texto plano, y visualizarlos una vez seleccionados (no se pueden quitar una vez seleccionados)**.

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
- Ahí, seleccionar algún ramo y "Agregar al horario". El resultado debería ser similar al de la maqueta del programa

![maqueta.png](https://raw.githubusercontent.com/gaboflowers/mallador_v3/master/maqueta.png)

- Update: Se ha logrado prácticamente un resultado similar a la maqueta (falta solucionar lo de los Scrollbar verticales)
![captura](https://raw.githubusercontent.com/gaboflowers/mallador_v3/master/captura_main.png)

Funciones problemáticas:

1  En malladorv_v3.py:
  - actualizar_ramos_inferior (<- será necesario separar su función?)
  - nuevo_ramo_inferior
  - poblar_widgets_ultimo_ramo (<- será necesario separar su función?)
  - quitar_ramo (MUCHO)
  

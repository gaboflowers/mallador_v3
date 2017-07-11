# mallador_v3
Interfaz para visualizar horarios U-Campus (fcfm por el momento)

Estado actual:
- La interfaz deja descargar y guardar catálogos (mediante fetcher.py).
- Se pueden incorporar ramos a la ventana principal.
- No funciona el scrollbar la lista de sección de cada ramo

En resumen, **de momento (2017-01-05) ya sirve para visualizar los ramos, a excepción de los que tengan más de 8 secciones, en cuyo caso aún no se puede hacer scroll para revisar toda la lista**.

Utiliza Python 2.x.

El archivo [mallador_v3_pack.zip](https://github.com/gaboflowers/mallador_v3/raw/master/mallador_v3_pack.zip) contiene, en la mayoría de los casos, lo necesario para ejecutar el programa.

## Dependencias  

Las siguientes dependencias no forman parte de la librería estándar de Python:
- bs4 *(BeautifulSoup)*
- unidecode

Para instalarlas, se recomienda usar pip:
```
pip install [librería]
```
(se ejecuta en el Símbolo del sistema, o en la Terminal de UNIX/Linux. Ejemplo: "pip install bs4")

Si no está instalado, referirse a la página de [pip](https://pip.pypa.io/en/stable/installing/)

En caso de utilizar las versiones provistas en el ZIP (no se recomienda), se debe copiar las carpetas *bs4* y *unidecode* en la carpeta *site-packages* de la instalación local de Python. Generalmente, esta carpeta está en C:\Python27\Lib\site-packages en Windows.

## Utilización

Una vez satisfechas las dependencias, los archivos principales son sólo *mallador_v3.pyw*, *fetcher.py* y *structHorario.py*.
La información de los cursos está guardada en "catálogos", los cuales se pueden descargar de U-Campus, o utilizar uno ya obtenido en disco.

El programa principal es *mallador_v3.pyw*. Generalmente, basta con hacer doble clic para ejecutarlo, pero en caso contrario, se puede abrir con IDLE y ejecutar como siempre (o directamente desde Python en la línea de comandos). Desde Linux, abriendo una ventana de terminal (gráfica), generalmente basta con escribir "python"+[espacio], luego arrastrar el ícono de *mallador_v3.pyw*
hacia la terminal, para que se ingrese la ruta completa del archivo, y luego Enter.

- Para obtener el catálogo de algún semestre (posterior a Otoño 2013, inclusive):
	- Abrir *mallador_v3.pyw*
	- Clic en "Archivo", luego en "Gestionar catalogos"
	- Ingresar año y semestre en la parte inferior. Por defecto, lee la fecha del sistema y "asume" el semestre, pero debido a varias razones político-administrativas, usted puede modificarlo. Clic en Descargar.
	- Una vez hecho clic, el programa puede demorar varios segundos (o minutos, dependiendo de la conexión) en cargar. Es normal que mientras esté cargando, al hacer clic en la ventana el sistema muestre que esté pegado. Basta con esperar (a menos que pase mucho tiempo, eso queda al sentido común del usuario). Si aun así falla, seguir con la sección siguiente.
	- El programa mostrará en el Gestor de catálogos el item "DESCARGADO"+[código semestre]. Si lo desea, puede hacer clic en "Guardar catálogo" para no tener que descargarlo nuevamente. En este momento, ya puede cerrar la ventana del Gestor. Para seguir con la visualización de ramos, sáltese la sección siguiente.

- Para cargar un catálogo:
	- Archivo > Gestionar catalogos > Cargar catalogo
	- Seleccione el archivo de catálogo (generalmente, "catalogo"+[semestre]+".fcfm")
	- Aceptar. La ventana mostrará el nombre del archivo cargado. Ya se puede cerrar la ventana del Gestor.
	- El Zip viene con el catálogo de Otoño 2017 (y el repositorio incluye Otoño 2016). La idea es descargar nuevamente el catálogo entre Inscripción y Modificas, ya que en la ventana principal de ramos cargados se ve el cupo y la cantidad de ocupados, número que varía en cada Modifica.
	
- Para cargar un curso (sólo una vez cargado un catálogo):
	- Ventanas > Mostrar cursos disponibles. Se abrirá el catálogo de cursos, con un menú selector de departamentos en la parte superior.
	- Escoja un departamento, y haga clic en "Agregar al Horario". Puede escoger ramos de varios departamentos a la vez.
	- A medida que agrega ramos al horario, van apareciendo menúes en la ventana principal.
	- **He visto que muchas veces un ramo seleccionado de la lista de cursos disponibles simplemente no se agrega. Esto parece tincada de Python, puesto que al cerrar y abrir el programa de nuevo, no he logrado recrear el bug. Por lo visto, basta con abrir de nuevo.**

- Para visualizar una combinación de (secciones de) ramos:
	- Por defecto, los ramos cargados están ocultos. Al marcar la casilla "Mostrar", aparecerán los bloques dibujados en el horario. Puede escoger cualquier sección en cualquier momento, y los bloques de dicho ramo se redibujarán.
	- Si no quiere que algún ramo siga apareciendo, puede desmarcar la casilla "Mostrar", o hacer clic en "Quitar" para removerlo de la lista de menúes. Si quiere agregarlo nuevamente, puede volver a hacerlo en "Mostrar cursos disponibles".Debi
	- **Debido a un bug, no se pueden deslizar las listas de secciones de cada ramo. Si agregó un ramo cuyo botón de menú quedó dibujado fuera de la ventana, para removerlo tendrá sólo que ocultarlo, o volver a iniciar el programa.**
	- ~~Una vez borrado un ramo,lo más probable es que el resto de los ramos cargados queden en un orden distinto al que tenían originalmente. Esto se debe a la implementación mediante Diccionario, la cual no garantiza ningún orden. Debido a que no es crucial, no planeo cambiar esto prontamente.~~ Arreglado 11-07-2017.
	
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

1  En malladorv_v3.pyw:
  - actualizar_ramos_inferior
  - nuevo_ramo_inferior
  - poblar_widgets_ultimo_ramo
  - quitar_ramo (MUCHO)
  Debería separar sus funciones, pero de momento funcionan...
  
2  En fetcher.py
  - guardarCatalogo
  - cargarCatalogo
  

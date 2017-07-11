# -*- coding: cp1252 -*-
from fetcher import *
from ttk import *
from Tkinter import *
import tkMessageBox
from tkFileDialog import askopenfilename
from datetime import date
from os import getcwd
from os import name as os_name
from os import remove as os_remove
from random import randint
from random import choice

#from time import sleep # <------ debugging

###BUGS:- (ARREGLADO) No se puede exportar un catalogo importado: si lo arreglo para la exportacion,
###         no se puede importar y viceversa. Algun dia tendre que arreglar "fetcher"
###         para que trabaje de forma mas limpia con Unicode
###
###     - (ARREGLADO) VentanaMallador permite multiples ventanas Toplevel de cada instancia abiertas <- arreglado con self.ventanas_cerradas
###     - No funcionan los Scrollbars verticales (de cada ramo). Lo siento, Taller de Proyecto :c

class VentanaMallador(Frame):
	counter = 0
	def __init__(self,*args,**kwargs):
		self.frame_1 = Frame.__init__(self, *args, **kwargs)
		self.root = args[0]

		#self.root.bind( "<Configure>", self.onresize )

		self.ventanas_cerradas = [True,True,True] #[ventana importar catalogos, ventana db, ventana agregar]
		self.ventanas = {'carga':None, 'db':None, 'agregar':None}
		
		self.menubar = Menu(self.root)

		#agregar menues deplegables
		self.filemenu = Menu(self.menubar, tearoff=0) #Archivo
		self.filemenu.add_command(label="Gestionar catalogos", command=self.manage_db)
		self.menubar.add_cascade(label="Archivo", menu=self.filemenu)

		self.winmenu = Menu(self.menubar, tearoff=0) #Ventana
		self.winmenu.add_command(label="Mostrar Cursos Disponibles",\
		                         command=self.ventana_ramos_db)
		self.winmenu.add_command(label="Nada todavia")#"Mostrar Cursos Seleccionados",\
		                         #command=self.ventana_ramos_db)
		self.menubar.add_cascade(label="Ventanas", menu=self.winmenu)

		#mostrar barra menu
		self.root.config(menu = self.menubar)

		self.catalogos = [] #[["nombre", catalogo], ["nombre", catalogo], ...]
		

		#info para descargar
		self.year_entry = None
		self.sem_entry = None

		#lista catalogos
		self.lista_catalogos = None

		
		#self.cargados = [] # OBSOLETO (usar self.dict_cargados) lista de cursos cargados
		
		self.d_cargados = dict()
		self.ultimo_ramo_cargado = ""
		
		#self.dicc_cajas_ramo = [] #<-- para guardar las cajas de los objetos dentro del canvas que se mueve
		#self.dicc_widgets_ramo = [] #<-- para guardar las variables de los widgets
		self.d_cajas_ramo = dict()
		self.d_widgets_ramo = dict()
		#self.bloques_ramo = [] # [ [ramo1 = cod, bloques s1, bloques s2, ...], [ ramo2 = cod, bloques s1, bloques s2, ...],. ...]
		#self.geometrias_ramo = [] # <-- geometrias_ramo[i] tiene los rectangulos y textos del ramo i
		self.d_bloques_ramo = dict()
		self.d_geometrias_ramo = dict()

		self.n_bloques = 0

		#Widgets de esta ventana
		self.canvas = Canvas(self.frame_1,width=660, height=300, bg="white")
		self.canvas.pack()
		self.tabla_horario()
		self.widgets_main()
		self.status_main()
		
	"""
	def onresize(self,event):
		print self.root.winfo_reqwidth()
	"""

	#---------------- Widgets ventana principal ----------------
	def tabla_horario(self):
		
		self.canvas.delete("all")
		h,w=304,600
		
		for i in range(w/5,w+10,w/5):
		    self.canvas.create_line(i,0,i,h)
		dias = ["Lunes","Martes","Miercoles","Jueves","Viernes"]
		for i in range(5):
		    self.canvas.create_text(w/10+i*w/5,10,text=dias[i])
		self.canvas.create_line(0,20,664,20)

		self.minutos_a_coord = lambda x: x*28/75+20

		self.canvas.create_line(0,self.minutos_a_coord(90),664,self.minutos_a_coord(90), fill="blue") #8:30 + 90mins (10:00)
		self.canvas.create_line(0,self.minutos_a_coord(210),664,self.minutos_a_coord(210),fill="blue") #12:00
		self.canvas.create_line(0,self.minutos_a_coord(300),664,self.minutos_a_coord(300), fill="red") #13:30 (almuerzo)
		self.canvas.create_line(0,self.minutos_a_coord(360),664,self.minutos_a_coord(360), fill="red") #14:30
		self.canvas.create_line(0,self.minutos_a_coord(450),664,self.minutos_a_coord(450), fill="blue") #16:00
		self.canvas.create_line(0,self.minutos_a_coord(570),664,self.minutos_a_coord(570), fill="blue") #18:00
		self.canvas.create_line(0,self.minutos_a_coord(690),664,self.minutos_a_coord(690), fill="blue") #20:00

		self.canvas.create_text(615,13,text="8:30")
		self.canvas.create_text(615,self.minutos_a_coord(70),text="10:00")
		self.canvas.create_text(615,self.minutos_a_coord(190),text="12:00")
		self.canvas.create_text(615,self.minutos_a_coord(280),text="13:30")
		self.canvas.create_text(615,self.minutos_a_coord(343),text="14:30")
		self.canvas.create_text(615,self.minutos_a_coord(430),text="16:00")
		self.canvas.create_text(615,self.minutos_a_coord(550),text="18:00")
		self.canvas.create_text(615,self.minutos_a_coord(670),text="20:00")           

		    
	def widgets_main(self): # <--------------- POBLA EL CANVAS DE LOS CANVASES SCROLLEABLES DE LOS RAMOS
		frame_2 = Frame(self.frame_1,height=300)
		frame_2.pack(fill=X)
		frame_2.pack_propagate(0)

		self.canvas_scroll = Canvas(frame_2, borderwidth=0)#,width=660, height=250) # <- CANVAS SCROLLEABLE EN X
		self.canvas_scroll.configure(background="navy") # <- DELENDA EST
		self.frame_canvas = Frame(self.canvas_scroll) # <- FRAME DENTRO DEL CANVAS
		scrollbar = Scrollbar(frame_2,orient=HORIZONTAL,command=self.canvas_scroll.xview)
		self.canvas_scroll.configure(xscrollcommand=scrollbar.set)
		
		scrollbar.pack(side=BOTTOM,fill=X)
		self.canvas_scroll.pack(fill=BOTH,expand=True)
		self.canvas_scroll.create_window((4,4), window=self.frame_canvas, anchor="nw")

		comando_aux = lambda event: self.onFrameConfigureSub(self.canvas_scroll)

		self.frame_canvas.bind("<Configure>", comando_aux)
		#self.frame_canvas.bind("<Configure>", self.onFrameConfigure)
		#self.frame_canvas.configure(background="red") #<- DELENDA EST

		self.actualizar_ramos_inferior()
		
	"""    
	def onFrameConfigure(self,event): # StackOverflow :P
		self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
	"""

	def onFrameConfigureSub(self,cv):
		cv.configure(scrollregion=cv.bbox("all"))

	def actualizar_ramo_quitado_inferior(self,codigo):
		print "s.d_c_r",self.d_cajas_ramo
		
		try:
		    self.d_cajas_ramo[codigo]['frame'].destroy()
		    del self.d_cajas_ramo[codigo]
		except KeyError:
		    pass
		
		for dicc in self.d_cajas_ramo.values():
		    dicc['frame'].pack_forget()

		for dicc in self.d_cajas_ramo.values():
		    dicc['frame'].pack(side=LEFT, fill=Y)

		
	def actualizar_ramos_inferior(self,agregaRamo=True): # <------------?
		'''Si agregaRamo = True, significa que fue llamado por widgets_main
		   Si no, fue llamado por quitarRamo.'''
		if len(self.d_cajas_ramo) != 0:
			for dicc in self.d_cajas_ramo.values():
			    dicc['frame'].pack_forget()
			    dicc['frame'].destroy()
			self.d_cajas_ramo = dict()     

		for ramo in self.d_cargados:       # <----- CREO QUE POR AQUI TENGO LA PURA EMBARRA :CCCCCCCCCCC
			#print ramo, "in self.cargados"         # PD.: Falta arreglar el puro Scroll
			frame = Frame(self.frame_canvas,width=250,height=280)
			frame.pack(side=LEFT,fill=Y)
			frame.pack_propagate(0)
			
			canvas = Canvas(frame,borderwidth=0,bg="green")#bg="#cc3102") #<----- DELENDA (green)
			frame_in_canvas = Frame(canvas)
			scroll = Scrollbar(frame,command = canvas.yview)
			canvas.configure(yscrollcommand = scroll.set)

			scroll.pack(side=RIGHT,fill=Y)
			canvas.pack(fill=BOTH,expand = True)
			canvas.create_window((4,4), window = frame_in_canvas, anchor="nw")#,tags="frame_in_canvas")

			diccionario = {'frame':frame, 'canvas':canvas, 'frame_in_canvas':frame_in_canvas}

			comando_bind = lambda event : self.onFrameConfigureSub(canvas)    

			frame_in_canvas.bind("<Configure>", comando_bind)
			#frame_in_canvas.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigureSub(canvas))

			self.d_cajas_ramo[self.ultimo_ramo_cargado] = diccionario
			#self.dicc_cajas_ramo.append(diccionario) #lista de diccionarios con los widgets pertinentes

			if agregaRamo: ### <-----------?
			    self.poblar_widgets_ultimo_ramo()

		print "----"
		self.dibujar_bloques()

	def nuevo_ramo_inferior(self):
		ramo = self.d_cargados[self.ultimo_ramo_cargado]

		frame = Frame(self.frame_canvas,width=250,height=280)
		frame.pack(side=LEFT,fill=Y)
		frame.pack_propagate(0)

		canvas = Canvas(frame,borderwidth=0,bg="green")#bg="#cc3102") #<----- DELENDA (green)
		frame_in_canvas = Frame(canvas)
		scroll = Scrollbar(frame,command = canvas.yview)
		canvas.configure(yscrollcommand = scroll.set)

		scroll.pack(side=RIGHT,fill=Y)
		canvas.pack(side=LEFT,expand = True)
		#canvas.pack_propagate(0)
		canvas.create_window((4,4), window = frame_in_canvas, anchor="nw")#,tags="frame_in_canvas")

		diccionario = {'frame':frame, 'canvas':canvas, 'frame_in_canvas':frame_in_canvas}

		comando_bind = lambda event : self.onFrameConfigureSub(canvas)    

		frame_in_canvas.bind("<Configure>", comando_bind)
		#frame_in_canvas.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigureSub(canvas))

		self.d_cajas_ramo[self.ultimo_ramo_cargado] = diccionario
		#self.dicc_cajas_ramo.append(diccionario) #lista de diccionarios con los widgets pertinentes

		self.poblar_widgets_ultimo_ramo()
		#self.poblar_widgets_ramo(i)
		self.dibujar_bloques()
		self.ud_actualizar_cargadas()

	def poblar_widgets_ultimo_ramo(self): #nuevo ramo
		'''Lee el ramo que quiero cargar (cuyo codigo es self.ultimo_ramo_cargado)
		Escribe el nombre y los datos generales en el frame_in_canvas que le corresponde,
		coloca un Radiobutton para cada seccion, una checkbox (para mostrar/ocultar el ramo)
		y un boton para eliminarlo. Guarda las variables en un diccionario, y guarda
		el diccionario en self.dicc_widgets_ramo

		Guarda los bloques de cada seccion en una lista, y esa lista en self.bloques_ramo.
		Posteriormente, self.dibujar_bloques solo tiene que leerlos desde ahi.'''

		ultimo_ramo = self.ultimo_ramo_cargado

		ramo = self.d_cargados[ultimo_ramo]
		nombre_y_cod = ramo[0]
		codigo = nombre_y_cod[:nombre_y_cod.find(' ')]

		datos_generales = ramo[1]
		lista_secciones = ramo[2:]
		print "poblar:", ramo

		frame = self.d_cajas_ramo[ultimo_ramo]['frame_in_canvas']
		frame.pack()
		titulo = (nombre_y_cod[:34]+"..") if len(nombre_y_cod) > 34 else nombre_y_cod
		Label(frame,text = titulo).pack()

		try:
			uds_ramo = datos_generales["UD"]
		except KeyError:
			uds_ramo = "[N/A]"

		Label(frame,text = uds_ramo +" UD").pack()#side=LEFT)

		f_secc = Frame(frame)
		f_secc.pack(pady=5)

		if ultimo_ramo not in self.d_widgets_ramo:
			varCheck = BooleanVar()
			varRadio = IntVar()
		else:
			varCheck = self.d_widgets_ramo[ultimo_ramo]['mostrar']
			varRadio = self.d_widgets_ramo[ultimo_ramo]['seccion']

		comando = lambda : self.dibujar_bloques_codigo(str(ultimo_ramo))
		#siempre va a ser el ultimo ramo cargado, pero para cada ramo nuevo que se pueble,
		# la funcion 'comando' va a ser distinta
		C = Checkbutton(f_secc, text = "Mostrar", variable=varCheck, onvalue=True,\
						offvalue=False, command= comando)

		C.pack(anchor=W)

		bloques = [] # [bloques seccion1, bloques seccion2, ...]
		i = 0
		print "        secciones:"
		for seccion in lista_secciones:
			print " "*10, seccion

			try:
				cupo = seccion.cupo
			except AttributeError:
				cupo = ""

			try:
				ocupados = seccion.ocupados
			except AttributeError:
				ocupados = ""

			'''    
			profes = ""
			for profe in seccion.profes:
				profes += (profe+'\n')
			'''
			try:
				profes = seccion.str_profes
			except AttributeError:
				profes = "<Sin prof.>"

			texto = '('+ocupados+'/'+cupo+') ' + profes
			texto = (texto[:35]) if len(texto) > 35 else texto
			n_secc = str(i+1)
			texto = n_secc + ") " + texto

			R = Radiobutton(f_secc, text = texto, variable=varRadio,\
						value = i, command = self.dibujar_bloques)
			R.pack(anchor=W)
			if len(seccion) > 3: bloques.append(seccion[3])
			else: bloques.append([])

			i+=1

		#self.bloques_ramo.append(bloques)
		self.d_bloques_ramo[ultimo_ramo] = bloques

		#master_frame = self.dicc_cajas_ramo[indice]['frame']
		print "fww", frame.winfo_width()
		#master_frame.config(width = frame.winfo_width())

		remover = Button(f_secc, text="Quitar", command = lambda: self.quitarRamo(ultimo_ramo))
		remover.pack()

		handles = {'mostrar':varCheck, 'seccion':varRadio, 'checkbox':C}
		self.d_widgets_ramo[ultimo_ramo] = handles
		#self.dicc_widgets_ramo.append(handles)
	 
	def dibujar_bloques(self):
		print "dibujando?"
		self.canvas.delete("all")
		self.n_bloques = 0
		self.tabla_horario()
		self.d_geometrias_ramo = dict()

		'''
		for i in range(len(self.bloques_ramo)):
		    if self.dicc_widgets_ramo[i]['mostrar'].get():
		        self.dibujar_bloques_indice(i)
		'''
		for cod in self.d_cargados:
		    if self.d_widgets_ramo[cod]['mostrar'].get():
		        self.dibujar_bloques_codigo(cod)
		self.ud_actualizar_mostradas()
		self.choques_actualizar()


	def dibujar_bloques_codigo(self,codigo):
		varCheckbox = self.d_widgets_ramo[codigo]['mostrar'] #evento "caja marcada o desmarcada?"

		if varCheckbox.get(): #si "Mostrar" esta marcado
		    color = self.asignar_color(codigo)

		    seccion_marcada = self.d_widgets_ramo[codigo]['seccion'].get() #numero seccion marcada por Radiobutton
		    bloques = self.d_bloques_ramo[codigo][seccion_marcada]
		    
		    items_canvas = []
		    i=0
		    for bloque in bloques: #bloque = structHorario.Bloque(str tipo, str dia, Hora ti, Hora tf)
		        dias = ["lu","ma","mi","ju","vi","sa"]
		        w = 600
		        tipo = bloque.tipo
		        dia = bloque.dia
		        ti = bloque.ti # class Hora
		        tf = bloque.tf #


		        # El contorno del rectangulo depende del tipo de ramo
		        dashTuple = None
		        if tipo == "aux":
		            dashTuple = (2,2)
		        elif tipo == "lab":
		            dashTuple = (3,2,1)

		        offset = 0
		        if len(self.d_cargados)>1:
		            offset = 3*i/(len(self.d_cargados) - 1)
		        print "off",offset

		        x1 = equis1 = dias.index(bloque.dia)*w/5+offset
		        x2 = x1+w/5-30
		        y1 = self.minutos_a_coord(ti.getMinutos())
		        y2 = self.minutos_a_coord(tf.getMinutos())

		        R = self.canvas.create_rectangle(x1,y1,x2,y2, tags=codigo, dash=dashTuple,fill=color)
		        texto = codigo+"\n("+tipo+")"
		        T = self.canvas.create_text(x1+w/10-offset, (y1+y2)/2 ,text = texto, tags=codigo)
		        items_canvas.append(R)
		        items_canvas.append(T)
		        i+=1
		        self.n_bloques += 1

		    self.d_geometrias_ramo[codigo] = items_canvas
		    print "s.d_g_r",self.d_geometrias_ramo
		    
		else: #"Mostrar" esta desmarcado
		    self.canvas.delete(codigo) #borro todas las geometrias con el tag [codigo]

		self.ud_actualizar_mostradas()
		self.choques_actualizar()
		    
		
	def asignar_color(self,codigo):
		ran = lambda: randint(30,255)
		epsilon = lambda: randint(-6,6)
		n_alto = lambda: randint(150,245)
		n_medio = lambda: randint(100,170)
		n_bajo = lambda: randint(50,90)

		color_str = lambda a,b,c: ('#%02X%02X%02X' % (a,b,c))

		depto = codigo[:2].lower()
		yr = int(codigo[3])
		if len(codigo) == 6:
		    if depto == "ma":
		        b = n_bajo()
		        if codigo[3:5] == "00": #calculos
		            return color_str(n_alto(),b+epsilon(),b+epsilon())
		        return color_str(b+epsilon(),b+epsilon(),n_alto()) #alg,edo
		    if depto == "ei": return color_str(n_alto(),min(n_alto(),190),n_alto())
		    if yr == 1:
		        if depto == "fi":
		            a = n_alto()
		            return color_str(n_bajo(),a+epsilon(),a+epsilon())
		        if depto == "cc": return color_str(n_bajo(),n_medio(),n_alto())
		        if depto == "cm": return color_str(n_bajo(),n_alto(),n_medio())
		        return color_str(ran(),ran(),ran())
		    if depto == "in": return color_str(n_alto(),n_medio(),epsilon()+6)
		    a = color_str(n_alto(),n_medio(),n_medio())
		    b = color_str(n_medio(),n_medio(), n_alto())
		    c = color_str(n_medio(),n_alto(),n_medio())
		    return choice([a,b,c])
		a = color_str(n_alto(),n_medio(),n_medio())
		b = color_str(n_medio(),n_medio(), n_alto())
		c = color_str(n_medio(),n_alto(),n_medio())
		return choice([a,b,c])

	def quitarRamo(self,codigo):
		del self.d_cargados[codigo]
		self.canvas.delete(codigo)
		
		try:
		    check = self.d_widgets_ramo[codigo]['checkbox']
		    check.deselect()
		    del self.d_widgets_ramo[codigo]
		except KeyError:
		    print "KE"
		    pass
		
		try:
		    del self.d_geometrias_ramo[codigo]
		    frame = self.d_cajas_ramo[codigo]['frame']
		    frame.pack_forget()
		    frame.destroy()
		    del self.d_cajas_ramo[codigo]
		except KeyError:
		    pass

		self.actualizar_ramo_quitado_inferior(codigo)
		#self.actualizar_ramos_inferior(False)
		self.ud_actualizar_cargadas()
		self.ud_actualizar_mostradas()
		self.choques_actualizar()
		
	"""        
	def quitarRamo(self,i):
		self.cargados.pop(i)
		for item in self.geometrias_ramo[i]:
		    self.canvas.delete(item)
		self.geometrias_ramo.pop(i)
		    
		self.actualizar_ramos_inferior() # <----- Falta programar solo el "remover dibujos", no borrar todas las variables
		self.dicc_cajas_ramo[i]['frame'].destroy()
		self.dicc_cajas_ramo.pop(i)
		self.dicc_widgets_ramo.pop(i)
		self.bloques_ramo.pop(i)
	"""
		
		
	'''def populate(self):
		
		for row in range(100):
		    Label(self.frame_canvas, text="%s" % row, width=3,borderwidth="1",\
		          relief="solid").pack(side=LEFT)
		    t="this is the second column for row %s" %row
		    Label(self.frame_canvas, text=t).pack(side=LEFT) '''

	#--------------------- Barra de estado ventana principal

	def status_main(self):
		self.frame_status = Frame(self.frame_1)
		self.frame_status.pack(fill=X)

		self.frame_ud = Frame(self.frame_status,bg="red")#,width=30,height=20)
		self.frame_ud.pack(side=LEFT)
		
		self.ud_cargadas = UDs_Bar(self.frame_ud,"UDs Cargadas")
		self.ud_mostradas = UDs_Bar(self.frame_ud,"UDs Mostradas")

		self.choques = ChoquesBar(self.frame_status,"Choques (mostrados)")

	def ud_actualizar_cargadas(self):
		n_uds = 0
		error = False
		for ramo in self.d_cargados.values():
			datos_ramo = ramo[1]
			#uds_ramo = datos_ramo[0]
			uds_ramo = datos_ramo['UD'] # <--- cambie datos a dict
			if not uds_ramo.isdigit():
				error = True
			else:
				n_uds += int(uds_ramo)

		if error:
		    n_uds = str(n_uds) +"?"
		else:
		    n_uds = str(n_uds)

		self.ud_cargadas.set_UDs(n_uds)

	def ud_actualizar_mostradas(self):
		try:
		    n_uds = 0
		    error = False
		    for cod in self.d_cargados:
		        if self.d_widgets_ramo[cod]['mostrar'].get():
					ramo = self.d_cargados[cod]
					datos_ramo = ramo[1]
					#uds_ramo = datos_ramo[0]
					uds_ramo = datos_ramo['UD'] # <--- cambie datos a dict
					if not uds_ramo.isdigit():
						error = True
					else:
						n_uds += int(uds_ramo)

		    if error:
		        n_uds = str(n_uds) +"?"
		    else:
		        n_uds = str(n_uds)

		    self.ud_mostradas.set_UDs(n_uds)
		except AttributeError:
		    pass

	def choques_actualizar(self):
		try:
		    bloques_mostrados = []
		    for cod in self.d_cargados:
		        if self.d_widgets_ramo[cod]['mostrar'].get():
		            seccion_marcada = self.d_widgets_ramo[cod]['seccion'].get()
		            bloques = self.d_bloques_ramo[cod][seccion_marcada]
		            bloques_mostrados.extend(bloques)

		    n_choques = 0
		    
		    n = len(bloques_mostrados)
		    for i in range(n):
		        for j in range(i+1,n):
		            bloque_x = bloques_mostrados[i]
		            bloque_y = bloques_mostrados[j]
		            if bloque_x.chocaCon(bloque_y):
		                n_choques+=1

		    self.choques.set_choques(str(n_choques))
		except AttributeError:
		    pass
		 
	#--------------------- COMUN
	def cerrar_ventana(self,i):
		self.ventanas_cerradas[i] = True
		if i == 0: self.ventanas['carga'].destroy()
		elif i == 1: self.ventanas['db'].destroy()
		elif i == 2: self.ventanas['agregar'].destroy()
		
	#--------------------- VENTANA CARGA (catalogos) -----------------------
	def manage_db(self):
		if self.ventanas_cerradas[0]:
		    self.ventanas_cerradas[0] = False
		    
		    self.ventanas['carga'] = Toplevel(self,padx=5,pady=5)
		    self.ventanas['carga'].resizable(width=False,height=True)

		    self.ventanas['carga'].protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana(0))
		    self.ventanas['carga'].title("Gestionar catalogos")

		    #lista catalogos cargados
		    frame_catalogos = Frame(self.ventanas['carga'])
		    frame_catalogos.pack(fill=X)

		    self.lista_catalogos = Listbox(frame_catalogos)
		    self.lista_catalogos.pack(fill=X)

		    self.actualizar_lista_catalogos()

		    #botones catalogos
		    b_borrar = Button(frame_catalogos,text = u"Remover catálogo", command=self.borrar_item_lista_cat)
		    b_borrar.pack(side=LEFT)

		    b_guardar = Button(frame_catalogos,text = u"Guardar catálogo", command=self.guardar_item_lista_cat)
		    b_guardar.pack(side=LEFT)

		    #importar desde archivo
		    frame_importar = Frame(self.ventanas['carga'])
		    frame_importar.pack(pady=10)
		    Button(frame_importar, text="Importar catalogo desde archivo",command=self.importar).pack(side=LEFT)

		    #descargar desde ucampus
		    frame_descargar = LabelFrame(self.ventanas['carga'], text="Descargar catalogo desde U-Campus:")
		    frame_descargar.pack(pady=10)
		    #Label(frame_descargar, text="Descargar catalogo desde U-Campus:").pack()

		    Label(frame_descargar, text = u"Año").pack(side=LEFT)
		    self.year_entry = Entry(frame_descargar,width=5)
		    self.year_entry.insert(0,str(date.today().year))
		    self.year_entry.pack(side=LEFT)

		    Label(frame_descargar, text = u"Semestre").pack(side=LEFT)
		    self.sem_entry = Entry(frame_descargar,width=3)
		    semestre_tentativo = 1
		    if date.today().month > 6: semestre_tentativo = 2
		    self.sem_entry.insert(0,str(semestre_tentativo))
		    self.sem_entry.pack(side=LEFT)
		    
		    Button(frame_descargar, text="Descargar", command = self.descargar).pack()          
		    

	def actualizar_lista_catalogos(self):
		self.lista_catalogos.delete(0,END)
		for item in self.catalogos: self.lista_catalogos.insert(END,item[0])
		self.lista_catalogos.update_idletasks()

	def borrar_item_lista_cat(self):
		item_seleccionado = map(int, self.lista_catalogos.curselection())
		if len(item_seleccionado) > 0:
		    self.catalogos.pop(item_seleccionado[0])
		self.actualizar_lista_catalogos()

	def guardar_item_lista_cat(self):
		item_seleccionado = map(int, self.lista_catalogos.curselection())
		if len(item_seleccionado) > 0:
			item = self.catalogos[item_seleccionado[0]]
			nombre = item[0]
			catalogo = item[1]
			if nombre[:3] == "DES":
				cod = nombre.split(" ")[-1]
				slash = cod.find('/')
				yr = int(cod[:slash])
				sem = int(cod[slash+1:])
			elif nombre[:8] == "catalogo":
				yr = int(nombre[8:12])
				sem = int(nombre[12])
			else:                               #<-------faltan los catalogos personales/EDIT: ni loco los implemento
				yr = 0000
				sem = 0
			print "g_i_l_c so far so good..."
			filename = guardarCatalogo(catalogo,yr,sem)
			term = str(yr)+"-"+str(sem)
			info = u"Catálogo "+term+" guardado con nombre "+filename
			tkMessageBox.showinfo("Guardado", info)
		    
		
	def importar(self):
		    filename = askopenfilename().split('/')
		    filename = filename[-1]

		    catalogo = cargarCatalogo(filename)
		    #nombre = filename[:filename.find('.')]
		    
		    self.catalogos.append([filename,catalogo])

		    self.actualizar_lista_catalogos()
		    self.actualizar_db()            

	def descargar(self):
		print type(self.year_entry)
		yr = self.year_entry.get()
		sem = self.sem_entry.get()
		if yr.isdigit() and sem.isdigit():
		    yr,sem = int(yr),int(sem)
		    if sem in [1,2,3] and yr > 2009:
		        print "loading"
		        catalogo = getCatalogo(yr,sem)
		        print "(truco archivo temporal)"
		        archivo_temporal = guardarCatalogo(catalogo,yr,sem,"fcfm_tmp", "~cat"+str(yr)+str(sem))
		        catalogo = cargarCatalogo(archivo_temporal)
		        os_remove(archivo_temporal)                
		        self.catalogos.append(["DESCARGADO "+str(yr)+"/"+str(sem),catalogo])
		        self.actualizar_lista_catalogos()
		print "len self.catalogos", len(self.catalogos)


	#--------------------- VENTANA DB (cursos) -----------------------
	def nombre_depto(self,depto):
		nombres = {'AS':u'Astronomía', 'BT':u'Biotecnología', 'CC':u'Computación', 'CI':'Civil',\
		               'CM':'Ciencia de los Materiales', 'DR':'Deportivo/Recreativo/Cultural',\
		               'EH':'Humanista', 'escuela':'Escuela de Ing. y Cs.', 'idiomas':'Escuela de Ing. y Cs. (Idiomas)',\
		               'ing':'Escuela de Ing. y Cs. (Ing. e Inn.)', 'EL':u'Eléctrica', 'FG':'Formacion General',\
		               'FI':u'Física', 'GF':'Geofisica', 'GL':u'Geología', 'IN':'Industrias', 'IQ':u'Química',\
		               'MA':u'Matemática', 'ME':u'Mecánica', 'MI':'Minas', 'TE':u"Área de Idiomas", 'VA':u"Formación General"}
		try:
		    return nombres[depto]
		except KeyError: return "?????"

	def ventana_ramos_db(self):
		print ":DDDDDD"
		if self.ventanas_cerradas[1]:
		    self.ventanas_cerradas[1] = False
		    
		    self.ventanas['db'] = Toplevel(self,padx=5,pady=5)
		    self.ventanas['db'].minsize(width=245, height = 400)
		    self.ventanas['db'].title("Lista de catalogos")
		    self.ventanas['db'].protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana(1))
		    
		    N = len(self.catalogos)

		    #db_frame = Frame(self.ventanas['db'], width=200, height = 300)
		    db_frame = Frame(self.ventanas['db'])
		    db_frame.pack(fill=BOTH,expand=True)

		    union_codigos = []
		    for i in range(N):
		        cat = self.catalogos[i][1]
		        for depto in cat:
		            if depto[0] not in union_codigos:
		                union_codigos.append(depto[0])

		    self.union_catalogos = []
		    for codigo in union_codigos:
		        depto = [codigo]
		        for i in range(N):
		            cat = self.catalogos[i][1]
		            for d in cat:
		                if d[0] == codigo:
		                    depto.extend(d[1:])
		        self.union_catalogos.append(depto)

		    cursos_PC = ["PC"]
		    for i in range(len(self.union_catalogos)):
		        sigla = union_codigos[i]
		        if sigla in ["MA","FI","CM","CC","IN","ing"]:
		            dept = self.union_catalogos[i]
		            for curso in dept[1:]:
		                cod = curso[0].split(" ")[0]
		                if len(cod) != 6:
		                    continue
		                else:
		                    yr = int(cod[2])
		                    if yr <= 2:
		                        cursos_PC.append(curso)
		    
		    self.union_catalogos.insert(0,cursos_PC)

		    self.items_menu = [u"Plan Común"]
		    for cod in union_codigos:
		        nom = cod
		        if nom in ['escuela','ing','idiomas']: nom = "EI"
		        self.items_menu.append(nom+" "+self.nombre_depto(cod))

		    #Variables para leer curso/depto seleccionado
		    self.var_CBox = StringVar()
		    self.CBox = Combobox(db_frame, textvariable=self.var_CBox, state='readonly',width=35)
		    self.CBox['values'] = tuple(self.items_menu)
		    self.CBox.bind("<<ComboboxSelected>>", lambda x: self.actualizar_lista_cursos())
		    self.CBox.current(0)
		    self.CBox.pack()

		    f = Frame(db_frame)
		    f.pack()

		    escrolbar = Scrollbar(f)
		    escrolbar.pack(side=RIGHT, fill=Y)
		    
		    self.lista_cursos = Listbox(f,height=25, width= 35)
		    self.lista_cursos.pack(fill=X)

		    self.lista_cursos.config(yscrollcommand = escrolbar.set)
		    escrolbar.config(command = self.lista_cursos.yview)

		    f2 = Frame(db_frame)
		    f2.pack()

		    Button(f2,text="Agregar al horario", command=self.agregar_al_horario).pack()
		    

		    self.actualizar_lista_cursos()

	def actualizar_lista_cursos(self):
		i = self.items_menu.index(self.var_CBox.get())
		self.lista_cursos.delete(0,END)
		for item in self.union_catalogos[i][1:]:
		    self.lista_cursos.insert(END,item[0])
		self.lista_cursos.update_idletasks()


	def agregar_al_horario(self):
		'''No lee mas parametros: tanto el departamento como el curso seleccionado
		los lee de self.var_CBox y self.lista_cursos en ventana_ramos_db()'''
		
		depto_seleccionado = self.items_menu.index(self.var_CBox.get())
		print "depto_seleccionado",depto_seleccionado
		curso_seleccionado = map(int, self.lista_cursos.curselection())[0] + 1 # ojo con el +1
		print "curso_seleccionado",curso_seleccionado

		curso = self.union_catalogos[depto_seleccionado][curso_seleccionado]

		if curso.cod not in self.d_cargados:
		    self.d_cargados[curso.cod] = curso
		    print "--self.d_cargados"
		    print self.d_cargados
		    print "--End_self.d_cargados"
		    self.ultimo_ramo_cargado = curso.cod
		    self.nuevo_ramo_inferior()

		'''
		if curso not in self.cargados: #solo si el curso ya no estaba
		    self.cargados.append(curso)
		    print "--self_cargados"
		    print self.cargados
		    print "--End_self_cargados"
		    #self.actualizar_ramos_inferior()
		    self.nuevo_ramo_inferior()
		'''

	def actualizar_db(self): pass


class StatusBar:
    #pk=-1 -> pack side=LEFT;    0 -> fill=X;    1 -> side=RIGHT
    def __init__(self, frame, ancho,pk=-1):
        self.label = Label(frame, bd=2, relief=RIDGE, anchor=W, width=ancho)
        if pk == -1:
            self.label.pack(side=LEFT)
        elif pk == 0:
            self.label.pack(fill=X)
        else:
            self.label.pack(side=RIGHT)

    def set(self, texto):
        self.label.config(text=texto)

    def clear(self):
        self.label.config(text="")

class UDs_Bar(StatusBar):
    def __init__(self,frame,texto):
        StatusBar.__init__(self, frame, 17)
        self.text = texto
        self.uds = "0"
        self.update_label()

    def set_UDs(self,uds):
        self.uds = uds
        self.update_label()

    def update_label(self):
        self.set(self.text+": "+self.uds)


class ChoquesBar(StatusBar):
    def __init__(self,frame,texto):
        StatusBar.__init__(self, frame, 20, pk=1)
        self.text = texto
        self.choques = "0"
        self.update_label()

    def set_choques(self,choques):
        self.choques = choques
        self.update_label()

    def update_label(self):
        self.set(self.text+": "+self.choques)
        if self.choques != "0":
            self.label.config(fg = "red3")
        else:
            self.label.config(fg = "black")

                           
if __name__ == "__main__":
    root = Tk()
    root.wm_title("Mallador")

    if os_name == "nt": root.iconbitmap(default='favicon2.ico')
    
    main = VentanaMallador(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()

# -*- coding: cp1252 -*-
from fetcher import *
from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
from datetime import date
from os import getcwd
from os import name as os_name
from random import randint
from random import choice

###BUGS:- No se puede exportar un catalogo importado: si lo arreglo para la exportacion,
###         no se puede importar y viceversa. Algun dia tendre que arreglar "fetcher"
###         para que trabaje de forma mas limpia con Unicode
###
###     - VentanaMallador permite multiples ventanas Toplevel de cada instancia abiertas
    
class VentanaMallador(Frame):
    counter = 0
    def __init__(self,*args,**kwargs):
        self.frame_1 = Frame.__init__(self, *args, **kwargs)
        self.root = args[0]

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
        self.winmenu.add_command(label="Mostrar Cursos Seleccionados",\
                                 command=self.ventana_ramos_db)
        self.menubar.add_cascade(label="Ventanas", menu=self.winmenu)

        #mostrar barra menu
        self.root.config(menu = self.menubar)

        self.catalogos = [] #[["nombre", catalogo], ["nombre", catalogo], ...]

        #info para descargar
        self.year_entry = None
        self.sem_entry = None

        #lista catalogos
        self.lista_catalogos = None

        #lista de cursos cargados
        self.cargados = []
        self.dicc_cajas_ramo = [] #<-- para guardar las cajas de los objetos dentro del canvas que se mueve
        self.dicc_widgets_ramo = [] #<-- para guardar las variables de los widgets
        self.bloques_ramo = [] # [ [ramo1 = cod, bloques s1, bloques s2, ...], [ ramo2 = cod, bloques s1, bloques s2, ...],. ...]
        self.geometrias_ramo = [] # <-- geometrias_ramo[i] tiene los rectangulos y textos del ramo i

        #Widgets de esta ventana
        self.canvas = Canvas(self.frame_1,width=660, height=300, bg="white")
        self.canvas.pack()
        self.tabla_horario()
        self.widgets_main()
        
        
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

            
    def widgets_main(self):
        frame_2 = Frame(self.frame_1,height=260)
        frame_2.pack(fill=X)
        frame_2.pack_propagate(0)

        self.canvas_scroll = Canvas(frame_2, borderwidth=0)#width=660, height=250)
        self.frame_canvas = Frame(self.canvas_scroll)
        scrollbar = Scrollbar(frame_2,orient=HORIZONTAL,command=self.canvas_scroll.xview)
        self.canvas_scroll.configure(xscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=BOTTOM,fill=X)
        self.canvas_scroll.pack(fill=BOTH,expand=True)
        self.canvas_scroll.create_window((4,4), window=self.frame_canvas, anchor="nw", 
                                  tags="self.frame_canvas")

        self.frame_canvas.bind("<Configure>", self.onFrameConfigure)

        self.actualizar_ramos_inferior()
        
    def onFrameConfigure(self,event): # StackOverflow :P
        self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

    def onFrameConfigureSub(self,canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def actualizar_ramos_inferior(self):
        i = 0
        for ramo in self.cargados:
            #print ramo, "in self.cargados"
            frame = Frame(self.frame_canvas,width=200)
            frame.pack(side=LEFT,fill=Y)
            Label(frame,text="test").pack()
            frame.pack_propagate(0)
            
            canvas = Canvas(frame,borderwidth=0,bg="#cc3102")
            frame_in_canvas = Frame(canvas)
            scroll = Scrollbar(frame,command = canvas.yview)
            canvas.configure(yscrollcommand = scroll.set)

            scroll.pack(side=RIGHT,fill=Y)
            canvas.pack(fill=BOTH,expand = True)
            canvas.create_window((4,4), window = frame_in_canvas, anchor="nw",tags="frame_in_canvas")

            diccionario = {'frame':frame, 'canvas':canvas, 'frame_in_canvas':frame_in_canvas}

            frame_in_canvas.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigureSub(canvas))

            self.dicc_cajas_ramo.append(diccionario)

            self.poblar_widgets_ramo(i)

                       
            i+=1
        print "----"
        self.dibujar_bloques()
        
    '''
    def poblar_widgets_ramo(self,indice):
        pass
    '''

    def poblar_widgets_ramo(self,indice):
        '''Lee el ramo que quiero cargar (el indice-esimo) de self.cargados.
        Escribe el nombre y los datos generales en el frame_in_canvas que le corresponde,
        coloca un Radiobutton para cada seccion, una checkbox (para mostrar/ocultar el ramo)
        y un boton para eliminarlo. Guarda las variables en un diccionario, y guarda
        el diccionario en self.dicc_widgets_ramo

        Guarda los bloques de cada seccion en una lista, y esa lista en self.bloques_ramo.
        Posteriormente, self.dibujar_bloques solo tiene que leerlos desde ahi.'''
        ramo = self.cargados[indice]
        
        nombre_y_cod = ramo[0]
        codigo = nombre_y_cod[:nombre_y_cod.find(' ')]
        
        datos_generales = ramo[1]
        lista_secciones = ramo[2:]
        print "poblar:", ramo
    
        frame = self.dicc_cajas_ramo[indice]['frame_in_canvas']
        frame.pack()
        Label(frame,text = nombre_y_cod).pack()
        Label(frame,text = datos_generales[0]+" UD").pack(side=LEFT)

        f_secc = Frame(frame)
        f_secc.pack(pady=5)

        varCheck = BooleanVar()
        C = Checkbutton(f_secc, text = "Mostrar", variable=varCheck, onvalue=True, offvalue=False, command= lambda: self.dibujar_bloques(indice))
        C.pack(anchor=W)
        
        varRadio = IntVar()
        bloques = [codigo] # [codigo, bloques s1, bloques s2, ...]
        i = 0
        for seccion in lista_secciones:
            print "tipo seccion", type(seccion)
            cupo = seccion.cupo
            ocupados = seccion.ocupados
            profes = ""
            for profe in seccion.profes:
                profes += (profe+'\n')
            
            texto = profes+'  ('+cupo+'/'+ocupados+')'
            R = Radiobutton(f_secc, text = texto, variable=varRadio,\
                        value = i, command = self.dibujar_bloques)
            R.pack(anchor=W)
            if len(seccion) > 3: bloques.append(seccion[3])
            else: bloques.append([])

            i+=1
            
        self.bloques_ramo.append(bloques)
            
        remover = Button(f_secc, text="Quitar", command = lambda: self.quitarRamo(indice))
        remover.pack()

        handles = {'mostrar':varCheck, 'seccion':varRadio}
        self.dicc_widgets_ramo.append(handles)
    
    def dibujar_bloques(self):
        self.canvas.delete("all")
        self.tabla_horario()
        self.geometrias_ramo = []
        
        for i in range(len(self.bloques_ramo)):
            if self.dicc_widgets_ramo[i]['mostrar'].get():
                seccion_marcada = self.dicc_widgets_ramo[i]['seccion'].get()
                codigo = self.bloques_ramo[i][0]
                bloques = self.bloques_ramo[i][seccion_marcada + 1] # bloques_ramo[i] = [codigo, bloques s1, bloques s2, ...]
                self.dibujar_bloques_ramo(codigo,bloques,i)
                
    def dibujar_bloques_ramo(self,codigo,bloques,indice): #indice indica que este es el indice-esimo ramo que estoy dibujando (offset)
        color = self.asignar_color(codigo)
        items_canvas = []
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
            if len(self.cargados)>1: offset = i/(len(self.cargados) - 1)

            x1 = equis1 = dias.index(bloque.dia)*w/5+offset
            x2 = x1+w/5-30
            y1 = self.minutos_a_coord(ti.getMinutos())
            y2 = self.minutos_a_coord(tf.getMinutos())

            R = self.canvas.create_rectangle(x1,y1,x2,y2,dash=dashTuple,fill=color)
            texto = codigo+"\n("+tipo+")"
            T = canvas.create_text(x1+w/10-offset, (y1+y2)/2 ,text = texto)
            items_canvas.append(R)
            items_canvas.append(T)
            
        self.geometrias_ramo.append(items_canvas)

    def asignar_color(self,codigo):
        ran = lambda: randint(30,255)
        epsilon = lambda: randint(-6,6)
        n_alto = lambda: randint(150,245)
        n_medio = lambda: randint(100,170)
        n_bajo = lambda: randint(10,90)

        color_str = lambda a,b,c: ('#%02X%02X%02X' % (a,b,c))

        depto = codigo[:2].lower()
        yr = int(codigo[3])
        if len(codigo) == 6:
            if depto == "ma":
                b = n_bajo()
                if codigo[3:5] == "00": #calculos
                    return color_str(n_alto(),b+epsilon(),b+epsilon())
                return color_str(b+epsilon(),b+epsilon(),n_alto()) #alg,edo
            if depto == "ei": return color_str(n_alto(),min(n_alto(),190),n_alto)
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

        
        
    '''def populate(self):
        
        for row in range(100):
            Label(self.frame_canvas, text="%s" % row, width=3,borderwidth="1",\
                  relief="solid").pack(side=LEFT)
            t="this is the second column for row %s" %row
            Label(self.frame_canvas, text=t).pack(side=LEFT) '''
    
    #--------------------- COMUN
    def cerrar_ventana(self,i):
        self.ventanas_cerradas[i] = True
        if i == 0: self.ventanas['carga'].destroy()
        elif i == 1: self.ventanas['db'].destroy()
        elif i == 2: self.ventanas['agregar'].destroy()
        
    #--------------------- VENTANA CARGA -----------------------
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
            guardarCatalogo(catalogo,yr,sem)
            
        
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
                self.catalogos.append(["DESCARGADO "+str(yr)+"/"+str(sem),catalogo])
                self.actualizar_lista_catalogos()
        print "len self.catalogos", len(self.catalogos)


    #--------------------- VENTANA DB -----------------------
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
            self.ventanas['db'].title("Lista de catalogos")
            self.ventanas['db'].protocol("WM_DELETE_WINDOW", lambda: self.cerrar_ventana(1))
            
            N = len(self.catalogos)

            db_frame = Frame(self.ventanas['db'], width=200, height = 300)
            db_frame.pack()

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
        depto_seleccionado = self.items_menu.index(self.var_CBox.get())
        print "depto_seleccionado",depto_seleccionado
        curso_seleccionado = map(int, self.lista_cursos.curselection())[0]
        print "curso_seleccionado",curso_seleccionado

        curso = self.union_catalogos[depto_seleccionado][curso_seleccionado]

        if curso not in self.cargados:
            self.cargados.append(curso)

            self.actualizar_ramos_inferior()

    def actualizar_db(self): pass


if __name__ == "__main__":
    root = Tk()
    root.wm_title("Mallador")

    if os_name == "nt": root.iconbitmap(default='favicon2.ico')
    
    main = VentanaMallador(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()

import urllib2
import unidecode
import datetime
import structHorario
import codecs
from bs4 import BeautifulSoup as BS
from os import listdir as ls
from os import getcwd as pwd

#definiciones:
#catalogo: lista de departamentos
#departamento: lista de cursos
#cursos: lista de secciones
#seccion: lista de structHorario.Bloque

#ejemplo de uso:
#>>> catalogo = getCatalogo(2016,2)
#>>> guardarCatalogo(catalogo,2016,2) #crea catalogo20162.fcfm
#-------
#>>> catalogo = cargarCatalogo("catalogo20162.fcfm")

global codigoDepto
codigoDepto = {'AS':'3', 'BT':'268', 'CC':'5', 'CI':'6', 'CM':'306', 'DR':'7',\
               'EH':'8', 'escuela':'27', 'idiomas':'9', 'ing':'12060002', 'EL':'10',\
               'FG':'310', 'FI':'13', 'GF':'15', 'GL':'16', 'IN':'19', 'IQ':'20',\
               'MA':'21', 'ME':'22', 'MI':'23'}
global codigosDeptos
codigosDeptos = codigoDepto.keys()
codigosDeptos.sort()

def urlCatalogo(yr,sem,sigla):
    yr,sem,sigla = str(yr),str(sem),str(sigla)
    return 'https://ucampus.uchile.cl/m/fcfm_catalogo/?semestre='+yr+sem+\
               '&depto='+codigoDepto[sigla]

siglas = codigoDepto.keys()

#dado el BeautifulSoup del catalogo de UN departamento
#retorna una lista (de cursos), con una lista de secciones en c/curso
#el primer item de la lista es el codigo del departamento
def parseCursosSopa(sopa):
    cod_cursos = [tag['id'] for tag in sopa.findAll('h2',{'id':True})]

    codigo_este_depto = cod_cursos[-1][:2]
    if codigo_este_depto == "EI":
        tag = sopa.find('ul',{'id':'navbar'})
        nombre_depto = unidecode.unidecode(tag.findAll('li')[1].text[5:]).lower()
        if nombre_depto[:3] == "esc": codigo_este_depto = "escuela"
        elif nombre_depto[:11] == "area de ing": codigo_este_depto = "ing"
        else: codigo_este_depto = "idiomas"
        
    departamento = [codigo_este_depto] # [codigo_este_depto, curso1, curso2, curso3, ...]
    
    i = 0
    tablas = sopa.findAll('table')
    for tabla in tablas:
        codigo_este_curso = cod_cursos[i]
        nombre_y_codigo = sopa.find('h2',{'id':codigo_este_curso}).text.replace('\n','').replace('\t','')
        item_curso = [nombre_y_codigo] # [nombre+codigo curso, [datos], secc1, secc2, secc3, ...]

        tag = sopa.find('h2',{'id':codigo_este_curso})
        tag = tag.find_next('dl')
        datos_raw = tag.findAll('dd') #UD, Requisitos, Equivalencias...

        datos = [dato.text.replace('\n','').replace('\t','') for dato in datos_raw]
        item_curso.append(datos)
        
        secciones = tabla.tbody.findAll('tr')
        for seccion in secciones:
            item_seccion = [] # [[Profes],Cupo,Ocupados,[Horario]]    
            
            datos_seccion = seccion.findAll('td')

            profes_seccion = datos_seccion[1].findAll('h1')
            vector_profes = []
            for profe in profes_seccion:
                vector_profes.append(profe.text.replace('\n','').strip())
            item_seccion.append(vector_profes)
            for j in range(2,4):
                item_seccion.append(datos_seccion[j].text.replace('\n','').strip())

            horario_raw = datos_seccion[4]
            horario_raw = repr(horario_raw).replace('\\t','').replace('\\n','').replace('\\r','')[4:-5].lower()
            if horario_raw == "":
                item_curso.append([])
                continue
            horario_raw = horario_raw.replace('\\xe1','a').replace('\\xe9','e').replace('\\xed','i')\
                          .replace('\\xf3','o').replace('\\xfa','u').replace('\\xf1','nh').replace('\\xc1','A')\
                          .replace('\\xc9','E').replace('\\xcd','I').replace('\\xbf','O').replace('\\xda','U')\
                          .replace('\\xfc','u').replace('\\xdc','U')
            
            lista_horario = [] #lista de Bloques
            for item in horario_raw.split('<br/>'):
                colon = item.find(':')
                tipo = item[:colon]
                #print "tipo :",tipo <- debugging
                if tipo == "catedra":
                    tipo = "cat"
                elif tipo == "auxiliar":
                    tipo = "aux"
                elif tipo == "laboratorio":
                    tipo = "lab"
                elif tipo == "control":
                    tipo = "con"
                elif tipo == "semana": #<-- Problemas diferenciando semanas de horas; no voy a parsear semanas (*)
                    continue
                else: tipo = "otro"
                item = item.split(" ")

                #print 'item: ',item # <- debugging
                #print 'len item:', len(item), 'item:',item,'type item:',type(item) 

                largo_item = len(item)
                indices = range(1,largo_item,4) #es un for "a la C", necesito jugar con los indices mas abajo
                k = 0
                while k < len(indices):
                    j = indices[k]
                    if item[j][:3] == "sem": #<-- Problemas (vease (*))
                        k = len(indices)
                        continue
                    dia = item[j][:2] #structHorario.Bloque maneja dias como 'lu', 'ma', ...
                    t_i = item[j+1]
                    t_f = item[j+3].replace(',','').replace(';','')
                    bloque2 = None
                    if j+4 < largo_item:
                        if item[j+4][0].isdigit(): #a veces un mismo dia tiene 2 bloques
                            t_i2 = item[j+4]
                            t_f2 = item[j+6]
                            bloque2 = structHorario.Bloque(tipo,dia,t_i2,t_f2)

                    #print "dia: "+dia,"t_i: "+t_i,"t_f: "+t_f <- debugging
                    bloque = structHorario.Bloque(tipo,dia,t_i,t_f)
                    
                    lista_horario.append(bloque)
                    k+=1
                    if bloque2 != None:
                        lista_horario.append(bloque2)
                        k+=2 #<-- juego de indices
                    
            item_seccion.append(lista_horario)
            #item_seccion.append(horario_raw.text)
            
            item_curso.append(item_seccion)
        departamento.append(item_curso)
        i+=1
    return departamento

        
#retorna una lista con las sopas del codigo HTML de cada depto
def getCatalogoHTML(yr,sem):
    yr,sem = str(yr),str(sem)

    catalogoHTML = []
    for s in codigosDeptos:
        url = urlCatalogo(yr,sem,s)
        html = urllib2.urlopen(urllib2.Request(url)).read()
        sopa = BS(html,'html.parser')
        catalogoHTML.append(sopa)
    return catalogoHTML

#retorna una lista "Catalogo" (cada elemento de getCatalogoHTML parseado
#por parseCursosSopa
def getCatalogo(yr,sem):
    catalogo = []
    
    for catalogo_depto in getCatalogoHTML(yr,sem):
        catalogo_depto_parseado = parseCursosSopa(catalogo_depto)
        catalogo.append(catalogo_depto_parseado)

    return catalogo


#dada una lista Catalogo, la codifica en texto para su posterior lectura
def guardarCatalogo(catalogo,yr,sem,extension='.fcfm'):
    nombre_archivo = "catalogo"+str(yr)+str(sem)
    directorio_actual = ls(pwd())
    if nombre_archivo+".fcfm" in directorio_actual:
        time = str(datetime.datetime.now()).replace(' ','-').replace(':','-')[0:19]
        nombre_archivo = nombre_archivo +"-"+ time
    nombre_archivo = nombre_archivo + extension
    
    save_file = codecs.open(nombre_archivo,'w',encoding='utf-8')
    for departamento in catalogo:
        n_cursos = str(len(departamento) - 1)
        cabecera_depto = '$'+n_cursos+';'+departamento[0]+'\n'
        print "cabecera:",cabecera_depto
        save_file.write(cabecera_depto) #escribe el codigo del depto
                                        # (ej: $25,AS si es que Astronomia impartiera
                                        # 25 cursos ese semestre)
        for curso in departamento[1:]:
            #print "curso:",curso # <- DEBUGGING
            n_secciones = str(len(curso) - 2)
            nombre_y_cod = curso[0]
            cabecera_curso = '%'+n_secciones+';'+nombre_y_cod+'\n'
            
            save_file.write(cabecera_curso) #ej: %3,MA2001 Calculo en Varias Variables, si
                                            #hubieran 3 secciones de CVV ese semestre
            datos_curso = curso[1]
            if len(datos_curso) < 2:
                string = '!N' #!N: "no hay datos"
            else:
                string = '!'+datos_curso[0]+';'+datos_curso[1]+";"
                if len(datos_curso) == 3:  string += datos_curso[2]+";"
            #print "string:",string
            save_file.write(unidecode.unidecode(string)+"\n")   #ej: !10;(MA1002/MA1A2),(MA1102/MA1B2);MA2A1/MA22A/MA220
                                            #porque CVV tiene 10 UD, y pide C.Diferencial y A.Lineal
            
            for seccion in curso[2:]:
                if seccion == []: continue
                #print "seccion:",seccion # <- DEBUGGING
                profes = seccion[0]
                if len(profes) == 0:
                    string_profes = ""
                else:
                    string_profes = profes[0]#.encode('utf-8')
                    for profe in profes[1:]: string_profes += ','+profe
                string = string_profes+";"+seccion[1]+";"+seccion[2]+";" #ej: 'Hector Olivero Quinteros;100;0;
                                                                         #porque H.Olivero es el profe, hay 100 cupos y 0 ocupados
                horario = seccion[3]
                if horario != []:
                    for bloque in horario:
                        datos_bloque = bloque.getBloque()

                        string_bloque = "B"+datos_bloque[0]+','+datos_bloque[1]+','+str(datos_bloque[2])+','+str(datos_bloque[3])+','
                                                                          #ej: Bcat,ma,08:30,10:00,
                        string += string_bloque
                    string += '\n' #ej: 'Hector Olivero Quinteros;100;0;Bcat,ma,08:30,10:00,Bcat,ju,08:30,10:00,Baux,mi,10:00,12:00,'
                save_file.write(string)#.encode('utf-8'))
        save_file.write('=EOD\n') #fin del departamento
    save_file.close()
    return

#carga una base de datos Catalogo generada por guardarCatalogo
#retorna una lista de departamentos
def cargarCatalogo(nombre_archivo):
    directorio_actual = ls(pwd())
    if nombre_archivo not in directorio_actual:
        raise OSError("Archivo "+nombre_archivo+" no encontrado")

    #cargar y leer archivo
    load_file = open(nombre_archivo,'r')
    file_data = [] #guardar informacion del archivo en un arreglo
    for linea in load_file: file_data.append(linea)
    load_file.close()
    
    largo_archivo = len(file_data)
    
    i=0
    catalogo = []
    depto = []
    curso = structHorario.Curso()
    while i < largo_archivo:
        item = file_data[i]
        primer_char = item[0]
        #print curso
        if primer_char == "$": #nuevo depto
            c = item.find(';')
            depto.append(item[c+1:-1]) #ingresar codigo depto
        elif primer_char == "=": #fin depto
            if len(curso) != 0:
                depto.append(curso)
                curso = structHorario.Curso()
            catalogo.append(depto)
            depto = []
        elif primer_char == "%": #nuevo curso en depto
            if len(curso) != 0:
                if len(curso) == 2: curso.append([])
                depto.append(curso)
                curso = structHorario.Curso()
            c = item.find(';')
            nombre_y_curso = item[c+1:-1]
            #print nombre_y_curso
            curso.append(nombre_y_curso)
        elif primer_char == "!": # datos de curso
            datos = item[1:-1].split(";")[:-1]
            curso.append(datos)
        elif primer_char != "\n": #item es un string seccion
            datos_seccion = item.replace('\n','').split(";")
                                
            vector_profes = []
            profes = datos_seccion[0]
            for profe in profes.split(','):
                vector_profes.append(profe)
                
            #print "datos_seccion:",datos_seccion
            seccion = structHorario.Seccion([vector_profes,datos_seccion[1],datos_seccion[2]])
            
            horario_raw = datos_seccion[3]
            horario = []

            bloques_raw = horario_raw.split('B')[1:]
            #print bloques_raw
            for bloque_raw in bloques_raw:
                b_raw = bloque_raw.split(",")
                #print "b_raw:", b_raw
                bloque = structHorario.Bloque(b_raw[0], b_raw[1], b_raw[2], b_raw[3])
                horario.append(bloque)
            seccion.append(horario)
            curso.append(seccion)
        i+=1
        
    return catalogo

#s = BS(urllib2.urlopen(urllib2.Request('http://www.cec.uchile.cl/~gabriel.flores.m/ex_ucampus.html')).read(),'html.parser')

        

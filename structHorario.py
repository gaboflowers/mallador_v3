from unidecode import unidecode

class Hora:
    #Hora: str -> Hora
    def __init__(self,time):
        if type(time) == unicode: time = str(time)
        if type(time) != str: raise TypeError
        if ":" not in time: raise ValueError("Colon not in argument")
        indexColon = time.index(":")
        if indexColon == 0 or indexColon == len(time) - 1:
            raise ValueError("Colon must be between hours and minutes")
        self.hora = int(time[:indexColon])
        self.min = int(time[indexColon+1:])

    def __str__(self):
        mins = str(self.min)
        if len(mins) == 1:
            mins = "0"+mins
        return "Hora("+str(self.hora)+":"+mins+")"

    #getHoraFloat: None -> float
    #retorna hora con decimal (10:30 es 10.5; 18:45 es 18,75)
    def getHoraFloat(self):
        return self.hora + self.min/60.0

    #getHora: None -> str
    #retorna hora como string
    def getHora(self):
        return str(self.hora) + ":" + (str(self.min).zfill(2))

    #getMinutos: None -> int
    #retorna cuantos minutos han pasado desde las 8:30
    def getMinutos(self):
        minutos = int(self.getHoraFloat()*60)
        ocho30 = 510 #minutos desde medianoche
        return minutos-ocho30

assert Hora("09:30").getMinutos() == 60
        
class Bloque:
    #Bloque: str str (str or int) Hora Hora -> Bloque
    def __init__(self,tipo,dia,ti,tf):
        if tipo not in ["cat","aux","lab","con","otro"]:
            raise ValueError("tipo must be 'cat', 'aux', 'lab', 'con' or 'otro'")
        self.tipo = tipo
        diaNum = [1,2,3,4,5,6]
        diaNom = ["lu","ma","mi","ju","vi","sa"]
        if type(dia) == int:
            self.dia = diaNom[diaNum.index(dia)]
        else:
            self.dia = dia.lower()[:2]
        self.ti = Hora(ti)
        self.tf = Hora(tf)

    def __str__(self):
        return "Bloque("+str(self.tipo)+","+str(self.dia)+","+str(self.ti)+","+str(self.tf)+")"

    def getBloque(self):
        return [self.tipo, self.dia, self.ti.getHora(), self.tf.getHora()]

    #__eq__: Bloque -> bool
    #True si 2 bloques empiezan y terminan a la misma hora el mismo dia
    def __eq__(self,x):
        return self.dia == x.dia and self.ti == x.ti and self.tf == x.tf

    #chocaCon: Bloque int -> bool
    #True si 2 bloques se solapan. Si el parametro "margen" se pasa, considera
    #ese tiempo (en minutos) como tolerancia maxima
    def chocaCon(self,x,margen=0):
        inicioA = self.ti.getHoraFloat()
        inicioB = x.ti.getHoraFloat()
        finA = self.tf.getHoraFloat()
        finB = x.tf.getHoraFloat()
        
        puntoA = max(inicioA, inicioB)
        puntoB = min(finA,finB)

        if puntoB*60.0 - puntoA*60.0 > margen and self.dia == x.dia:
            return True
        return False
   


class Seccion(list):
    def __init__(self,L=[]):
        list.__init__(self,L)
        
        try:
            self.profes = self[0]
        except IndexError:
            self.profes = []
            
        try:    
            self.cupo = self[1]
            if len(self.cupo) == 0: self.cupo = ""
            self.ocupados = self[2]
            if len(self.ocupados) == 0: self.ocupados = ""
        except IndexError:
            self.cupo = ""
            self.ocupados = ""

        if len(self.profes) == 0:
            self.nombre_profes = "<Profes no disp.>"
        else:
            self.nombre_profes = ", ".join(self.profes)

        if len(self.profes) == 0:
            self.str_profes = ""
        elif len(self.profes) >= 3:
            s = ""
            for p in self.profes:
                n_completo = p.split()
                nuevo = ""
                if len(n_completo) <= 1: s = p
                elif len(n_completo) == 2:
                    nuevo = n_completo[0]+". "+n_completo[1]+", "
                elif len(n_completo) == 3:
                    A = n_completo[0]
                    B = n_completo[1]
                    C = n_completo[2]
                    if "." in B:
                        nuevo = A[0]+". "+C+", "
                    else:
                        nuevo = A[0]+", "+B+", "
                else:
                    nuevo = n_completo[0]+". "
                    for n in n_completo[1:]:
                        if not n.istitle():
                            nuevo += (n + " ")
                        else:
                            nuevo += n
                            break
                    nuevo += ", "
                    
                s += nuevo
            self.str_profes = s[:-1]    
        else:
            self.str_profes = ", ".join(self.profes)

    def __str__(self):
        try:
            s = "<Seccion> "+self.nombre_profes
            if isinstance(s,str):
                return s
            return unidecode(s)
        except IndexError:
            return "<Seccion [Profes no disp.]>"

    def __repr__(self):
        return str(self)
    
class Curso(list):
    def __init__(self,L=[]):
        list.__init__(self,L)
        try:
            self.cod_y_curso = self[0]
            arr = self[0].split(' ')
            self.cod = arr[0]
            self.nombre = arr[1]
        except IndexError:
            self.cod_y_curso = "XX0000 [Curso vacio]"
            self.cod = "XX0000"
            self.nombre = "[Curso vacio]"
        

    def __str__(self):
        s = "<Curso> "+self.cod_y_curso
        if isinstance(s,str):
            return s
        return unidecode(s)
        
    def __repr__(self):
        return str(self)

    def setNombre(self):
        if len(self) > 0:
            self.cod_y_curso = self[0]
            arr = self[0].split(' ')
            self.cod = arr[0]
            self.nombre = arr[1]
            
class Depto(list):
    def __init__(self,L=[]):
        list.__init__(self,L)
        #self.name = 
        
class Catalogo(list):
    def __init__(self, semestre, L=[]):
        list.__init__(self,list())
        self.name = semestre

    def __str__(self):
        s = "<Catalogo "+self.name+">"
        if isinstance(s,str):
            return s
        return unidecode(s)

    def __repr__(self):
        return str(self)

class Hora:
    #Hora: str -> Hora
    def __init__(self,time):
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
        inicioA = self.ti.getHora()
        inicioB = x.ti.getHora()
        finA = self.tf.getHora()
        finB = x.tf.getHora()
        
        puntoA = max(inicioA, inicioB)
        puntoB = min(finA,finB)

        if puntoB*60.0 - puntoA*60.0 > margen and self.dia == x.dia:
            return True
        return False
   
class Curso(list):
    def __init__(self,L=[]):
        list.__init__(self,L)

    def __str__(self):
        try:
            return "<Curso> "+str(self[0])
        except IndexError:
            return "<Curso [Vacio]>"

    def __repr__(self):
        return str(self)

class Seccion(list):
    def __init__(self,L=[]):
        list.__init__(self,L)
        self.profes = self[0]
        self.cupo = self[1]
        if len(self.cupo) == 0: self.cupo = ""
        self.ocupados = self[2]
        if len(self.ocupados) == 0: self.ocupados = ""

    def __str__(self):
        try:
            return "<Curso> "+str(self[0])
        except IndexError:
            return "<Curso [Vacio]>"

    def __repr__(self):
        return str(self)


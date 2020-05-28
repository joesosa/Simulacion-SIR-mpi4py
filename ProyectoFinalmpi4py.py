# coding=utf-8

from mpi4py import MPI
import random
import numpy as np
import math
import matplotlib.pyplot as plt


class Persona:
    def __init__(self,id,tipoEdad,pos_f,pos_c,radio):
        ###def __init__(self,id,radio,velocidad,recuperacionP):
        self.id = id # identificar de la persona
        self.tipoEdad = tipoEdad
        self.pos_origenF = pos_f # esta posición y la siguiente definen el punto de origen
        self.pos_origenC = pos_c
        self.pos_actualF = pos_f
        self.pos_actualC = pos_c
        self.radio = radio
        random.seed(a=None) # base para generar numeros random consistentes
        # ver si esto se usa

    def getTipoEdad(self):
        return self.tipoEdad

    def editarPosF(self,valor,tam):
        nFila = self.pos_actualF + valor # nueva fila
        if nFila >= 0 and nFila < tam : # verifica que no se salga del "tablero"
            if ( nFila > (self.pos_origenF+self.radio) ) : ## verifica que no se salga del radio
                valor = valor - 2
            elif ( nFila < (self.pos_origenF-self.radio) ): # y si se sale
                valor = valor + 2
            self.pos_actualF = self.pos_actualF + valor

    def editarPosC(self,valor,tam):
        nColumna = self.pos_actualC + valor
        if nColumna >= 0 and nColumna < tam:
            if nColumna > (self.pos_origenC+self.radio):
                valor = valor - 2
            elif nColumna < (self.pos_origenC-self.radio):
                valor = valor + 2
            self.pos_actualC = self.pos_actualC + valor

    def getPosActualF(self):
        return self.pos_actualF

    def getPosActualC(self):
        return self.pos_actualC

    def getPosOrigenF(self):
        return self.pos_origenF

    def getPosOrigenC(self):
        return self.pos_origenC


def rellenarMap(map,m_infectadas,l_poblacion,v_infectadas,cant_infectadas,cpr,toc,poi,radio_jov,radio_may,m_mdf_infectadas): # mapa/diccionario de números que funcionan como id de personas
      # crea a las personas, las mete en una lista y coloca sus identificadores en un mapa
        # personas originalmente infectadas
        cant_jov = int(cpr * 0.9045) # calcula un numero de jóvenes
        tmm = math.floor(math.sqrt(cpr/toc))+1 # fórmula para calcular el tamaño de la matriz
        ##1: crea una lista N posiciones (f,c) al azar:
        lst_lcl_pos = [(random.randint(0,tmm),random.randint(0,tmm)) for i in range(cpr)]
	    ##2: crea un map con las posiciones como clave y una lista de indices como valor:
        for i in range(len(lst_lcl_pos)): # crea todos los objetos persona y los inserta en la lista de personas
            if (lst_lcl_pos[i] in map): # si el par ordenado ya está en el mapa
                map[lst_lcl_pos[i]].append(i) #  solo agrega el id al mapa
                if i < cant_jov: # si el indice/id de las personas corresponde al de los jovenes
                    f = [lst_lcl_pos[i][0]][0] # obtiene la fila de la posición
                    c = [lst_lcl_pos[i][1]][0] # obtiene la coulmna de la posición
                    persona = Persona(i,'j',f,c,radio_jov) # crea la personas con su id, su tipo de edad y que sepa su posicion origen
                    l_poblacion.append(persona) # inserta a la persona en la lista de objetos persona
                else: # si es mayor, lo agrega como mayor
                    f = [lst_lcl_pos[i][0]][0] # toma la fila de la llave (el primer elemento)
                    c = [lst_lcl_pos[i][1]][0] # toma la columna de la llave (el segundo elemento)
                    persona = Persona(i,'m',f,c,radio_may)
                    l_poblacion.append(persona)
            else:  #si no esta en el mapa, además de añadir a la persona, agrega el par ordenado
                map[lst_lcl_pos[i]] = [i] # agrega el par ordenado y el identidicador de la persona
                m_infectadas[lst_lcl_pos[i]] = 0
                m_mdf_infectadas[lst_lcl_pos[i]] = 0
                if i < cant_jov:
                    f = [lst_lcl_pos[i][0]][0]
                    c = [lst_lcl_pos[i][1]][0]
                    persona = Persona(i,'j',f,c,radio_jov)
                    l_poblacion.append(persona)
                else:
                    f = [lst_lcl_pos[i][0]][0]
                    c = [lst_lcl_pos[i][1]][0]
                    persona = Persona(i,'m',f,c,radio_may)
                    l_poblacion.append(persona)

	    ##3: crea una lista a partir del map:
	    #lista_map = list(map.items())
        for i in range(poi): # set de las personas originalmente infectadas
            pRand = random.randint(0,cpr-1) # cualquiera de la población puede ser infectado inial
            v_infectadas[pRand] = random.randrange(20,40) # se infecta una cantidad determinada de días
            cant_infectadas = cant_infectadas + 1 # aumentar contador de infectados totales
            p = l_poblacion[pRand]
            f = p.getPosActualF()
            c = p.getPosActualC()
            m_infectadas[(f,c)] = m_infectadas[(f,c)] + 1 # aumenta el contador de infectados en el mapa
            m_mdf_infectadas[(f,c)] = m_mdf_infectadas[(f,c)] + 1
        return cant_infectadas

"""...................................."""

def nuevoTic(pInd,uInd,l_poblacion,map,m_infectadas,v_muertas,v_infectadas,v_inmunes,cant_infectadas,cant_muertas,cant_resistentes,cpr,vel_joven,vel_mayor,prob_rec_jov,prob_rec_may,tam,pot_infec,dmn,dmx,m_mdf_infectadas):
      for id in range(pInd,uInd): # para mover todas las personas
        if v_muertas[id] !=1: # si la persona no está muerta
          moverPersona(id,l_poblacion,map,m_infectadas,v_infectadas,vel_joven,vel_mayor,tam,m_mdf_infectadas) # vamos a mover a todas las personas # moverPersona() -> nuevaPosEnMap
          if v_infectadas[id] > 0 : #si la persona está infectada
            cant_infectadas,cant_resistentes,cant_muertas = nuevoDiaInfectada(id,l_poblacion, map,m_infectadas,v_infectadas,v_muertas,v_inmunes,cant_infectadas,cant_muertas,cant_resistentes,cpr,prob_rec_jov,prob_rec_may,m_mdf_infectadas) # resta la cantidad de días restantes infectada y si es el último determina si gana inmunidad o muere
          elif v_inmunes[id] > 0: # si es inmune
            v_inmunes[id] = v_inmunes[id]-1
            if v_inmunes[id] == 1:
              cant_resistentes = cant_resistentes-1
        
        
      # una vez que se hicieron los cambios en el mapa, se simula la infección para cada persona 
      f = 0
      c = 0
      for id in range(pInd,uInd):
          if (v_muertas[id] !=1) and (v_infectadas[id] == 0) and (v_inmunes[id] == 0) : # si la persona es susceptible/sana
            # si la persona es suceptible
            # se intentará infectar la cantidad de veces que aprece en el contador de infectados
            f = l_poblacion[id].getPosActualF()
            c = l_poblacion[id].getPosActualC()
            cant_infect = m_infectadas[(f,c)] # devuelve el contador de infectados en la celda
            for i in range(cant_infect): # cantidad de personas infectadas en la celda # si es 0 no itera
              cant_infectadas = infectarme(id,l_poblacion,m_infectadas,v_infectadas,v_inmunes,pot_infec,dmn,dmx,cant_infectadas,m_mdf_infectadas)
              #nuevo dia susceptible
      
      return cant_infectadas,cant_resistentes,cant_muertas    
      # después de simular el día de infección, devuelve los resultados del tic, pero los resultados se pedirán afuera

"""...................................."""
def moverPersona(id,l_poblacion,map,m_infectadas,v_infectadas,vel_jov,vel_may,tam,m_mdf_infectadas): # radio es la cantidad de celdas que se puede mover
        # seleccionar la dirección de movimiento: arriba-abajo, izquierda-derecha y diagonales
        pers = l_poblacion[id]
        # por el toque del id, no hace falta obtener el tipo edad de la persona, pero aquí lo usaremos
        tipo_edad = l_poblacion[id].getTipoEdad()
        velocidad = vel_jov
        if tipo_edad == 'm':
          velocidad = vel_may

        aFila = pers.getPosActualF() # fila anterior
        aColumna = pers.getPosActualC() # columna anterior

        for i in range(velocidad): # velocidad es el número de celdas en las que se puede mover
          mr = random.randrange(8) # movimiento random, tiene 8 posibilidades (celdas que le rodean)
          if mr==0:
            pers.editarPosF(1,tam)
          elif mr==1:
            pers.editarPosF(-1,tam)
          elif mr==2:
            pers.editarPosC(1,tam)
          elif mr==3:
            pers.editarPosC(-1,tam)
          elif mr==4:
            pers.editarPosC(-1,tam)
            pers.editarPosF(-1,tam)
          elif mr==5:
            pers.editarPosC(1,tam)
            pers.editarPosF(1,tam)
          elif mr==6:
            pers.editarPosC(1,tam)
            pers.editarPosF(-1,tam)
          else:
            pers.editarPosC(-1,tam)
            pers.editarPosF(1,tam)
        nFila = pers.getPosActualF()
        nColumna = pers.getPosActualC()
        nuevaPosEnMap(id,aFila,aColumna,nFila,nColumna,map,m_infectadas,v_infectadas,m_mdf_infectadas) # establece la nueva coordenada (fila, columna) # cambia la dirección  de la persona en el diccionario

"""...................................."""
def nuevaPosEnMap(id,f1,c1,f2,c2,map,m_infectadas,v_infectadas,m_mdf_infectadas): # f1 y c1 pos actual -> f2 y c2 son las nuevas
        ## cambia la posición del identificador de la persona en el mapa
        # esto es para eliminar la persona de la posición anterior en el mapa
        
        if (f1,c1) in map: # verifica que esté la posición (par ordenado)
            if id in map[(f1,c1)]: # si el id de la persona está en la posición
                map[(f1,c1)].remove(id) # remueva el id
                if v_infectadas[id] > 0: # si está infectada
                    m_infectadas[(f1,c1)] = m_infectadas[(f1,c1)]-1 # disminuye el contador porque cambia de celda
                    m_mdf_infectadas[(f1,c1)] = m_mdf_infectadas[(f1,c1)]-1
                    
        if (f2,c2) in map: # si la nueva posición ya está en el mapa
            if id not in map[(f2,c2)]: # si el id no está en esa posición del mapa    
                map[(f2,c2)].append(id) # inserta a la personas
                if v_infectadas[id] > 0: # esta infectada
                    m_infectadas[(f2,c2)] = m_infectadas[(f2,c2)]+1 
                    m_mdf_infectadas[(f2,c2)] = m_mdf_infectadas[(f2,c2)]+1
                    
        else: # si la nueva posición no estaba
          map[(f2,c2)] = [id] # agrega el par ordenado y el id de la persona
          m_infectadas[(f2,c2)] = 0
          m_mdf_infectadas[(f2,c2)] = 0
          if v_infectadas[id] > 0: # esta infectada
            m_infectadas[(f2,c2)] = m_infectadas[(f2,c2)]+1  # aumenta el contador de infectados en la celda
            m_mdf_infectadas[(f2,c2)] = m_mdf_infectadas[(f2,c2)]+1
            


def nuevoDiaInfectada(id,l_poblacion, map,m_infectadas,v_infectadas,v_muertas,v_inmunes,cant_infectadas,cant_muertas,cant_resistentes,cpr,prob_rec_jov,prob_rec_may,m_mdf_infectadas): # le pasa el id para obtener su referencia en la lista de personas, se llama este método solo si la persona está infectada
        prob_rec = prob_rec_jov # hay más probabilidades de que sea joven
        if id >= int(cpr * 0.9045): # si es mayor. Por el orden de creación de personas, el id de 0 a esa cantidad son jovenes, pero si el id es más grande, la personas es mayor
            prob_rec = prob_rec_may # le asigna la probabilidad de recuperación del mayor
        # lo anterior es por si está en el último día de la enfermedad donde se determina si vive o muere
        v_infectadas[id] = v_infectadas[id] - 1 # un día menos de enfermedad
        # 
        if v_infectadas[id] == 1: # si es el último día, se ve si muere o adquiere inmunidad ciertos días
            cant_infectadas = cant_infectadas-1 # en este punto, el último día, la persona deja de estar infectada, muere o adquiere
            p = l_poblacion[id]
            f = p.getPosActualF()
            c = p.getPosActualC()
            m_infectadas[(f,c)] = m_infectadas[(f,c)] - 1
            m_mdf_infectadas[(f,c)] = m_mdf_infectadas[(f,c)] - 1
            
            #self.v_infectadas[id] = 0
            rr = random.random() # proceso de probabilidad para ver si muere o sobrevive
            if rr>prob_rec : # probabilidad de recuperación, si "recuperación random" excede la probabilidad, se muere  
                v_muertas[id] = 1
                cant_muertas = cant_muertas + 1
                # si la persona está muerta, se saca del mapa
                p = l_poblacion[id]
                f = p.getPosActualF()
                c = p.getPosActualC()
                if (f,c) in map: # verifica que esté la posición (par ordenado)
                  if id in map[(f,c)]: # si el id de la persona está en la posición
                    map[(f,c)].remove(id) # remueva el id
                
            else:
                r_inm = random.randrange(200,480) # rango de días posibles de inmunidad
                v_inmunes[id] = r_inm # días que será inmune
                cant_resistentes = cant_resistentes + 1

        return cant_infectadas,cant_resistentes,cant_muertas
          
def infectarme(id,l_poblacion,m_infectadas,v_infectadas,v_inmunes,pot_infec,dmn,dmx,cant_infectadas,m_mdf_infectadas): ## solo se invoca si la #persona es susceptible
#codigo de infectar antes de insertar
    #if (self.v_infectadas[id] == 0) and (self.v_inmunes[id]==0): # si la persona es susceptible
    if v_infectadas[id] == 0 and v_inmunes[id] == 0 : # si no está infectada y si no es inmune, verá si se infecta
      p = l_poblacion[id]
      f = p.getPosActualF()
      c = p.getPosActualC()
      cant_infect = m_infectadas[(f,c)]
      i = 0
      while ((v_infectadas[id]==0) and (i<cant_infect)) : # si la persona no se ha infectado y hay personas que la puedan infectar
        infectarP = random.random() # valor entre 0 y 1
        if infectarP < pot_infec : # si se infecta, depende de la potencia infecciosa del virus
          v_infectadas[id] = random.randrange(dmn,dmx) # se genera una cantidad determinada de días
          m_infectadas[(f,c)] = m_infectadas[(f,c)]+1 # esta persona se infectó, aumenta el contador de infectados
          m_mdf_infectadas[(f,c)] = m_mdf_infectadas[(f,c)]+1
          cant_infectadas = cant_infectadas + 1
        i = i + 1
    return cant_infectadas

def reductor_lsts_map(x, y):
      map_global = {}
      if (len(x) < len(y)):
        for i in range(len(y) - len(x)):
          x.append(())
      if (len(y) < len(x)):
        for i in range(len(x) - len(y)):
          y.append(())
      for a,b in zip(x,y):
        # agrega la lista de posiciones al map_global que vienen en x
        if (len(a)==2):
          if (a[0] in map_global):
            map_global[a[0]] = map_global[a[0]] + a[1]
          else:
            map_global[a[0]] = a[1]
      
        # agrega la lista de posiciones al map_global que vienen en y	
        if (len(b)==2):
          if (b[0] in map_global):
            map_global[b[0]] = map_global[b[0]] + b[1]
          else:
            map_global[b[0]] = b[1]	
      return list(map_global.items())

def main(): 
    comm = MPI.COMM_WORLD
    pid = comm.rank
    
    # el proceso maestro toma los paremtros
    if pid == 0:
        param = []
        with open('parametros.txt') as fin:
         
          for line in fin: # se va por cada línea, cada línea tiene un parámetro
              param.append(line)
        cpr = int(param[0])
        cont_pers = cpr // comm.size       # primera división de trabajo entre todos los procesos
        pers_restantes = cpr%comm.size         # guarda cuantos datos faltan por asignar (residuo)
        v_dist = np.full(comm.size, cont_pers, dtype=int) # contadores, cantidad de personas asignadas a cada proceso,  # distancia # incializamos con la primera división entre todos
        for i in range(pers_restantes): # asigna el último resto entre los procesos p1 en adelante.
            v_dist[i+1] = (v_dist[i+1]) + 1
        # si solo hay un proceso, ni siquiera entra aquí

        cont = 0
        # vectores con indices de inicio y final para cada proceso
        v_inic = np.zeros(comm.size, dtype=int)
        v_fin = np.zeros(comm.size, dtype=int)
        
        for j in range(len(v_dist)): # recore el vector con la distribución de personas por proceso para determinar donde inicia a trbajar y donde termina
            v_inic[j] = cont
            cont = cont + v_dist[j]
            v_fin[j] = v_inic[j]+v_dist[j]-1
        
    else: # los otros procesos preparan sus variables para recibirlas en el bcast
        v_inic = None
        v_fin = None
        param = None
        
    # el proceso 0 transmite las variables
    param = comm.bcast(param, root=0)
    v_inic = comm.bcast(v_inic, root=0)
    v_fin = comm.bcast(v_fin, root=0)
    inicio = v_inic[pid]
    fin = v_fin[pid]
    cpr = int(param[0])     # cantidad de población
    piv = float(param[1])   # probabilidad infecciosa del virus
    prj = float(param[2])   # probabilidad de recuperación de jovenes
    prm = float(param[3])   # probabilidad de recuperación de mayores
    poi = int(param[4])    # cantidad de personas originalmente infectada
    toc = float(param[5])   # tasa de ocupación para determinar el tamaño de la matriz
    dmn = int(param[6])     # duración mínima de la enfermedad
    dmx = int(param[7])     # duración máxima de la enfermedad
    rmj = int(param[8])     # radio de movilidad de jóvenes
    rmm = int(param[9])     # radio de movilidad de mayores
    vmj = int(param[10])    # velocidad de movilidad de jóvenes
    vmm = int(param[11])    # velocidad de movilidad de mayores
    dsd = int(param[12])
    tam = int(math.floor(math.sqrt(cpr/toc))+1)

    # el proceso 0 inicializa las estructuras necesaria para la simulación
    if pid == 0:
        map = {}
        m_infectadas = {}
        m_mdf_infectadas = {} # modificaciones locales del proceso al mapa de infectados por tic, cada tic se reinicia
        v_inmunes = np.zeros(cpr, dtype=int)
        v_muertas = np.zeros(cpr, dtype=int) 
        v_infectadas = np.zeros(cpr, dtype=int)
        l_poblacion = []
        cant_resistentes = 0
        cant_susceptibles = 0 
        cant_muertas = 0
        cant_infectadas = 0
        cant_infectadas = rellenarMap(map,m_infectadas,l_poblacion,v_infectadas,cant_infectadas,cpr,toc,poi,rmj,rmm,m_mdf_infectadas)
        # estos ultimos son para graficar
        v_cant_susceptibles = np.zeros(dsd, dtype=int)  # no inmunes y no infectadas
        v_cant_infectados = np.zeros(dsd,dtype=int)
        v_cant_resistentes = np.zeros(dsd,dtype=int)   #inmunes
        v_cant_muertos = np.zeros(dsd, dtype=int)
    else: # los otros procesos se preparan para el bcast
        map = None
        m_mdf_infectadas = None
        m_infectadas = None
        l_poblacion = None
        v_infectadas = np.empty(cpr, dtype=int)
        v_inmunes = np.empty(cpr, dtype=int)
        v_muertas = np.empty(cpr, dtype=int)
        cant_resistentes = 0
        cant_susceptibles = 0
        cant_muertas = 0
        cant_infectadas = 0
    #comunicación colectiva
    map = comm.bcast(map, root=0)
    m_infectadas = comm.bcast(m_infectadas, root=0)
    m_mdf_infectadas = comm.bcast(m_mdf_infectadas, root=0)
    l_poblacion = comm.bcast(l_poblacion, root=0)
    comm.Bcast(v_infectadas, root=0)
    comm.Bcast(v_inmunes, root=0)
    comm.Bcast(v_muertas, root=0)

    
    suma_infectadas = 0
    suma_resistentes = 0
    suma_muertas = 0
    suma_susceptibles = 0
    
    
   
    for dia in range(dsd): # ejecuta los tics indicados como la duración de la simulación
    # si el fin esta fallando, es +1
        # por proceso, por dia 
        # P0 por dia, infectados, resistentes, muertos y susceptibles
        cant_infectadas,cant_resistentes, cant_muertas = nuevoTic(inicio,fin+1,l_poblacion,map,m_infectadas,v_muertas,v_infectadas,v_inmunes,cant_infectadas,cant_muertas,cant_resistentes,cpr,vmj,vmm,prj,prm,tam,piv,dmn,dmx,m_mdf_infectadas)

        cant_susceptibles = (fin-inicio+1) - cant_infectadas - cant_resistentes - cant_muertas
        
        suma_infectadas = comm.reduce(cant_infectadas, op=MPI.SUM)
        suma_resistentes = comm.reduce(cant_resistentes, op=MPI.SUM)
        suma_muertas = comm.reduce(cant_muertas, op=MPI.SUM)
        suma_susceptibles = comm.reduce(cant_susceptibles, op=MPI.SUM)
        # reduce de una suma
        #pasar resultados por tic al proceso 0 
        #para insertarlos en el vector
        if pid == 0:
          v_cant_susceptibles[dia] = suma_susceptibles  # no inmunes y no infectadas
          v_cant_infectados[dia]= suma_infectadas
          v_cant_resistentes[dia] = suma_resistentes
          v_cant_muertos[dia] = suma_muertas

        lst_map_mdf = list(m_mdf_infectadas.items())
        lst_mdf_globales = comm.reduce(lst_map_mdf, op=reductor_lsts_map, root=0) #Reduce de los mapaa de modificaciones de todos los procesos

        if (pid == 0):
          lst_m_infectados = list(m_infectadas.items()) #  lista de todos los infectados        
          #Reduce de los mapaa de modificaciones de todos los procesos
          # Al mapa de estado general se suma y resta el mapa de modificaciones
          lst_m_infectados = reductor_lsts_map(lst_m_infectados, lst_mdf_globales)
          
          m_mdf_infectadas.clear()
          m_infectadas.clear() # vamos a actualizar el estado de la simulacion, borramos el mapa
          for par in lst_m_infectados:
              m_infectadas[par[0]] = par[1]
              m_mdf_infectadas[par[0]] = 0
  
        m_infectadas = comm.bcast(m_infectadas,root=0)
    
    if pid == 0:
        v_cant_dias = np.arange(1,dsd+1) # para graficar las listas, representa los días
        plt.title(u"Resultados de simulación")
        plt.xlabel(u"Dias")
        plt.ylabel(u"Personas")
        plt.plot(v_cant_dias,v_cant_susceptibles, label = u"Susceptibles")
        plt.plot(v_cant_dias,v_cant_infectados, label = u"Infectadas")
        plt.plot(v_cant_dias,v_cant_resistentes,label = u"Resistentes")
        plt.plot(v_cant_dias,v_cant_muertos, label = u"Muertas")
        plt.legend()
        plt.show()    
    
main()
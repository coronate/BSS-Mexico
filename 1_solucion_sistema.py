
"""
Para la primera parte de la solución se tomara un sistema y se intentara resolver siuiendo
"""
import itertools
import pandas as pd  
import numpy as np 
import random
import itertools
import sys

columnas = ['A', 'B', 'C', 'D']
S = pd.DataFrame( columns = columnas, index=  columnas)
for i in columnas:
    for j in columnas:
        if i == j:
            S.loc[i, j] = 'X'
        else:    
            S.loc[i, j] = np.random.randint(1, 10)
global NUM_ESTACIONES
global NUM_ESTADOS
NUM_ESTACIONES =  5
NUM_ESTADOS =  5


def mapaAleatorio( NUM_ESTACIONES, NUM_ESTADOS ): 
    #print("-------CREACION DE LISTA CON NOMBRES ESTACION---------")

    listaNombres = list()
    for i in range( NUM_ESTACIONES ): 
        nombre  =  "estacion_" +  str(i+1)
        listaNombres.append( nombre)
    #Matriz con columnas == numero de estaciones e index  ==  numero de estaciones

    estacionesMap = pd.DataFrame(  index=  listaNombres , columns= listaNombres )
    #print("-------CREACION DE MAPA ALEATORIO----------")

    for i in range( len( estacionesMap )):
        fila  = estacionesMap.index[i]
        for j in range( len( estacionesMap )):
                columna =  estacionesMap.columns[ j]
                if fila == columna:
                    estacionesMap.loc[ fila, columna ] = "X"
                else:
                    estacionesMap.loc[ fila, columna ] = random.randint( 1, NUM_ESTADOS ) 
    return estacionesMap




def getCode( S ):
    lista =  []
    for i in S.columns:
        for j in S.columns:
            lista.append(str(S.loc[i, j] ))
    return lista

"""
Es necesario crear unos diccionarios globales para poder insertar las soluciones y que puedan ser consultados en
cualquier scope del codigo.
SOLUCIONES

 L     SYSTEM        CODE 

[2]   [X][p1]   == [][][][] => CODE
      [p2][X]

[3]   [][][]    == [][][][][][][][][] => CODE
      [][][]
      [][][]

[4]   [][][][]  == [][][][][][][][][][][][][][][][] => CODE
      [][][][]
      [][][][]
      [][][][]
...

"""

global SOLUCIONES
SOLUCIONES = dict()

def getSolution( code ):
    """
    Return the solution of the system if the code of the system is saved in the dictionary.
    1. Look for the dictionary -> L
    2. If L is found the this dictionary have all the previous solved systems of length L
    3. Look for the code s of system S in L

    """ 
    global SOLUCIONES
    l = len(code)
    code = "".join(code)
    try:
        type(SOLUCIONES[l] )
        try:
            solution_sequence = SOLUCIONES[l][code]['sequence'] 
            solution_cost = SOLUCIONES[l][code]['cost'] 
            return solution_sequence, solution_cost
        except Exception as e:
            #print("No existe respuesta para code = {}".format(code))
            return False

    except Exception as e:
        #print( "No existe el nivel L = {} en el diccionario".format(l))
        SOLUCIONES[l] = dict()
        return False

def insertSolution(code, optimal_mov, min_cost, equivalent_systems):
    """
    Once we solve the system S we save the optimal transition route in SOLUCIONES
    in the L index.
    """
    global SOLUCIONES
    l = len(code)

    code_string = ''.join(code)
    #level = int(np.sqrt(l))
    #tab = "\t"
    #for i in range(level):
    #    tab = tab + "\t"
    #print("\n\n"+tab+"  --------Ingresando solucion sobre {}: => {} ------".format(l, code ))
    SOLUCIONES[l][code_string] = dict()
    SOLUCIONES[l][code_string]["cost"] = min_cost
    SOLUCIONES[l][code_string]["sequence"] = optimal_mov

    if equivalent_systems:
        #Generates all the possible equivalent systems given the code of a particular system.
        equivalentSystems = getEquivalentSystem(code)
        for equiCode in equivalentSystems:
            SOLUCIONES[l][equiCode]= dict()
            SOLUCIONES[l][equiCode]["cost"] = min_cost
            SOLUCIONES[l][equiCode]["sequence"] = optimal_mov    #TO DO: Exixten varios sistemas que son equivalentes. Es posible obtener todas las permutaciones
        #de las columnas para obtener los sistemas equivalentes.


def getEquivalentSystem(code):
    """
    Given a code of the system S this function return all the possible systems that have the same solution as S
    Example:

    [X][1][2]    == [X][1][2][3][X][4][5][6][X] => CODE
    [3][X][4]
    [5][6][X]

    [X][2][1]    == [X][2][1][5][X][6][3][4][X] => CODE
    [5][X][6]
    [3][4][X]
    """
    equivalentSystems = list()
    #first row and column are fixed beacause the starting poitn must be always the same
    ncol = int(np.sqrt(len(code)))
    S= np.matrix(code).reshape( ncol,ncol )
    S = pd.DataFrame(S)

    columnas = S.columns.drop(0)
    permutations = list(itertools.permutations(columnas, ncol-1))

    for per in permutations:
        newIndexOrder = list(per)
        newIndexOrder.insert(0,0)
        S_b = S.loc[newIndexOrder, newIndexOrder]
        equiCode = getCode(S_b)
        equivalentSystems.append( "".join(equiCode) )

    return equivalentSystems


def getSystem(S, movement_node):
    """
    Delete the first column and the first row in order to remove one node from the system

    [a,a][a,b][a,c][a,d]
    [b,a] [][][]
    [b,c] [][][]
    [b,d] [][][]

    After this transformMatrix reorder ht matrix so the movement_node is at the column 0, 
    row 0. 

    """
    starting_node = S.columns[0]
    columnsMinusA = list(S.columns)
    columnsMinusA.remove(starting_node)
    S_minusA = S[columnsMinusA]
    S_minusA = S_minusA.loc[columnsMinusA]

    s_minusA_start = S_minusA.columns[0]
    return transformMatrix( S_minusA, s_minusA_start, movement_node)


def get_SOLUCIONES_size():
    """
    Return the amount of solved and saved systems in SOLUCIONES
    """
    global SOLUCIONES
    levels_list = SOLUCIONES.keys()
    cuenta = 0 
    for level in levels_list:
        code_list = list(SOLUCIONES[level].keys())
        cuenta += len(code_list)
    return cuenta

def transformMatrix(S, a, b ):
    """
    [a][B][C][b] => [b][B][C][a]

       [a][B][C][b]               [b][B][C][a]                 [b][B][C][a] 

    [a]  [a,a] [] [a,b]         [a]  [a,b] [a,] [a,a]        [b]  [b,b] [b,] [b,a]
    [B]  [a]   [] [b]   =>   [B]  [b]   []   [a]    =>    [B]  [b]   []   [a]   
    [C]  [a]   [] [b]        [C]  [b]   []   [a]          [C]  [b]   []   [a]   
    [b]  [b,a] [] [b,b]      [b]  [b,b] [b,] [b,a]        [a]  [a,b] [a,] [a,a]


    """
    order =  list(S.columns)
    aPosition = order.index(a)
    bPosition = order.index(b)
    #Changing columns order
    order[bPosition] = a
    order[aPosition] = b
    #Changing rows order

    newMatrix = S[order]
    newMatrix = newMatrix.loc[order]

    return newMatrix


####################################################################################################################

def solveSystem(S, equivalent_systems, start_solutions = False):
    """
    Given a System S of NxN nodes. This function returns the optimal sequence of nodes that minimize the cost of 
    traveling through al the nodes.

    equivalent_systems: each time a system is solved this feature solve all the possible equivalent systems to be 
    solved using the same solution of the primary system. It just bassicaly calculate the equivalent systems
    ans assign the same solution in the SOLUCIONES dictionary.

    start_solutions: It solves and saves all the possible systems equal o lower to X = start_solutions.
    """
    global SOLUCIONES, NUM_ESTADOS, NUM_ESTACIONES

    if start_solutions:
        print("Start First level system generator")
        startSolutions( start_solutions, NUM_ESTADOS)
        start_solutions = False
        print("Complete generator")

    codeS        = getCode(S)           #GeneticCode that represent's the system [A, B, A D np.nan ... ]
    solutionS    = getSolution( codeS ) #False if system haven't been solved.
    starting_node = S.columns[0]         #
    nodesList    = list(S.columns)      # A, B , C , D
    movementList = dict()     # 0->NA,  1->B, 2->C, ... n->N

    #Print function so we ean diferenciate levels
    #level = len(S.columns)
    #tab = "\t"
    #for i in range(level):
    #    tab = tab + "\t"

    for i in range(len(nodesList)):
        if i != 0:
            movementList[ i ] =  nodesList[i]

    #print("\n\n Evaluando el Sistema:\n\n {} \n\n CODIGO {} ".format(S, codeS))

    if solutionS:
        optimal_mov = solutionS[0]
        min_cost = solutionS[1]
        return optimal_mov, min_cost

    else: #No existe solucion guaradda para code en SOLUCIONES
        if len( codeS ) <= 4: #El codigo corresponde a una matriz de 2X2 y solo hay una opciond e moviento
            #print("\n" + tab + "***Se ha llegado al minimo sistema***")
            optimal_mov =[ [0,1]  ]
            movement_node = movementList[1]
            min_cost = S.loc[starting_node, movement_node]
            #print(optimal_mov)

        else:
            min_cost = 10000000
            #print(movementList.keys())
            for mov in movementList.keys():
                movement_node = movementList[mov]
                #print("\n" +tab+ "Moviendo camion de {}  a {} ".format( starting_node, movement_node))
                #list(itertools.permutations([1, 2, 3]))
                mov_cost  = S.loc[starting_node, movement_node]

                #Delete the starting node and transform the system so movement_node -> starting_node
                SminiusMov = getSystem( S, movement_node)
                SminiusMov_movements, SminiusMov_cost= solveSystem(SminiusMov, equivalent_systems)
                #print(SminiusMov_movements)

                total_cost = mov_cost + SminiusMov_cost

                #print("\n" +tab+ "Ruta evaluda: mov_cost {} total_cost {} ".format( mov_cost, total_cost))

                if total_cost < min_cost:
                    min_cost    = total_cost
                    optimal_mov = SminiusMov_movements +  [[0,mov]]
                    #print( "\n"+tab+"NUEVO MINIMO: {}   =>  {} xxxx {} ".format(min_cost, optimal_mov, SminiusMov_movements) )

        insertSolution( codeS, optimal_mov, min_cost, equivalent_systems)
        return optimal_mov, min_cost




def startSolutions(  level_top, num_estados ):
    """
    This funtion insert in the SOLUCIONES dictionary the solution for all possible
    Systems of level_top, solving firts all the problems for level_top-1.
    """
    global SOLUCIONES

    level = int(np.sqrt(level_top))
    #print("LEVEL: {}".format(level))
    if( level_top != 4):   
        S = mapaAleatorio(level,level)
        previousLevel = np.power( level-1, 2)
        startSolutions(  previousLevel, num_estados) #es mas facil si resolvemos primero los niveles mas bajos.
    combinationsCode = list(itertools.combinations_with_replacement( range(1, num_estados ), level_top-level))
    #print("SYSTEM: {}  => {}".format(level, combinationsCode))

    for elements in combinationsCode:
        cont  = 0 
        S = mapaAleatorio(level,level)

        for i in range(level):
            i_name = "estacion_" + str(i+1)
            for j in range(level):
                j_name = "estacion_" + str(j+1)
                if i ==j :
                    S.loc[i_name,j_name] = "X"
                else:
                    S.loc[i_name,j_name] = elements[cont]
                    cont += 1
        #print("Elements: {} \n\tS: {}".format(elements, S))
        solveSystem(S, equivalent_systems = True)
    tamano = sys.getsizeof(SOLUCIONES)
    print("Dictionary Size: {} \n\t {}".format( tamano , list(SOLUCIONES.keys()) ))


def solveSystem_bruteForce(S):
    """
    Given a System S of NxN nodes. This function returns the optimal sequence of nodes that minimize the cost of 
    traveling through al the nodes using a brute force algorithm.
    """

    global SOLUCIONES
    codeS        = getCode(S)           #GeneticCode that represent's the system [A, B, A D np.nan ... ]
    starting_node = S.columns[0]         #
    nodesList    = list(S.columns)      # A, B , C , D
    movementList = dict()     # 0->NA,  1->B, 2->C, ... n->N

    #Print function so we ean diferenciate levels
    #level = len(S.columns)
    #tab = "\t"
    #for i in range(level):
    #    tab = tab + "\t"

    for i in range(len(nodesList)):
        if i != 0:
            movementList[ i ] =  nodesList[i]
    #print("\n\n Evaluando el Sistema:\n\n {} \n\n CODIGO {} ".format(S, codeS))


    if len( codeS ) <= 4: #El codigo corresponde a una matriz de 2X2 y solo hay una opciond e moviento
        #print("\n" + tab + "***Se ha llegado al minimo sistema***")
        optimal_mov =[ [0,1]  ]
        movement_node = movementList[1]
        min_cost = S.loc[starting_node, movement_node]
        #print(optimal_mov)

    else:
        min_cost = 10000000
        for mov in movementList.keys():
            movement_node = movementList[mov]
            #print("\n" +tab+ "Moviendo camion de {}  a {} ".format( starting_node, movement_node))
            #list(itertools.permutations([1, 2, 3]))
            mov_cost  = S.loc[starting_node, movement_node]

            #Delete the starting node and transform the system so movement_node -> starting_node
            SminiusMov = getSystem( S, movement_node)
            SminiusMov_movements, SminiusMov_cost= solveSystem_bruteForce(SminiusMov)
            total_cost = mov_cost + SminiusMov_cost

            #print("\n" +tab+ "Ruta evaluda: mov_cost {} total_cost {} ".format( mov_cost, total_cost))

            if total_cost < min_cost:
                min_cost    = total_cost
                optimal_mov = SminiusMov_movements +  [[0,mov]]
                #print( "\n"+tab+"NUEVO MINIMO: {}   =>  {} xxxx {} ".format(min_cost, optimal_mov, SminiusMov_movements) )

        #memory = False
        #insertSolution( codeS, optimal_mov, min_cost, memory)
        return optimal_mov, min_cost



S = mapaAleatorio( NUM_ESTACIONES,NUM_ESTADOS )
code = getCode(S)

seq, cost =  solveSystem(S, equivalent_systems =True, start_solutions = 9 )
#seq, cost =  solveSystem(S, equivalent_systems =False, start_solutions = False )
#seq, cost =  solveSystem(S, equivalent_systems =True, start_solutions = False )

print(get_SOLUCIONES_size())




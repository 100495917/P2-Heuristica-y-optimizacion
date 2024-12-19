# -*- coding: utf-8 -*-

import heapq
import sys
from collections import deque
import time
from itertools import product

# Variables globales (se llenarán al leer el mapa)
goals = []
mapa = []
# Usamos sets para las celdas porque permite operaciones de búsqueda rápidas para verificar si una celda pertence al conjunto
Mgris = set()
Mamarillo = set()
Mtransitable = set()

# Variables para estadísticas
nodos_expandidos = 0

########### FUNCIONES PARA LEER EL INPUT MAPA ############

def leer_mapa(path_mapa):
    '''
    Lee el archivo del mapa y genera las estructuras de datos necesarias.
    '''
    global goals, mapa, Mgris, Mamarillo, Mtransitable

    # Abrir el fichero
    with open(path_mapa, 'r') as f:
        # Leer todas las líneas, eliminando espacios en blanco al inicio y al final
        # y filtrando las líneas vacías
        lines = [l.strip() for l in f if l.strip()]

    # La primera línea del fichero indica el número de aviones 'n'
    n = int(lines[0].strip())

    # Inicializamos listas para almacenar las posiciones iniciales y las metas de cada avión
    aviones_init = []
    aviones_goal = []

    # A continuación, las siguientes 'n' líneas contienen, para cada avión, dos pares de coordenadas:
    # la posición inicial y la posición objetivo.
    # Formato de cada línea: "(x_init,y_init) (x_goal,y_goal)"
    for i in range(1, n+1):
        linea = lines[i]

        # Dividir la línea por espacios. Debería haber dos partes: la posición inicial y la meta.
        parts = linea.split()

        # Eliminar los paréntesis de las cadenas correspondientes a las posiciones
        init_str = parts[0].strip("()")
        goal_str = parts[1].strip("()")

        # Separar las coordenadas por coma y convertirlas a enteros
        x_init, y_init = map(int, init_str.split(','))
        x_goal, y_goal = map(int, goal_str.split(','))

        # Añadir las posiciones iniciales y finales a las listas
        aviones_init.append((x_init, y_init))
        aviones_goal.append((x_goal, y_goal))


    # Validar que las posiciones iniciales y las metas no se repiten
    validar_posiciones(aviones_init, aviones_goal)

    # A partir de la línea n+1, se define la matriz del mapa. Cada línea del mapa contiene
    # una fila, con las celdas separadas por punto y coma ';'.
    mapa_lines = lines[n+1:]
    if len(mapa_lines) == 0:
        raise ValueError("El mapa no contiene filas.")

    # Leer el mapa línea a línea, separando las celdas por ';' y añadiéndolas a 'mapa'
    # Validar dimensiones consistentes
    num_columnas = None
    for row_i, l in enumerate(mapa_lines):
        row = l.split(';')
        if num_columnas is None:
            num_columnas = len(row)
        elif len(row) != num_columnas:
            raise ValueError(f"Todas las filas del mapa deben tener el mismo número de columnas. "
                             f"La fila {row_i + 1} tiene {len(row)} columnas en lugar de {num_columnas}.")
        mapa.append(row)

    # Ahora que el mapa está cargado, debemos identificar las celdas grises (G), amarillas (A)
    # y calcular el conjunto de celdas transitables (todas menos las grises).
    # (x, y): x es la fila (índice de la fila), e y es la columna (índice dentro de la fila).
    for x, fila in enumerate(mapa):
        for y, c in enumerate(fila):
            # Si la celda es 'G' (gris), es intransitable:
            if c == 'G':
                Mgris.add((x,y))
            # Si la celda es 'A' (amarilla), se puede transitar sin parar
            elif c == 'A':
                Mamarillo.add((x,y))
            # Todas las celdas que no sean 'G' son transitables (incluye blancas y amarillas)
            if c != 'G':
                Mtransitable.add((x,y))

        # Validar que las posiciones iniciales y metas están dentro del rango del mapa
        max_filas = len(mapa)
        max_columnas = len(mapa[0])
        for x, y in aviones_init + aviones_goal:
            if not (0 <= x < max_filas and 0 <= y < max_columnas):
                raise ValueError(f"Posición ({x}, {y}) está fuera del rango del mapa: "
                                 f"0 <= x < {max_filas}, 0 <= y < {max_columnas}.")

    # Imprimir el mapa para comprobar que se ha leído correctamente
    #imprimir_mapa(mapa, aviones_init, aviones_goal)

    # Devolvemos una tupla con las posiciones iniciales de todos los aviones,
    # la lista de metas de todos ellos, y el número de aviones.
    return tuple(aviones_init), aviones_goal, n

def validar_posiciones(aviones_init, aviones_goal):
    """
    Valida los parámetros de entrada verificando que dos o más aviones no tengan la misma posicion inicial
    ni la misma meta
    """
    if len(set(aviones_init)) != len(aviones_init):
        raise ValueError("Entrada inválida. Dos o más aviones tienen la misma posición inicial.")
    if len(set(aviones_goal)) != len(aviones_goal):
        raise ValueError("Entrada inválida. Dos o más aviones tienen la misma posición objetivo.")


################# ALGORITMO A STAR ######################
def a_star(inicial):
    # Para guardar las estadísticas necesitamos nodos_expandidos
    global nodos_expandidos
    # ABIERTA se implementa como una cola de prioridad (min-heap) sobre f(n)
    # Cada elemento en ABIERTA es una tupla (f, g, estado, antecesor, accion)
    ABIERTA = []
    # CERRADA es un conjunto de estados ya explorados
    CERRADA = set()

    # Para reconstruir el camino, guardamos de dónde venimos y qué acción se tomó
    # came_from[estado] = (estado_anterior, accion)
    came_from = {}

    # cost_so_far[estado] = g(estado)
    cost_so_far = {}

    g_inicial = 0
    f_inicial = g_inicial + heuristica(inicial)

    heapq.heappush(ABIERTA, (f_inicial, g_inicial, inicial, None, None))

    # Insertamos valor del nodo inicial en el diccionario de predecesores (padre, accion)
    came_from[inicial] = (None, None)

    # Insertamos coste inicial en el diccionario de costes
    cost_so_far[inicial] = g_inicial

    # Inicializamos variable de control y solución
    EXITO = False
    solucion = None

    # Hasta que ABIERTA está vacía o EXITO
    while ABIERTA and not EXITO:
        #imprimir_abierta(ABIERTA)

        # Quitar el primer nodo de ABIERA
        f_actual, g_actual, actual, padre, accion = heapq.heappop(ABIERTA)

        # Cada vez que sacamos un nodo de ABIERTA lo estamos expandiendo
        nodos_expandidos += 1

        #print("Nodo que estamos expandiendo:")
        #imprimir_nodo(f_actual, g_actual, actual, padre, accion)

        # SI N es Estado-final ENTONCES EXITO=Verdadero
        if es_estado_final(actual):
            EXITO = True
            solucion = reconstruir_camino(came_from, actual)
            break

        # SI NO, Expandir N y meterlo en CERRADA
        CERRADA.add(actual)
        #imprimir_cerrada(CERRADA)
        # sucesores(actual) expande N y genera el conjunto S de sucesores de N
        # Para cada sucesor s en S :
        for accion_s, sucesor, coste_accion in sucesores(actual):
            # Calculamos nuevo coste del sucesor
            # g(nuevo) = g(actual) + coste_accion
            nuevo_coste = g_actual + coste_accion

            # Reglas de inserción y actualización en ABIERTA
            # 1. Si sucesor no está en ABIERTA ni en CERRADA
            # 2. Si está en ABIERTA pero f(nuevo) es mejor
            # 3. Si está en CERRADA se ignora
            if sucesor in CERRADA:
                # Caso 3: está en CERRADA, se ignora
                continue

            # Si no está en cost_so_far (equivalente a no estar ni en ABIERTA ni CERRADA) o encontramos un camino mejor
            if sucesor not in cost_so_far or nuevo_coste < cost_so_far[sucesor]:
                cost_so_far[sucesor] = nuevo_coste
                h_sucesor = heuristica(sucesor)
                f_sucesor = nuevo_coste + h_sucesor

                #print("Sucesor que estamos generando:")
                #imprimir_nodo(f_sucesor, nuevo_coste, sucesor, actual, accion_s)

                # Caso 1: sucesor no estaba en ABIERTA ni CERRADA
                # o caso 2: estaba en ABIERTA pero encontramos f mejor
                # En heapq no es trivial eliminar, así que se insertará de nuevo con el coste mejor
                # y el anterior quedará obsoleto.
                heapq.heappush(ABIERTA, (f_sucesor, nuevo_coste, sucesor, actual, accion_s))
                came_from[sucesor] = (actual, accion_s)

    if EXITO:
        return solucion
    else:
        return None

def es_estado_final(nodo):
    # nodo: ((x1,y1),(x2,y2),...)
    # goals: [(gx1, gy1), (gx2, gy2), ...]
    for (x,y),(gx,gy) in zip(nodo, goals):
        if (x,y) != (gx,gy):
            return False
    return True


################ HEURÍSTICAS #################

# Tenemos una lista de metas global llamada 'goals'
# goals = [(gx1, gy1), (gx2, gy2), ..., (gxN, gyN)]

def heuristica_max_manhattan(nodo):
    '''
    Para cada avión ai calculamos la distancia Manhattan entre su posición actual y su pos objetivo
    Tomamos como heurística el máximo de las distancias Manhattan de los aviones
    '''
    # nodo es una tupla ((x1,y1), (x2,y2), ..., (xN,yN))
    distancias = []
    for (x, y), (gx, gy) in zip(nodo, goals):
        # Distancia Manhattan para este avión
        man_dist = abs(x - gx) + abs(y - gy)
        distancias.append(man_dist)

    # Heurística = máximo de estas distancias
    return max(distancias)

def precalcular_distancias_BFS(aviones_goal):
    """
    Función auxiliar para la heurística que consiste en precalcular las distancias mínimas
    desde cualquier celda del mapa hasta la meta de cada avión, ignorando la presencia de otro aviones,
    pero teniendo en cuenta las celdas grises
    """
    global distancias_por_avion
    distancias_por_avion = []

    # Para cada meta de avión, precalculamos distancias desde la meta a las demás celdas
    for avion_idx, (gx, gy) in enumerate(aviones_goal):
        dist = {}
        # BFS
        cola = deque()
        # Si la meta es transitable, inicializamos con dist=0 para cada meta del avión
        if (gx, gy) in Mtransitable:
            cola.append((gx, gy, 0))
            dist[(gx, gy)] = 0

        else:
            # Si la meta es no transitable, no se puede llegar a ella
            # Asignar distancias infinitas
            #print(f"[DEBUG] La meta ({gx}, {gy}) no es transitable. Todas las distancias serán ∞.")
            for (cx, cy) in Mtransitable:
                dist[(cx, cy)] = float('inf')
            distancias_por_avion.append(dist)
            continue

        while cola:
            # cada elemento de la cola es una tupla (x,y,d)
            x, y, d = cola.popleft()
            # Operadores válidos (derecha, izquierda, abajo y arriba)
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                # Se calcula la celda vecina para cada dirección
                nx, ny = x+dx, y+dy
                # la celda nueva tiene que ser transitable y no haberse calculado previamente
                if (nx, ny) in Mtransitable and (nx, ny) not in dist:
                    # Se incrementa la distancia en un paso
                    dist[(nx, ny)] = d+1
                    # Añadimos la celda a la cola con la nueva distancia
                    cola.append((nx, ny, d+1))

        # Para asegurar que todas las celdas del mapa tienen un valor asignado,
        # incluso si no son alcanzables:
        # Las celdas inaccesibles se marcan con infinito
        for (cx, cy) in Mtransitable:
            if (cx, cy) not in dist:
                dist[(cx, cy)] = float('inf')

        distancias_por_avion.append(dist)


def heuristica_distancias_minimas(nodo):
    '''
    Esta heurística consiste en precalcular, para cada avión, la distancia mínima desde cualquier celda del mapa
    hasta la meta de ese avión, ignorando la presencia de otros aviones y las restricciones dinámicas,
    pero teniendo en cuenta las celdas grises.
    Al evaluar un estado, la heurística toma el máximo de estas distancias precalculadas entre todos los aviones,
    garantizando así la admisibilidad.
    '''

    # nodo: ((x1,y1),(x2,y2),..., (xN,yN))
    # Para cada avión i, obtener dist[nodo[i]] y tomar el máx
    dist_list = []
    for i, (x,y) in enumerate(nodo):
        dist_i = distancias_por_avion[i].get((x,y), float('inf'))
        dist_list.append(dist_i)
    return max(dist_list)

def heuristica(nodo):
    if num_h == 1:
        return heuristica_max_manhattan(nodo)
    elif num_h==2:
        return heuristica_distancias_minimas(nodo)


def reconstruir_camino(came_from, estado_final):
    """
    Reconstruye el camino de acciones desde el estado inicial hasta estado_final.
    """
    acciones = []
    current = estado_final
    while came_from[current][0] is not None:
        padre, accion = came_from[current]
        acciones.append(accion)
        current = padre
    acciones.reverse()
    return acciones


############# FUNCIONES PARA GENERAR LOS SUCESORES, ASEGURANDO LAS PRECONDICIONES ##############
def sucesores(estado):
    # estado: ((x1,y1),(x2,y2),...)
    # Aplicamos los operadores posibles para cada avión
    # Operadores: (0,0)=wait, (-1,0)=up, (1,0)=down, (0,-1)=left, (0,1)=right
    # Combinaremos los operadores de todos los aviones y filtramos las combinaciones inválidas

    movimientos = [(0,0),(0,-1),(0,1),(-1,0),(1,0)]
    opciones_por_avion = []

    # Para cada avión, determinar los operadores válidos
    for (x, y) in estado:
        acciones_avion = []
        for (dx, dy) in movimientos:
            if dx == 0 and dy == 0:
                # Operador: wait
                if es_espera_valida(x, y):
                    acciones_avion.append((dx,dy))
            else:
                # Operador de movimiento
                if es_movimiento_valido(x, y, dx, dy):
                    acciones_avion.append((dx,dy))
        opciones_por_avion.append(acciones_avion)

    sucesores_list = []

    # Generar todas las combinaciones de acciones (cartesiano de opciones_por_avion, todos con todos)
    for comb in product(*opciones_por_avion):
        # Generar el nuevo estado aplicando las acciones de comb
        nuevo_estado = tuple((x+dx, y+dy) for (x,y),(dx,dy) in zip(estado, comb))

        # Verificar restricciones globales
        # 1. No colisiones
        if not no_hay_colisiones(nuevo_estado):
            continue

        # 2. No intercambio de posiciones
        if not no_hay_intercambio(estado, nuevo_estado):
            continue

        # Si se cumplen las condiciones, agregamos el sucesor
        # Coste por transición = 1
        sucesores_list.append((comb, nuevo_estado, 1))

    return sucesores_list


def es_espera_valida(x, y):
    """
    Función auxiliar para sucesores.
    Verifica si esperar en la celda (x,y) es válido.
    - No se puede esperar en celdas amarillas.
    - La celda debe ser transitable (esto se asume por estar en el estado actual).
    """
    if (x,y) in Mamarillo:
        return False
    # Si no es amarilla ni gris, asumimos que es blanca y por tanto se puede esperar.
    return True

def es_movimiento_valido(x, y, dx, dy):
    """
    Verifica si el movimiento (dx,dy) desde (x,y) es válido.
    La celda destino (x+dx, y+dy) debe ser transitable.
    """
    nx, ny = x+dx, y+dy
    if (nx, ny) not in Mtransitable:
        return False
    return True

def no_hay_colisiones(nuevo_estado):
    """
    Verifica que en el nuevo estado no haya colisiones:
    Ninguna celda debe estar ocupada por más de un avión.
    """
    return len(set(nuevo_estado)) == len(nuevo_estado)

def no_hay_intercambio(estado_anterior, nuevo_estado):
    """
    Verifica que no se produzca el intercambio de posiciones entre dos aviones adyacentes:
    Si PosAv(a_i,t)=p_i y PosAv(a_j,t)=p_j:
    No puede ser que PosAv(a_i,t+1)=p_j y PosAv(a_j,t+1)=p_i.
    """
    for i in range(len(estado_anterior)):
        for j in range(i+1, len(estado_anterior)):
            # Si el avión i termina en la posición anterior del avión j
            # y el avión j termina en la posición anterior del avión i
            # se produjo un intercambio.
            if estado_anterior[i] == nuevo_estado[j] and estado_anterior[j] == nuevo_estado[i]:
                return False
    return True


############### FUNCIONES AUXILIARES DE DEPURACIÓN QUE IMPRIMEN EN LA SALIDA ESTÁNDAR ################
# Hemos comentado las llamadas a estas funciones en el código ya que aumentan el tiempo de ejecución, pero se pueden usar para depurar

def imprimir_mapa(mapa, aviones_init, aviones_goal):
    """
    Función auxiliar para imprimir el mapa leído de forma visual
    """
    print("Mapa leído:")
    for fila in mapa:
        print(" ".join(fila))


def imprimir_abierta(abierta):
    """
    Imprime el contenido de la lista ABIERTA de forma legible
    abierta: Lista de tuplas en el formato (f, g, estado, padre, accion).
    """
    print("\nContenido de ABIERTA:")
    if not abierta:
        print("  [VACÍA]")
    for i, (f, g, estado, padre, accion) in enumerate(abierta):
        print(f"  Nodo {i + 1}:")
        print(f"    f = {f}, g = {g}")
        print(f"    Estado: {estado}")
        print(f"    Padre: {padre}")
        print(f"    Acción: {accion}")
    print("-" * 50)


def imprimir_cerrada(cerrada):
    """
    Imprime el contenido del conjunto CERRADA de manera legible
    """
    print("\nContenido de CERRADA (total: {} nodos):".format(len(cerrada)))
    for i, estado in enumerate(cerrada):
        print(f"  Nodo {i+1}: {estado}")
    print("-" * 50)

def imprimir_nodo(f, g, estado, padre, accion):
    """
    Imprime información detallada de un nodo en el algoritmo A*.
    - f: valor de la función f(n) = g(n) + h(n)
    - g: coste acumulado hasta el nodo actual
    - estado: posiciones actuales de los aviones
    - padre: estado del nodo padre
    - accion: acción que llevó al estado actual
    """
    print("Nodo actual:")
    print(f"  f(n): {f}")
    print(f"  g(n): {g}")
    print(f"  Estado actual: {estado}")
    if padre:
        print(f"  Nodo padre: {padre}")
    else:
        print("  Nodo padre: None (nodo inicial)")
    if accion:
        print(f"  Acción aplicada: {accion}")
    else:
        print("  Acción aplicada: None (nodo inicial)")
    print("-" * 50)


############ FUNCIONES PARA GUARDAR LA SOLUCIÓN ################

def movimiento_a_simbolo(dx, dy):
    if dx == 0 and dy == 0:
        return "w"
    elif dx == 0 and dy == 1:
        return "→"
    elif dx == 0 and dy == -1:
        return "←"
    elif dx == 1 and dy == 0:
        return "↓"
    elif dx == -1 and dy == 0:
        return "↑"
    else:
        # No debería darse un caso distinto
        return "?"

def reconstruir_estados(inicial, plan):
    """
    Dado el estado inicial y la secuencia de acciones (plan),
    reconstruye la lista de estados desde el inicial hasta el final.
    plan es una lista de acciones, cada acción es una tupla ((dx1,dy1),(dx2,dy2),...))
    """
    estados = [inicial]
    estado_actual = inicial
    for accion in plan:
        nuevo_estado = tuple((x+dx, y+dy) for ((x,y),(dx,dy)) in zip(estado_actual, accion))
        estados.append(nuevo_estado)
        estado_actual = nuevo_estado
    return estados

def guardar_solucion(path_mapa, num_h, inicial, plan):
    # Obtener el nombre base del mapa
    import os
    nombre_mapa = os.path.splitext(os.path.basename(path_mapa))[0]

    # Nombre del fichero de salida
    output_file = f"./ASTAR-tests/{nombre_mapa}-{num_h}.output"

    with open(output_file, "w") as f:
        if plan is None:
            # Si no hay solución, guardar el mensaje correspondiente
            f.write("El problema no tiene solución\n")
        else:
            # Reconstruir los estados desde inicial a final
            estados = reconstruir_estados(inicial, plan)

            # Crear el contenido para cada avión
            n_aviones = len(estados[0])
            lineas_aviones = []

            for avion_idx in range(n_aviones):
                # Extraer las posiciones del avión actual a lo largo de todos los estados
                posiciones = [estado[avion_idx] for estado in estados]

                # Construir la línea del avión
                # Formato: (x_final,y_final) <mov> (x_anterior,y_anterior) <mov> ...
                # Donde <mov> se deduce del cambio de coordenadas entre posiciones consecutivas
                linea = []
                # Agregar la primera posición (final)
                linea.append(f"({posiciones[0][0]},{posiciones[0][1]})")

                # Recorrer las posiciones consecutivas y determinar el movimiento
                for i in range(len(posiciones) - 1):
                    x_act, y_act = posiciones[i]
                    x_ant, y_ant = posiciones[i + 1]
                    dx = x_ant - x_act
                    dy = y_ant - y_act
                    simbolo = movimiento_a_simbolo(dx, dy)
                    linea.append(simbolo)
                    linea.append(f"({x_ant},{y_ant})")

                lineas_aviones.append(" ".join(linea))

            # Escribir todas las líneas de solución en el archivo
            for linea in lineas_aviones:
                f.write(linea + "\n")

    print(f"Archivo solución guardado en: {output_file}")

##################### FUNCIÓN PARA GUARDAR LAS ESTADÍSTICAS ##################

def guardar_estadisticas(path_mapa, num_h, tiempo_total, plan, h_inicial, nodos_expandidos):
    import os
    nombre_mapa = os.path.splitext(os.path.basename(path_mapa))[0]
    output_stat_file = f"./ASTAR-tests/{nombre_mapa}-{num_h}.stat"

    # tiempo_total en segundos (float)
    # makespan es la longitud del plan = número de pasos
    makespan = len(plan) if plan is not None else 0

    with open(output_stat_file, "w") as f:
        f.write(f"Tiempo total: {tiempo_total:.2f}s\n")
        f.write(f"Makespan: {makespan}\n")
        f.write(f"h inicial: {h_inicial}\n")
        f.write(f"Nodos expandidos: {nodos_expandidos}\n")

    #print(f"Estadísticas guardadas en: {output_stat_file}")


################## MAIN DEL PROGRAMA ######################

def main():
    global goals, num_h
    # Comprobamos número de argumentos válido
    if len(sys.argv) != 3:
        print("Uso: python ASTARRodaje.py <path_mapa.csv> <num-h>")
        sys.exit(1)

    # Ruta al mapa
    path_m = sys.argv[1]

    # Validamos num_h
    try:
        num_h = int(sys.argv[2])
        if num_h not in [1,2]:
            raise ValueError("Heurística no válida.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Extraemos posiciones iniciales y posiciones objetivo
    inicial, goals_list, n = leer_mapa(path_m)
    goals = goals_list

    # Precomputar distancias si num_h = 2
    if num_h == 2:
        precalcular_distancias_BFS(goals)

    # Calcular heurística inicial para las estadísticas
    h_inicial = heuristica(inicial)

    # Inicializar tiempo
    inicio_tiempo = time.time()

    # Ejecutar A*
    plan = a_star(inicial)

    # Finalizar tiempo
    fin_tiempo = time.time()
    tiempo_total = fin_tiempo - inicio_tiempo

    # Guardar la solución en el fichero <mapa>-<num-h>.output
    guardar_solucion(path_m, num_h, inicial, plan)

    if plan is not None:
        # Guardar estadísticas
        guardar_estadisticas(path_m, num_h, tiempo_total, plan, h_inicial, nodos_expandidos)



if __name__ == "__main__":
    main()

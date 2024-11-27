#!/usr/bin/env python
#-*- coding: utf-8 -*-

import constraint


FRANJAS = 4;

class Avion:
    """Clase para representar un avión en una franja de tiempo específica"""
    def __init__(self, id: int, tipo: str, restr: bool, t1: int, t2: int, franja: int):
        self._id = None
        self._tipo = None
        self._restr = restr
        self._t1 = None
        self._t2 = None
        self._franja = None

        self.id = id  # Setter valida
        self.tipo = tipo  # Setter valida
        self.t1 = t1  # Setter valida
        self.t2 = t2  # Setter valida
        self.franja = franja # Setter valida

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("id must be a positive nonzero integer.")
        self._id = value

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if value not in {"JMB", "STD"}:
            raise ValueError('tipo must be either "JMB" or "STD".')
        self._tipo = value

    @property
    def restr(self):
        return self._restr

    @restr.setter
    def restr(self, value):
        if not isinstance(value, bool):
            raise ValueError("restr must be a boolean.")
        self._restr = value

    @property
    def t1(self):
        return self._t1

    @t1.setter
    def t1(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("t1 must be a positive integer (or zero).")
        self._t1 = value

    @property
    def t2(self):
        return self._t2

    @t2.setter
    def t2(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("t2 must be a positive integer (or zero).")
        self._t2 = value

    @property
    def franja(self):
        return self._franja

    @franja.setter
    def franja(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("franja must be a positive integer (or zero).")
        self._franja = value

    def __str__(self):
        return f'{self.id}-{self.tipo}-{str(self.restr)[0]}-{self.t1}-{self.t2}(t={self.franja})'

    def __repr__(self):
        return f'{self.id}-{self.tipo}-{str(self.restr)[0]}-{self.t1}-{self.t2}(t={self.franja})'

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

class Taller:
    """Clase que representa uno de los talleres de la cuadrícula del problema"""
    def __init__(self, row: int, col: int, tipo: str):
        self._row = None
        self._col = None
        self._tipo = None
        #self._franja = None

        self.row = row       # Setter valida
        self.col = col       # Setter valida
        self.tipo = tipo     # Setter valida

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("row must be a non-negative integer (0 or greater).")
        self._row = value

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("col must be a non-negative integer (0 or greater).")
        self._col = value

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if value not in {"STD", "SPC", "PRK"}:
            raise ValueError('tipo must be one of "STD", "SPC", or "PRK".')
        self._tipo = value

    def __str__(self):
        return f'{self.tipo}({self.row},{self.col})'

    def __repr__(self):
        return f'{self.tipo}({self.row},{self.col})'




problem = constraint.Problem()

"""domain = []
for r in range(ROWS):
    row = []
    for c in range(COLUMNS):
        taller = Taller(r, c, "STD" if c % 2 == 0 else "PRK")
        row.append(taller)
    domain.append(row)"""

# Falta por implementar la función que lea la cuadrícula de la input file,
# por ahora he asignado valores en el código (cuadrícula 5x5 de ejemplo en el enunciado)
domain = [
    [Taller(0, 0, "PRK"), Taller(0, 1, "STD"), Taller(0, 2, "PRK"), Taller(0, 3, "SPC"), Taller(0, 4, "PRK")],
    [Taller(1, 0, "STD"), Taller(1, 1, "STD"), Taller(1, 2, "STD"), Taller(1, 3, "STD"), Taller(1, 4, "PRK")],
    [Taller(2, 0, "STD"), Taller(2, 1, "SPC"), Taller(2, 2, "STD"), Taller(2, 3, "SPC"), Taller(2, 4, "PRK")],
    [Taller(3, 0, "SPC"), Taller(3, 1, "PRK"), Taller(3, 2, "PRK"), Taller(3, 3, "STD"), Taller(3, 4, "PRK")],
    [Taller(4, 0, "PRK"), Taller(4, 1, "STD"), Taller(4, 2, "STD"), Taller(4, 3, "SPC"), Taller(4, 4, "PRK")]
]

print("Talleres del problema: ")
for row in domain:
    print(row)

# Falta la función que tome los valores de la input file, los he asignado en el código por ahora
print("Aviones del problema: ")
aviones = [Avion(1, "JMB", True, 2, 2, 0),
           Avion(2, "STD", False, 1, 3, 0),
           Avion(3, "STD", False, 3, 0, 0),
           #Avion(4, "JMB", True, 1, 1, 0),
           # Puedes probar que con cuadrícula 5x5, 4 franjas y
           # 4 aviones encuentra solución, pero con 5 aviones no
           Avion(5, "STD", False, 2, 2, 0)]

# Asignamos las variables
variables = []
for i in range(len(aviones)):
    avion = []
    for j in range(FRANJAS):
        A = Avion(i + 1, aviones[i].tipo, aviones[i].restr, aviones[i].t1, aviones[i].t2, j)
        # Variable es un avión en una franja específica, el dominio son todos los talleres
        problem.addVariable(A, [element for row in domain for element in row])
        avion.append(A)
        #print("Avion ", A.id, ": t1 = ", A.t1, ", t2 = ", A.t2)
    variables.append(avion)
    print(avion)
#print(variables)


# Restricción de no más de 2 aviones por taller y solo 1 puede ser JMB
# Uso una función exterior para poder acceder tanto a la información de los aviones en la franja y
# a las asignaciones que se hagan durante la resolución (pasadas por referencia)
def limite_aviones_por_taller_exterior(aviones_franja):
    def limite_aviones_por_taller(*assignments):
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # aviones_franja es una lista los aviones de una sola franja de tiempo
        # Contamos en dos diccionarios la cantidad de aviones y aviones JMB para cada Taller asignado
        #print(assignments)
        #print(aviones_franja)

        plane_count = {}
        jmb_count = {}
        for i in range(len(assignments)):
            if aviones_franja[i].tipo == "STD":
                # Añadimos el taller al diccionario si no estaba ya y sumamos 1
                plane_count[assignments[i]] = plane_count.get(assignments[i], 0) + 1
            else:
                # Añadimos 1 al total de aviones y de aviones JMB
                plane_count[assignments[i]] = plane_count.get(assignments[i], 0) + 1
                jmb_count[assignments[i]] = jmb_count.get(assignments[i], 0) + 1
        #print("Total planes: ", plane_count)
        #print("Total JMB planes: ", jmb_count)
        # No más de 2 aviones totales y no más de 1 avión JMB
        if (not (all(plane_count_taller <= 2 for plane_count_taller in plane_count.values())) or
                (not all(jmb_count_taller <= 1 for jmb_count_taller in jmb_count.values()))):
            return False
        return True
    return limite_aviones_por_taller    # Devolvemos el valor de la función interior


# Al menos un taller adyacente libre para cada taller asignado a un avión
def parking_adyacente_vacio(*assignments):
    global domain   # Usamos la matriz de talleres con la que se define el problema
    rows = len(domain)
    cols = len(domain[0])

    occupied_positions = {(taller.row, taller.col) for taller in
                          assignments}  # Posiciones ocupadas
    #print(occupied_positions)

    for taller in assignments:
        #print(taller)
        r, c = taller.row, taller.col  # Fila y columna del taller actual

        # Obtener posiciones adyacentes sin salir del rango
        adjacent_positions = [
            (r - 1, c),  # Above
            (r + 1, c),  # Below
            (r, c - 1),  # Left
            (r, c + 1)  # Right
        ]
        adjacent_positions = [
            (ar, ac) for ar, ac in adjacent_positions
            if 0 <= ar < rows and 0 <= ac < cols  # Eliminar las posiciones adyacentes fuera de rango
        ]
        #print(adjacent_positions)

        # Devolver false si no hay ninguna posición adyacente no en las posiciones ocupadas
        if not any((ar, ac) not in occupied_positions for ar, ac in adjacent_positions):
            #print(False)
            return False

    #print(True)
    #print(occupied_positions)
    return True

# No puede haber aviones de tipo JMB adyacentes en el grid
def no_jmb_adyacentes_exterior(aviones_franja):
    def no_jmb_adyacentes(*assignments):
        global domain
        # Posiciones ocupadas
        position_map = {(taller.row, taller.col): taller for row in domain for taller in row}

        # Posiciones ocupadas por aviones JMB
        jmb_positions = {
            (taller.row, taller.col)
            for taller, plane in zip(assignments, aviones_franja)
            if plane.tipo == "JMB"
        }

        for (r, c) in jmb_positions:
            # Posiciones adyacentes a talleres con aviones JMB
            adjacent_positions = [
                (r - 1, c),
                (r + 1, c),
                (r, c - 1),
                (r, c + 1)
            ]
            # Mantener solo las posiciones con aviones asignados
            adjacent_positions = [
                (ar, ac) for ar, ac in adjacent_positions if (ar, ac) in position_map
            ]

            # Si hay algun taller adyacente con otro avión JMB devolvemos False
            if any((ar, ac) in jmb_positions for ar, ac in adjacent_positions):
                return False

        return True
    return no_jmb_adyacentes    # Devolvemos el valor de la función interior


# Añadimos las retricciones relacionadas con la posición de los aviones para cada franja específica
print("Añadiendo restricciones posicionales.")
for franja in range(FRANJAS):
    aviones_franja = [avion_i[franja] for avion_i in variables]
    problem.addConstraint(parking_adyacente_vacio, aviones_franja)
    # Para las funciones exteriores pasamos los aviones de cada franja como parámetro para poder
    # operar con sus datos
    problem.addConstraint(no_jmb_adyacentes_exterior(aviones_franja), aviones_franja)
    problem.addConstraint(limite_aviones_por_taller_exterior(aviones_franja), aviones_franja)


# Restricción de que todos las tareas tienen que hacerse en todos los aviones a lo largo de todas
# las franjas. Esta restricción permite que las tareas STD se hagan en talleres SPC
def hacer_tareas_total_exterior(avion):
    def hacer_tareas_total(*assignments):
        #print(avion)
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # avion es una lista con un mismo avión en todas sus franjas de tiempo
        # Contamos la cantidad de asignaciones a talleres STD y SPC
        numero_tareas = sum(1 for taller in assignments if (taller.tipo == "STD" or taller.tipo == "SPC"))
        #print("count: ", numero_tareas)
        #print("tareas totales del avión ", plane[0].id, ": ", plane[0].t1 + plane[0].t2)
        #print(avion[0].id, assignments)
        return numero_tareas == avion[0].t1 + avion[0].t2   # ¿Todas las tareas hechas?
    return hacer_tareas_total   # Devolvemos el valor de la función interior

# Añadimos la restricción de completitud de tareas t1 y t2 a todas las listas
# de cada avión, que incluyen el avión en las diferentes franjas horarias
for avion in variables:
    print("Añadiendo restricción de tareas totales al avión ", avion)
    problem.addConstraint(hacer_tareas_total_exterior(avion), avion)


# Restricción de que todos las tareas SPC tienen que hacerse en todos
# los aviones a lo largo de todas las franjas
def hacer_tareas_spc_exterior(avion):
    def hacer_tareas_spc(*assignments):
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # plane es una lista con un mismo avión en todas sus franjas de tiempo
        # Contamos la cantidad de asignaciones a talleres STD
        std_count = sum(1 for taller in assignments if taller.tipo == "SPC")
        #print("count: ", std_count)
        #print("Tareas especiales del avión ", plane[0].id, ": ", plane[0].t2)
        # Usamos >= porque puede haber tareas STD hechas en talleres SPC
        return std_count >= avion[0].t2
    return hacer_tareas_spc # Devolvemos el valor de la función interior


# Añadimos la restricción de completitud de tareas t2 a todas las listas
# de cada avión, que incluyen el avión en las diferentes franjas horarias
for avion in variables:
    #print(avion)
    print("Añadiendo restricción de tareas SPC al avión ", avion)
    problem.addConstraint(hacer_tareas_spc_exterior(avion), avion)


# Tareas SPC hechas todas antes de entrar a un taller STD
def tareas_spc_primero(*assignments):
    entrada_tayer_std = False   # ¿Se ha entrado anteriormente a un taller STD?
    for taller in assignments:
        if taller.tipo == "STD":
            entrada_tayer_std = True
        elif entrada_tayer_std:     # Se ha asignado un taller SPC después de entrar en uno STD
            #print("False: ", assignments)
            return False
    #print("True: ", assignments)
    return True

# Añadimos la restricción de completitud de tareas t2 antes de t1 a todas las listas
# de cada avión en las diferentes franjas horarias si tienen restr==True
for avion in variables:
    #print(avion)
    if avion[0].restr:
        print("Añadiendo restricción de tareas SPC antes de STD al avión ", avion)
        problem.addConstraint(tareas_spc_primero, avion)

# Obtenemos una solución y la mostramos
solution = problem.getSolution()
print("Solución encontrada: ", solution)

"""solutions = problem.getSolutions()
if not solutions:
    print("No solutions found")
else:
    for solution in solutions:
        print(solution)
    print(len(solutions), " solutions found")"""
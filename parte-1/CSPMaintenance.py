#!/usr/bin/env python
# -*- coding: utf-8 -*-

import constraint
import sys
import re
import random

global NFRANJAS, FILAS, COLUMNAS, dominio, variables
global problem


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
        self.franja = franja  # Setter valida

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("id debe ser un entero positivo.")
        self._id = value

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if value not in {"JMB", "STD"}:
            raise ValueError('tipo debe ser "JMB" o "STD".')
        self._tipo = value

    @property
    def restr(self):
        return self._restr

    @restr.setter
    def restr(self, value):
        if not isinstance(value, bool):
            raise ValueError("restr debe ser un booleano.")
        self._restr = value

    @property
    def t1(self):
        return self._t1

    @t1.setter
    def t1(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("t1 debe ser un entero positivo o cero.")
        self._t1 = value

    @property
    def t2(self):
        return self._t2

    @t2.setter
    def t2(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("t2 debe ser un entero positivo o cero.")
        self._t2 = value

    @property
    def franja(self):
        return self._franja

    @franja.setter
    def franja(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("franja debe ser un entero positivo o cero.")
        self._franja = value

    def __str__(self):
        return f'{self.id}-{self.tipo}-{str(self.restr)[0]}-{self.t1}-{self.t2}'

    def __repr__(self):
        return f'{self.id}-{self.tipo}-{str(self.restr)[0]}-{self.t1}-{self.t2}'

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
        # self._franja = None

        self.row = row  # Setter valida
        self.col = col  # Setter valida
        self.tipo = tipo  # Setter valida

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("row debe ser un entero positivo o cero..")
        self._row = value

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("col debe ser un entero positivo o cero..")
        self._col = value

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if value not in {"STD", "SPC", "PRK"}:
            raise ValueError('tipo debe ser "STD", "SPC", o "PRK".')
        self._tipo = value

    def __str__(self):
        return f'{self.tipo}({self.row},{self.col})'

    def __repr__(self):
        return f'{self.tipo}({self.row},{self.col})'


# Restricción de no más de 2 aviones por taller y solo 1 puede ser JMB
# Usamos funciones anidadas para poder acceder tanto a la información de los aviones en la franja y
# a las asignaciones que se hagan durante la resolución (pasadas por referencia)
def limite_aviones_por_taller_exterior(aviones_franja):
    def limite_aviones_por_taller(*assignments):
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # aviones_franja es una lista los aviones de una sola franja de tiempo
        # Contamos en 2 diccionarios la cantidad de aviones y aviones JMB para cada Taller asignado

        cantidad_aviones = {}
        cantidad_jmb = {}
        for i in range(len(assignments)):
            if aviones_franja[i].tipo == "STD":
                # Añadimos el taller al diccionario si no estaba ya y sumamos 1
                cantidad_aviones[assignments[i]] = cantidad_aviones.get(assignments[i], 0) + 1
            else:
                # Añadimos 1 al total de aviones y de aviones JMB
                cantidad_aviones[assignments[i]] = cantidad_aviones.get(assignments[i], 0) + 1
                cantidad_jmb[assignments[i]] = cantidad_jmb.get(assignments[i], 0) + 1
        # No más de 2 aviones totales y no más de 1 avión JMB
        if (not (all(cantidad_aviones_taller <= 2 for cantidad_aviones_taller in
                     cantidad_aviones.values())) or
                (not all(
                    cantidad_jmb_taller <= 1 for cantidad_jmb_taller in cantidad_jmb.values()))):
            return False
        return True

    return limite_aviones_por_taller  # Devolvemos el valor de la función interior


# Al menos un taller adyacente libre para cada taller asignado a un avión
def parking_adyacente_vacio(*assignments):
    global dominio  # Usamos la matriz de talleres con la que se define el problema
    global FILAS
    global COLUMNAS

    posiciones_ocupadas = {(taller.row, taller.col) for taller in
                           assignments}  # Posiciones ocupadas

    for taller in assignments:
        r, c = taller.row, taller.col  # Fila y columna del taller actual

        # Obtener posiciones adyacentes sin salir del rango
        adjacent_positions = [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1)
        ]
        adjacent_positions = [
            (ar, ac) for ar, ac in adjacent_positions
            if 0 <= ar < FILAS and 0 <= ac < COLUMNAS  # Eliminar las posiciones fuera de rango
        ]

        # Devolver false si no hay ninguna posición adyacente no en las posiciones ocupadas
        if not any((ar, ac) not in posiciones_ocupadas for ar, ac in adjacent_positions):
            return False

    return True


# No puede haber aviones de tipo JMB adyacentes en la cuadrícula
def no_jmb_adyacentes_exterior(aviones_franja):
    def no_jmb_adyacentes(*assignments):
        global dominio
        # Posiciones ocupadas
        position_map = {(taller.row, taller.col): taller for taller in dominio}

        # Posiciones ocupadas por aviones JMB
        jmb_positions = {
            (taller.row, taller.col)
            for taller, avion in zip(assignments, aviones_franja)
            if avion.tipo == "JMB"
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

    return no_jmb_adyacentes  # Devolvemos el valor de la función interior


# Restricción de que todos las tareas tienen que hacerse en todos los aviones a lo largo de todas
# las franjas. Esta restricción permite que las tareas STD se hagan en talleres SPC
def hacer_tareas_total_exterior(avion):
    def hacer_tareas_total(*assignments):
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # avion es una lista con un mismo avión en todas sus franjas de tiempo
        # Contamos la cantidad de asignaciones a talleres STD y SPC
        numero_tareas = (
            sum(1 for taller in assignments if (taller.tipo == "STD" or taller.tipo == "SPC")))

        # Usamos >= ya que hemos asumido que un avión puede descansar en un taller libre aun que no
        # realize una tarea de mantenimiento
        return numero_tareas >= avion[0].t1 + avion[0].t2  # ¿Todas las tareas hechas?

    return hacer_tareas_total  # Devolvemos el valor de la función interior


# Restricción de que todos las tareas SPC tienen que hacerse en todos
# los aviones a lo largo de todas las franjas
def hacer_tareas_spc_exterior(avion):
    def hacer_tareas_spc(*assignments):
        # Assignments contiene las asignaciones de tipo Taller a las variables de tipo Avion
        # avion es una lista con un mismo avión en todas sus franjas de tiempo
        # Contamos la cantidad de asignaciones a talleres STD
        std_count = sum(1 for taller in assignments if taller.tipo == "SPC")
        # Usamos >= porque puede haber tareas STD hechas en talleres SPC
        return std_count >= avion[0].t2

    return hacer_tareas_spc  # Devolvemos el valor de la función interior


# Tareas SPC hechas todas antes de entrar a un taller STD
def tareas_spc_primero_exterior(avion):
    def tareas_spc_primero(*assignments):
        cuenta_acceso_talleres_spc = 0
        for taller in assignments:
            if cuenta_acceso_talleres_spc < avion[0].t2:  # Tareas SPC sin completar
                if taller.tipo == "SPC":  # Completamos una tarea SPC
                    cuenta_acceso_talleres_spc += 1
                elif taller.tipo == "STD":  # Acceso a un STD sin completar todas las tareas SPC
                    return False
        return True

    return tareas_spc_primero


def añadir_restricciones():
    global problem, variables, NFRANJAS

    # Añadimos las retricciones relacionadas con la posición de los aviones para cada franja
    print("Añadiendo restricciones posicionales a todos los aviones...")
    for franja in range(NFRANJAS):
        aviones_franja = [avion_i[franja] for avion_i in variables]
        problem.addConstraint(parking_adyacente_vacio, aviones_franja)
        # Para las funciones exteriores pasamos los aviones de cada franja como parámetro para poder
        # operar con sus datos
        problem.addConstraint(no_jmb_adyacentes_exterior(aviones_franja), aviones_franja)
        problem.addConstraint(limite_aviones_por_taller_exterior(aviones_franja), aviones_franja)

    # Añadimos la restricción de completitud de tareas totales y tareas t2 a todas las listas
    # de cada avión, que incluyen el avión en las diferentes franjas horarias
    print("Añadiendo restricciones de tareas todos los aviones...")
    for avion in variables:
        problem.addConstraint(hacer_tareas_total_exterior(avion), avion)
        problem.addConstraint(hacer_tareas_spc_exterior(avion), avion)

    # Añadimos la restricción de completitud de tareas t2 antes de t1 a todas las listas
    # de cada avión en las diferentes franjas horarias si tienen restr==True
    for avion in variables:
        if avion[0].restr:
            print("Añadiendo restricción de tareas SPC antes de STD al avión ", avion[0])
            problem.addConstraint(tareas_spc_primero_exterior(avion), avion)


def leer_parametros(path_param):
    """Función que lee todos los parámetros del archivo de entrada y crea el domninio y variables
    del problema a partir de estos parámetros"""
    global NFRANJAS, FILAS, COLUMNAS, dominio, variables, problem

    dominio = []  # Dominio del problema
    variables = []  # Matriz de variables del problema

    try:
        with open(path_param, 'r') as file:
            # Leemos todas las líneas de el fichero de entrada
            lines = file.readlines()

        # Extraemos el número de franjas de tiempo
        linea_franjas = lines[0].strip()

        # Usamos una expresión regular para extraer el dígito de "Franjas: d"
        NFRANJAS = int(re.search(r"Franjas:\s*(\d+)", linea_franjas).group(1))

        # Extraemos las dimensiones de la cuadrícula de talleres
        dimensiones_talleres = lines[1].strip()

        # Separamos los valores de dimension por la "x"
        FILAS, COLUMNAS = map(int, dimensiones_talleres.split('x'))

        # Extraemos los talleres de la cuadrícula del problema y sus posiciones
        for line in lines[2:5]:
            tipo, posiciones = line.split(":")
            tipo = tipo.strip()

            # Búsqueda de todas las strings del tipo "(d,d)" correspondientes a una posición
            posiciones = re.findall(r"\((\d+),(\d+)\)", posiciones)

            # Creamos el dominio de Talleres (el orden no importa)
            for posicion in posiciones:
                row, col = map(int, posicion)
                dominio.append(Taller(row, col, tipo))

        # Extraemos los aviones del problema y añadimos las variables
        for line in lines[5:]:
            info_avion = line.split("-")
            avion_i = []  # Lista del avión i en todas las franjas
            for franja in range(NFRANJAS):
                id = int(info_avion[0])
                tipo = info_avion[1]
                if info_avion[2] == "T":
                    restr = True
                elif info_avion[2] == "F":
                    restr = False
                else:
                    print(f"Error en el fichero de entrada: restr incorrecto (RESTR: T/F).")
                    sys.exit(1)

                t1 = int(info_avion[3])
                t2 = int(info_avion[4])
                pos_ij = Avion(id, tipo, restr, t1, t2, franja)
                # Variable es la posición de uno de los aviones en una franja específica, el
                # dominio son todos los talleres de la cuadrícula
                problem.addVariable(pos_ij, dominio)
                avion_i.append(pos_ij)  # Añadimos el avión en la franja j a la lista del avión i

            # Añadimos la lista del avión i en todas las franjas a la matriz de variables para poder
            # usarla al crear las restricciones
            variables.append(avion_i)

    except FileNotFoundError:
        print(f"Fichero de entrada '{path_param}' no encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Error en el fichero de entrada: {e}")
        sys.exit(1)


def escribir_soluciones(file_path, solutions):
    """Función que crea un nuevo archivo <file_path>.csv con el número de soluciones del problema
    y añade entre 1 y 5 de las primeras soluciones encontradas por python-constraint"""
    global NFRANJAS, variables

    with open(file_path + ".csv", "w") as out_file:
        out_file.write("N. Sol: " + str(len(solutions)) + "\n")

        # Lista aplanada de las matriz de variables (avion_ij) que usaremos para ordenar las sols
        array_variables = list(avion_ij for avion_i in variables for avion_ij in avion_i)
        if len(solutions) > 0:
            # Escribimos entre 1 y 5 soluciones de las primeras encontradas
            for nsol in range(random.randint(1, min(5, len(solutions)))):
                # Ordenamos la solución en base al orden de introducción de las variables, ya que a
                # veces python-constraint devuelve los valores asignados en un orden distinto al
                # orden en el que se han introducido las variables
                solucion_ordenada = {key: solutions[nsol][key] for key in array_variables}

                # Obtenemos los valores asignados a las variables
                posiciones_solucion = list(solucion_ordenada.values())

                out_file.write(f"Solución {nsol + 1}:\n")

                index = 0
                for avion_i in variables:
                    # Escribimos los valores correspondientes al avión i (tantos como franjas haya) y
                    # cambiamos index al indice de la primera asignación del siguiente avión
                    posiciones_avion_i = ", ".join(
                        map(str, posiciones_solucion[index:index + NFRANJAS]))
                    out_file.write(f"\t{avion_i[0]}: {posiciones_avion_i}\n")
                    index += NFRANJAS


def main():
    global problem
    problem = constraint.Problem()

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        sys.exit(1)

    file_path = sys.argv[1]
    leer_parametros(file_path)

    print(f"Franjas: {NFRANJAS}")
    print(f"Cuadrícula: {FILAS}x{COLUMNAS}")
    print("Dominio:", dominio)

    print("Aviones del problema: ")
    for avion_i in variables:
        print(avion_i[0])

    añadir_restricciones()

    solutions = problem.getSolutions()

    escribir_soluciones(file_path, solutions)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
ProgIIIG101-202502-Sudoku
"""

import itertools as it
import copy
import time
import os

cols = "ABCDEFGHI"
rows = range(1, 10)

# Inicialización de dominios
def init_domains():
    return {f"{c}{r}": set(range(1, 10)) for r in rows for c in cols}

var_doms = init_domains()

def loadBoard(fileName, domains):
    print(f"Cargando tablero: {fileName}")
    try:
        with open(fileName, 'r') as f:
            # Reiniciar dominios
            for key in domains:
                domains[key] = set(range(1, 10))
            
            # Leer archivo
            # El archivo tiene 81 líneas.
            # Orden: A1, B1, C1... I1, A2... (según el código original que iteraba keys)
            # Pero var_doms keys dependen del orden de inserción o creación.
            # Mejor asegurar el orden.
            ordered_keys = [f"{c}{r}" for r in rows for c in cols]
            
            lines = f.readlines()
            for i, key in enumerate(ordered_keys):
                if i < len(lines):
                    try:
                        value = int(lines[i].strip())
                        if 1 <= value <= 9:
                            domains[key] = {value}
                    except ValueError:
                        pass
    except FileNotFoundError:
        print("Archivo no encontrado.")
    return domains

def colsVars(cols, rows):
    groupVars = []
    for col in cols:
        colVars = []
        for row in rows:
            colVars.append(f"{col}{row}")
        groupVars.append(colVars)
    return groupVars

def rowsVars(cols, rows):
    groupVars = []
    for row in rows:
        rowVars = []
        for col in cols:
            rowVars.append(f"{col}{row}")
        groupVars.append(rowVars)
    return groupVars

def blockVars(cols, rows):
    groupVars = []
    # Bloques 3x3
    for r_block in [range(1, 4), range(4, 7), range(7, 10)]:
        for c_block in ["ABC", "DEF", "GHI"]:
            block = []
            for r in r_block:
                for c in c_block:
                    block.append(f"{c}{r}")
            groupVars.append(block)
    return groupVars

# Definición de grupos de variables (Filas, Columnas, Bloques)
groupVars = colsVars(cols, rows) + rowsVars(cols, rows) + blockVars(cols, rows)

# Definición de restricciones
constraints = []
for group in groupVars:
    constraints.append(('AllDiff', group))

def AllDiff(domains, vars):
    changed = False
    for var in vars:
        if len(domains[var]) == 1:
            val = list(domains[var])[0]
            for var2 in vars:
                if var != var2:
                    if val in domains[var2]:
                        domains[var2].discard(val)
                        changed = True
                        if len(domains[var2]) == 0:
                            return True, False # Changed, Inconsistent
    return changed, True # Changed, Consistent

def propagate(domains):
    # Aplica restricciones repetidamente hasta que no haya cambios (AC-3 simplificado)
    while True:
        any_change = False
        consistent = True
        for constraint in constraints:
            # constraint[0] es el nombre de la función ('AllDiff')
            # constraint[1] son las variables del grupo
            func = globals()[constraint[0]]
            changed, is_consistent = func(domains, constraint[1])
            if not is_consistent:
                return False # Inconsistente
            if changed:
                any_change = True
        
        if not any_change:
            break
    return True

def is_solved(domains):
    return all(len(domains[v]) == 1 for v in domains)

def select_variable(domains):
    # MRV: Minimum Remaining Values
    unassigned = [v for v in domains if len(domains[v]) > 1]
    if not unassigned:
        return None
    return min(unassigned, key=lambda v: len(domains[v]))

def backtrack(domains):
    # 1. Propagar restricciones
    if not propagate(domains):
        return None
    
    # 2. Verificar si está resuelto
    if is_solved(domains):
        return domains
    
    # 3. Seleccionar variable
    var = select_variable(domains)
    if not var:
        return None # No debería pasar si is_solved es False
    
    # 4. Probar valores
    # Ordenar valores (se puede mejorar con LCV)
    values = list(domains[var])
    
    for val in values:
        new_domains = copy.deepcopy(domains)
        new_domains[var] = {val}
        
        result = backtrack(new_domains)
        if result:
            return result
            
    return None

def print_board(domains):
    print("\nTablero Sudoku:")
    print("  " + " ".join(cols))
    for r in rows:
        row_str = f"{r} "
        for c in cols:
            key = f"{c}{r}"
            val = list(domains[key])[0] if len(domains[key]) == 1 else "."
            row_str += f"{val} "
        print(row_str)

def menu():
    while True:
        print("\n--- MENÚ SUDOKU CSP ---")
        print("1. Tablero Imposible 1 (tablero.txt)")
        print("2. Tablero Imposible 2 (tablero_imposible.txt)")
        print("3. Tablero Muy Difícil 1 (tablero_muy_dificil_1.txt)")
        print("4. Tablero Muy Difícil 2 (tablero_muy_dificil_2.txt)")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        filename = ""
        if opcion == "1":
            filename = "/.Tableros/tablero.txt"
        elif opcion == "2":
            filename = "/.Tableros/tablero_imposible.txt"
        elif opcion == "3":
            filename = "/.Tableros/tablero_muy_dificil_1.txt"
        elif opcion == "4":
            filename = "/.Tableros/tablero_muy_dificil_2.txt"
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")
            continue
            
        if filename:
            current_domains = init_domains()
            current_domains = loadBoard(filename, current_domains)
            
            print("Resolviendo...")
            start_time = time.time()
            solution = backtrack(current_domains)
            end_time = time.time()
            
            if solution:
                print(f"¡Solución encontrada en {end_time - start_time:.4f} segundos!")
                print_board(solution)
            else:
                print("No se encontró solución.")

if __name__ == "__main__":
    menu()


import os
import heapq
from collections import deque
import re

# ==========================================================
# ARCHIVOS DEL SISTEMA
# ==========================================================

ARCHIVO_USUARIOS = "usuarios.txt"
ARCHIVO_CENTROS = "centros.txt"
ARCHIVO_RUTAS = "rutas.txt"
SELECCION_CENTROS = []
RUTAS_MEMORIA = []
CENTROS_MEMORIA = []
CAMBIOS_CENTROS = False
CAMBIOS_RUTAS = False

# ==========================================================
# INICIALIZACIÓN DE ARCHIVOS
# ==========================================================

def inicializar_archivos():
    for archivo in [ARCHIVO_USUARIOS, ARCHIVO_CENTROS, ARCHIVO_RUTAS]:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8"):
                pass

# ==========================================================
# UTILIDADES GENERALES
# ==========================================================

def pausar():
    input("\nPresione ENTER para continuar...")

def leer_lineas(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return [linea.strip() for linea in f if linea.strip()]
    except:
        return []

def escribir_lineas(nombre_archivo, lineas):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            for linea in lineas:
                f.write(linea + "\n")
    except Exception as e:
        print("Error al guardar archivo:", e)

# ==========================================================
# USUARIOS – REGISTRO Y AUTENTICACIÓN
# ==========================================================

def validar_contrasena(clave):
    tiene_mayuscula = any(c.isupper() for c in clave)
    tiene_minuscula = any(c.islower() for c in clave)
    tiene_numero = any(c.isdigit() for c in clave)

    return tiene_mayuscula and tiene_minuscula and tiene_numero

def correo_valido(correo):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, correo) is not None

def usuario_existe(correo, cedula):
    for linea in leer_lineas(ARCHIVO_USUARIOS):
        datos = linea.split(",")
        if len(datos) >= 5:
            if datos[1] == cedula or datos[3].lower() == correo.lower():
                return True
    return False

def registrar_usuario():
    print("\n=== REGISTRO DE USUARIO ===")

    while True:
        nombre = input("Nombre completo: ").strip()
        if nombre:
            break
        print("El nombre no puede estar vacío.")

    while True:
        cedula = input("Cédula (10 dígitos): ").strip()
        if cedula.isdigit() and len(cedula) == 10:
            break
        print("Cédula inválida.")

    while True:
        edad_txt = input("Edad: ").strip()
        if edad_txt.isdigit() and 0 < int(edad_txt) < 120:
            edad = edad_txt
            break
        print("Edad inválida.")

    while True:
        correo = input("Correo electrónico: ").strip()
        if not correo_valido(correo):
            print("Formato de correo inválido.")
            continue
        if usuario_existe(correo, cedula):
            print("Ya existe un usuario con esa cédula o correo.")
            continue
        break

    while True:
        clave = input("Contraseña segura: ").strip()
        if validar_contrasena(clave):
            break
        print("Debe tener mayúsculas, minúsculas y números.")

    while True:
        rol = input("Tipo de cuenta (administrador/cliente): ").strip().lower()
        if rol in ["administrador", "cliente"]:
            break
        print("Rol inválido.")

    linea = f"{nombre},{cedula},{edad},{correo},{clave},{rol}"
    escribir_lineas(ARCHIVO_USUARIOS, leer_lineas(ARCHIVO_USUARIOS) + [linea])

    print("Usuario registrado correctamente.")

def iniciar_sesion():
    print("\n=== INICIO DE SESIÓN ===")
    correo = input("Correo: ").strip()
    clave = input("Contraseña: ").strip()

    for linea in leer_lineas(ARCHIVO_USUARIOS):
        datos = linea.split(",")
        if len(datos) == 6:
            if datos[3] == correo and datos[4] == clave:
                print("Bienvenido,", datos[0])
                return datos[5], datos[0]
    print("Credenciales incorrectas.")
    return None, None

# ==========================================================
# CENTROS – ADMINISTRADOR
# ==========================================================

def cargar_centros():
    global CENTROS_MEMORIA
    if CENTROS_MEMORIA:
        return CENTROS_MEMORIA

    centros = []
    for linea in leer_lineas(ARCHIVO_CENTROS):
        partes = linea.split(",")
        if len(partes) == 3:
            try:
                centros.append({
                    "nombre": partes[0],
                    "region": partes[1],
                    "costo": float(partes[2])
                })
            except:
                pass
    CENTROS_MEMORIA = centros
    return CENTROS_MEMORIA

def agregar_centro():
    global CAMBIOS_CENTROS
    print("\n=== AGREGAR CENTRO DE DISTRIBUCIÓN ===")

    nombre = input("Nombre del centro: ").strip()
    region = input("Región: ").strip()

    try:
        costo = float(input("Costo base: "))
        if costo < 0:
            raise ValueError
    except:
        print("Costo inválido.")
        return

    centros = cargar_centros()
    if any(c["nombre"].lower() == nombre.lower() for c in centros):
        print("El centro ya existe.")
        return

    centros.append({"nombre": nombre, "region": region, "costo": costo})
    CAMBIOS_CENTROS = True
    print("Centro agregado (pendiente de guardar).")

def listar_centros():
    print("\n=== LISTA DE CENTROS ===")
    centros = cargar_centros()
    if not centros:
        print("No hay centros registrados.")
        return

    for i, c in enumerate(centros, 1):
        print(f"{i}. {c['nombre']} | {c['region']} | ${c['costo']}")

def guardar_centros():
    global CAMBIOS_CENTROS, CENTROS_MEMORIA
    if not CAMBIOS_CENTROS:
        print("No hay cambios para guardar.")
        return

    lineas = [
        f"{c['nombre']},{c['region']},{c['costo']}"
        for c in CENTROS_MEMORIA
    ]
    escribir_lineas(ARCHIVO_CENTROS, lineas)
    CAMBIOS_CENTROS = False
    print("Centros guardados correctamente.")


# ==========================================================
# ACCIONES – CLIENTE
# ==========================================================

def seleccionar_centros_envio():
    global SELECCION_CENTROS
    print("\n=== SELECCIONAR CENTROS PARA ENVÍO ===")
    centros_disponibles = cargar_centros()
    
    if not centros_disponibles:
        print("No hay centros registrados en el sistema.")
        return

    for i, c in enumerate(centros_disponibles, 1):
        print(f"{i}. {c['nombre']} (${c['costo']})")

    entrada = input("\nIngrese los números de los centros (ej: 1,3): ").strip()
    if not entrada: return

    partes = entrada.split(",")
    for parte in partes:
        p = parte.strip()
        if p.isdigit():
            idx = int(p) - 1
            if 0 <= idx < len(centros_disponibles):
                SELECCION_CENTROS.append(centros_disponibles[idx])
                print(f"Agregado: {centros_disponibles[idx]['nombre']}")

def agregar_ruta():
    global CAMBIOS_RUTAS, RUTAS_MEMORIA
    print("\n=== AGREGAR RUTA ===")

    centros = cargar_centros()
    if not centros:
        print("No existen centros registrados.")
        return

    origen = input("Centro origen: ").strip()
    destino = input("Centro destino: ").strip()

    if origen == destino:
        print("Origen y destino no pueden ser iguales.")
        return

    nombres = [c["nombre"] for c in centros]
    if origen not in nombres or destino not in nombres:
        print("Centro inexistente.")
        return

    try:
        distancia = float(input("Distancia: "))
        costo = float(input("Costo: "))
        if distancia <= 0 or costo < 0:
            raise ValueError
    except:
        print("Distancia o costo inválido.")
        return

    for r in RUTAS_MEMORIA:
        if r["origen"] == origen and r["destino"] == destino:
            print("La ruta ya existe.")
            return

    RUTAS_MEMORIA.append({
        "origen": origen,
        "destino": destino,
        "distancia": distancia,
        "costo": costo
    })

    CAMBIOS_RUTAS = True
    print("Ruta agregada (pendiente de guardar).")

def listar_rutas():
    print("\n=== LISTA DE RUTAS ===")
    rutas = cargar_rutas()
    if not rutas:
        print("No hay rutas registradas.")
        return

    for i, r in enumerate(rutas, 1):
        print(f"{i}. {r['origen']} -> {r['destino']} | Dist: {r['distancia']} | Costo: {r['costo']}")


def eliminar_ruta():
    global CAMBIOS_RUTAS
    print("\n=== ELIMINAR RUTA ===")

    rutas = cargar_rutas()
    if not rutas:
        print("No hay rutas registradas.")
        return

    origen = input("Origen: ").strip()
    destino = input("Destino: ").strip()

    nuevas = []
    eliminado = False

    for r in rutas:
        if r["origen"] == origen and r["destino"] == destino:
            eliminado = True
        else:
            nuevas.append(r)

    if eliminado:
        escribir_lineas(
            ARCHIVO_RUTAS,
            [f"{r['origen']},{r['destino']},{r['distancia']},{r['costo']}" for r in nuevas]
        )
        CAMBIOS_RUTAS = False
        print("Ruta eliminada.")
    else:
        print("Ruta no encontrada.")



def actualizar_centro():
    global CAMBIOS_CENTROS
    print("\n=== ACTUALIZAR CENTRO ===")

    centros = cargar_centros()
    if not centros:
        print("No hay centros.")
        return

    nombre = input("Centro a actualizar: ").strip()
    for c in centros:
        if c["nombre"] == nombre:
            print(f"Actual: {c}")

            nueva_region = input("Nueva región (ENTER para mantener): ").strip()
            nuevo_costo = input("Nuevo costo (ENTER para mantener): ").strip()

            if nueva_region:
                c["region"] = nueva_region

            if nuevo_costo:
                try:
                    valor = float(nuevo_costo)
                    if valor >= 0:
                        c["costo"] = valor
                except:
                    print("Costo inválido.")

            CAMBIOS_CENTROS = True
            print("Centro actualizado (pendiente de guardar).")
            return

    print("Centro no encontrado.")


def eliminar_centro():
    global CAMBIOS_CENTROS, CENTROS_MEMORIA
    print("\n=== ELIMINAR CENTRO ===")

    if not CENTROS_MEMORIA:
        print("No hay centros.")
        return

    nombre = input("Centro a eliminar: ").strip()
    nuevos = [c for c in CENTROS_MEMORIA if c["nombre"] != nombre]

    if len(nuevos) == len(CENTROS_MEMORIA):
        print("Centro no encontrado.")
        return

    CENTROS_MEMORIA = nuevos
    CAMBIOS_CENTROS = True
    print("Centro eliminado (pendiente de guardar).")


def listar_seleccion_ordenada():
    global SELECCION_CENTROS
    if not SELECCION_CENTROS:
        print("\nLa selección está vacía.")
        return

    print("\n--- Ordenar por: 1. Nombre | 2. Costo ---")
    op = input("Seleccione: ")
    llave = "nombre" if op == "1" else "costo"
    
    lista_ordenada = merge_sort_centros(SELECCION_CENTROS, llave)
    
    print("\n=== CENTROS SELECCIONADOS ===")
    total = 0
    for c in lista_ordenada:
        print(f"- {c['nombre']} | ${c['costo']}")
        total += c['costo']
    print(f"TOTAL ESTIMADO: ${total}")

def eliminar_centro_seleccionado():
    if not SELECCION_CENTROS:
        print("\nNo hay nada que eliminar.")
        return

    for i, c in enumerate(SELECCION_CENTROS, 1):
        print(f"{i}. {c['nombre']}")
    
    try:
        idx = int(input("Número del centro a quitar: ")) - 1
        if 0 <= idx < len(SELECCION_CENTROS):
            eliminado = SELECCION_CENTROS.pop(idx)
            print(f"Eliminado: {eliminado['nombre']}")
        else:
            print("Índice inválido.")
    except:
        print("Error en la entrada.")

def guardar_seleccion_archivo(nombre_usuario):
    if not SELECCION_CENTROS:
        print("\nNo hay selección para guardar.")
        return
    lineas_actuales = leer_lineas(ARCHIVO_RUTAS)
    
    nuevas_lineas = [
        f"PEDIDO_{nombre_usuario.replace(' ', '_')},{c['nombre']},0,{c['costo']}" 
        for c in SELECCION_CENTROS
    ]
    
    escribir_lineas(ARCHIVO_RUTAS, lineas_actuales + nuevas_lineas)
    print(f"\nSelección guardada en {ARCHIVO_RUTAS} correctamente.")

def actualizar_seleccion_centro():
    global SELECCION_CENTROS
    if not SELECCION_CENTROS:
        print("\nNo hay centros seleccionados para actualizar.")
        return

    print("\n=== ACTUALIZAR SELECCIÓN ===")
    for i, c in enumerate(SELECCION_CENTROS, 1):
        print(f"{i}. {c['nombre']} (Costo actual: ${c['costo']})")

    try:
        idx = int(input("Número del centro que desea cambiar: ")) - 1
        if 0 <= idx < len(SELECCION_CENTROS):
            centros_disponibles = cargar_centros()
            print("\n--- Seleccione el nuevo centro de reemplazo ---")
            for j, disponible in enumerate(centros_disponibles, 1):
                print(f"{j}. {disponible['nombre']} (${disponible['costo']})")
            
            nuevo_idx = int(input("Número del nuevo centro: ")) - 1
            if 0 <= nuevo_idx < len(centros_disponibles):
                SELECCION_CENTROS[idx] = centros_disponibles[nuevo_idx]
                print("Selección actualizada con éxito.")
            else:
                print("Opción de reemplazo no válida.")
        else:
            print("Índice de selección no válido.")
    except:
        print("Error: Ingrese solo números.")

# ==========================================================
# GRAFOS – RUTAS
# ==========================================================

def cargar_rutas():
    global RUTAS_MEMORIA
    if RUTAS_MEMORIA:
        return RUTAS_MEMORIA

    rutas = []
    for linea in leer_lineas(ARCHIVO_RUTAS):
        partes = linea.split(",")
        if len(partes) == 4:
            try:
                rutas.append({
                    "origen": partes[0],
                    "destino": partes[1],
                    "distancia": float(partes[2]),
                    "costo": float(partes[3])
                })
            except:
                pass

    RUTAS_MEMORIA = rutas
    return RUTAS_MEMORIA

def guardar_rutas():
    global CAMBIOS_RUTAS, RUTAS_MEMORIA
    if not CAMBIOS_RUTAS:
        print("No hay cambios de rutas para guardar.")
        return

    lineas = [
        f"{r['origen']},{r['destino']},{r['distancia']},{r['costo']}"
        for r in RUTAS_MEMORIA
    ]

    escribir_lineas(ARCHIVO_RUTAS, lineas)
    CAMBIOS_RUTAS = False
    print("Rutas guardadas correctamente.")


def construir_grafo():
    grafo = {}
    for r in cargar_rutas():
        grafo.setdefault(r["origen"], []).append((r["destino"], r["costo"]))
        grafo.setdefault(r["destino"], []).append((r["origen"], r["costo"]))
    return grafo

def dijkstra(origen, destino):
    print("\n=== CALCULAR RUTA MÁS ÓPTIMA (DIJKSTRA) ===")

    grafo = construir_grafo()
    if origen not in grafo or destino not in grafo:
        print("Centro inexistente.")
        return

    distancias = {nodo: float("inf") for nodo in grafo}
    distancias[origen] = 0
    previos = {}

    cola = [(0, origen)]

    while cola:
        dist_actual, actual = heapq.heappop(cola)

        if actual == destino:
            break

        if dist_actual > distancias[actual]:
            continue

        for vecino, peso in grafo.get(actual, []):
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                previos[vecino] = actual
                heapq.heappush(cola, (nueva_dist, vecino))

    if destino not in previos and origen != destino:
        print("No hay ruta disponible.")
        return

    ruta = []
    actual = destino
    while actual != origen:
        ruta.append(actual)
        actual = previos[actual]
    ruta.append(origen)
    ruta.reverse()

    print("Ruta:", " -> ".join(ruta))
    print("Costo total:", distancias[destino])

# ==========================================================
# ALGORITMO DE ORDENAMIENTO (MERGE SORT)
# ==========================================================

def merge_sort_centros(lista, llave):
    if len(lista) <= 1:
        return lista

    medio = len(lista) // 2
    izq = merge_sort_centros(lista[:medio], llave)
    der = merge_sort_centros(lista[medio:], llave)

    return merge(izq, der, llave)

def merge(izq, der, llave):
    resultado = []
    i = j = 0
    while i < len(izq) and j < len(der):
        if izq[i][llave] <= der[j][llave]:
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado

# ==========================================================
# ÁRBOL JERÁRQUICO (DICCIONARIOS)
# ==========================================================

def construir_arbol_regiones():
    arbol = {}
    for c in cargar_centros():
        arbol.setdefault(c["region"], []).append(c["nombre"])
    return arbol

def mostrar_arbol():
    print("\n=== JERARQUÍA DE REGIONES ===")
    arbol = construir_arbol_regiones()
    if not arbol:
        print("No hay datos.")
        return
    for region, centros in arbol.items():
        print(region)
        for c in centros:
            print("  └─", c)

# ==========================================================
# MENÚS
# ==========================================================

def menu_admin():
    while True:
        print("\n=== MENÚ ADMINISTRADOR ===")
        print("1. Agregar centro")
        print("2. Listar centros")
        print("3. Actualizar centro")
        print("4. Eliminar centro")
        print("5. Agregar ruta")
        print("6. Listar rutas")
        print("7. Eliminar ruta")
        print("8. Guardar cambios")
        print("9. Salir")

        op = input("Opción: ")

        if op == "1":
            agregar_centro()
        elif op == "2":
            listar_centros()
        elif op == "3":
            actualizar_centro()
        elif op == "4":
            eliminar_centro()
        elif op == "5":
            agregar_ruta()
        elif op == "6":
            listar_rutas()
        elif op == "7":
            eliminar_ruta()
        elif op == "8":
            guardar_centros()
            guardar_rutas()
        elif op == "9":
            break
        else:
            print("Opción inválida.")

        pausar()


def menu_cliente(nombre):
    while True:
        print(f"\n=== MENÚ CLIENTE ({nombre}) ===")
        print("1. Ver jerarquía de centros")
        print("2. Calcular ruta óptima (Dijkstra)")
        print("3. Seleccionar centros para envío")
        print("4. Ver selección y total (Ordenado Merge Sort)")
        print("5. Actualizar selección de centro")
        print("6. Eliminar centro de selección")
        print("7. Confirmar y Guardar selección en archivo")
        print("8. Salir")

        op = input("Opción: ")
        if op == "1":
            mostrar_arbol()
        elif op == "2":
            o = input("Origen: ").strip()
            d = input("Destino: ").strip()
            dijkstra(o, d)
        elif op == "3":
            seleccionar_centros_envio()
        elif op == "4":
            listar_seleccion_ordenada()
        elif op == "5":
            actualizar_seleccion_centro()
        elif op == "6":
            eliminar_centro_seleccionado()
        elif op == "7":
            guardar_seleccion_archivo(nombre)
        elif op == "8":
            SELECCION_CENTROS.clear()
            break
        else:
            print("Opción inválida.")
        pausar()

# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

def main():
    inicializar_archivos()

    while True:
        print("\n=== POLIDELIVERY ===")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Salir")

        op = input("Seleccione: ")

        if op == "1":
            rol, nombre = iniciar_sesion()
            if rol == "administrador":
                menu_admin()
            elif rol == "cliente":
                menu_cliente(nombre)
        elif op == "2":
            registrar_usuario()
        elif op == "3":
            print("Saliendo del sistema.")
            break
        else:
            print("Opción inválida.")

main()
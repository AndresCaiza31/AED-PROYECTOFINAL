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
    return centros

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
    global CAMBIOS_CENTROS
    if not CAMBIOS_CENTROS:
        print("No hay cambios para guardar.")
        return

    lineas = [
        f"{c['nombre']},{c['region']},{c['costo']}"
        for c in cargar_centros()
    ]
    escribir_lineas(ARCHIVO_CENTROS, lineas)
    CAMBIOS_CENTROS = False
    print("Centros guardados correctamente.")

# ==========================================================
# GRAFOS – RUTAS
# ==========================================================

def cargar_rutas():
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
    return rutas

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
        print("3. Guardar cambios")
        print("4. Salir")

        op = input("Opción: ")
        if op == "1":
            agregar_centro()
        elif op == "2":
            listar_centros()
        elif op == "3":
            guardar_centros()
        elif op == "4":
            break
        else:
            print("Opción inválida.")
        pausar()

def menu_cliente(nombre):
    while True:
        print(f"\n=== MENÚ CLIENTE ({nombre}) ===")
        print("1. Ver jerarquía de centros")
        print("2. Calcular ruta óptima")
        print("3. Salir")

        op = input("Opción: ")
        if op == "1":
            mostrar_arbol()
        elif op == "2":
            o = input("Origen: ").strip()
            d = input("Destino: ").strip()
            dijkstra(o, d)
        elif op == "3":
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

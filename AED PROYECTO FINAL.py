import re
import os
import heapq

class NodoRegion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.subregiones = {}
        self.centros = []

def agregar_jerarquia(raiz, region, subregion, centro):
    if region not in raiz.subregiones:
        nuevo_nodo_region = NodoRegion(region)
        raiz.subregiones[region] = nuevo_nodo_region
    
    nodo_reg = raiz.subregiones[region]
    
    if subregion not in nodo_reg.subregiones:
        nuevo_nodo_sub = NodoRegion(subregion)
        nodo_reg.subregiones[subregion] = nuevo_nodo_sub
        
    nodo_sub = nodo_reg.subregiones[subregion]
    
    if centro not in nodo_sub.centros:
        nodo_sub.centros.append(centro)

def cargar_centros(ruta_archivo, grafo, raiz):
    if os.path.exists(ruta_archivo):
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) >= 6:
                        u1, u2 = datos[0], datos[1]
                        dist, costo = float(datos[2]), float(datos[3])
                        reg, subreg = datos[4], datos[5]
                        
                        if u1 not in grafo: grafo[u1] = {}
                        if u2 not in grafo: grafo[u2] = {}
                        grafo[u1][u2] = {'dist': dist, 'costo': costo, 'reg': reg, 'subreg': subreg}
                        grafo[u2][u1] = {'dist': dist, 'costo': costo, 'reg': reg, 'subreg': subreg}
                        
                        agregar_jerarquia(raiz, reg, subreg, u1)
                        agregar_jerarquia(raiz, reg, subreg, u2)
        except Exception as e:
            print(f"Error al cargar centros: {e}")

def guardar_centros(ruta_archivo, grafo):
    try:
        archivo = open(ruta_archivo, "w", encoding="utf-8")
        visitados = set()
        for u in grafo:
            for v in grafo[u]:
                if (v, u) not in visitados:
                    distancia = grafo[u][v]['dist']
                    costo = grafo[u][v]['costo']
                    region = grafo[u][v]['reg']
                    subregion = grafo[u][v]['subreg']
                    linea = f"{u},{v},{distancia},{costo},{region},{subregion}\n"
                    archivo.write(linea)
                    visitados.add((u, v))
        archivo.close()
        print("Cambios guardados exitosamente.")
    except Exception as e:
        print(f"Error al intentar guardar los datos: {e}")

def algoritmo_dijkstra(grafo, inicio, fin):
    cola_prioridad = []
    tupla_inicial = (0, inicio, [])
    heapq.heappush(cola_prioridad, tupla_inicial)
    visitados = set()
    
    while cola_prioridad:
        costo_acumulado, nodo_actual, camino = heapq.heappop(cola_prioridad)
        
        if nodo_actual in visitados:
            continue
            
        nuevo_camino = camino + [nodo_actual]
        
        if nodo_actual == fin:
            return costo_acumulado, nuevo_camino
            
        visitados.add(nodo_actual)
        
        if nodo_actual in grafo:
            for vecino in grafo[nodo_actual]:
                if vecino not in visitados:
                    costo_tramo = grafo[nodo_actual][vecino]['costo']
                    nuevo_costo = costo_acumulado + costo_tramo
                    heapq.heappush(cola_prioridad, (nuevo_costo, vecino, nuevo_camino))
                    
    return float("inf"), []

def validar_password(password):
    if len(password) < 6:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True

def validar_correo(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron, email):
        return True
    return False

# --- FUNCIONES DE LÓGICA DE ACCIÓN ---

def accion_registrar_ruta(grafo, arbol_regiones):
    print("\n--- REGISTRO DE NUEVA RUTA ---")    
    while True:
        centro_a = input("Ingrese el Centro Origen: ").strip().lower().title()
        centro_b = input("Ingrese el Centro Destino: ").strip().lower().title()

        if not (centro_a and all(x.isalpha() or x.isspace() for x in centro_a)):
            print("Error: El origen no es válido.")
            continue

        if not (centro_b and all(x.isalpha() or x.isspace() for x in centro_b)):
            print("Error: El destino no es válido.")
            continue

        if centro_a == centro_b:
            print("Error: El origen y el destino no pueden ser el mismo.")
            continue
        
        break

    while True:
        try:
            distancia = float(input("Ingrese la distancia en KM: "))
            if distancia > 0:
                break
            else:
                print("Error: La distancia debe ser un número positivo mayor a cero.")
                continue

        except ValueError:
            print("Error: Ingrese un valor numérico válido para la distancia.")

    while True:
        try:
            costo = float(input("Ingrese el costo de envío $: "))
            if costo >= 0:
                break
            else:
                print("Error: El costo no puede ser negativo.")
                continue

        except ValueError:
            print("Error: Ingrese un valor numérico válido para el costo.")

    while True:
        region = input("Ingrese la Región (Ej: Costa, Sierra, Amazonía): ").strip().lower().title()
        if region and all(x.isalpha() or x.isspace() for x in region):
            break
        else:
            print("Error: Ingrese una región válida.")
            continue

    while True:
        subregion = input("Ingrese la Subregión/Provincia (Ej: Guayas, Pichincha): ").strip().lower().title()
        if subregion and all(x.isalpha() or x.isspace() for x in subregion):
            break
        else:
            print("Error: Ingrese una subregión válida.")
            continue

    if centro_a not in grafo: grafo[centro_a] = {}
    if centro_b not in grafo: grafo[centro_b] = {}
    
    grafo[centro_a][centro_b] = {
        'dist': distancia, 
        'costo': costo, 
        'reg': region, 
        'subreg': subregion
    }
    grafo[centro_b][centro_a] = {
        'dist': distancia, 
        'costo': costo, 
        'reg': region, 
        'subreg': subregion
    }

    agregar_jerarquia(arbol_regiones, region, subregion, centro_a)

    print(f"\nRuta registrada: {centro_a} <-> {centro_b} ({distancia} KM, ${costo})")


def accion_eliminar_centro(grafo):
    print("\n--- Eliminar Centro ---")
    if not grafo:
        print("No existen registros.")
        return

    centro = input("Ingrese el nombre del centro a eliminar: ").strip().lower().title()
    if centro in grafo:
        grafo.pop(centro)
        for nodo in grafo:
            if centro in grafo[nodo]:
                grafo[nodo].pop(centro)
        print(f"El centro '{centro}' y sus rutas han sido eliminados.")
    else:
        print("El centro ingresado no existe.")

def accion_listar_centros(grafo):
    print("\n--- LISTADO DE CENTROS LOGÍSTICOS ---")
    if not grafo:
        print("Error. No se tienen centros registrados.")
        return

    centros_ordenados = sorted(grafo.keys())
    for centro in centros_ordenados:
        print(f"• {centro}")

def accion_calcular_ruta(grafo):
    origen = input("Punto de partida: ").strip().lower().title()
    destino = input("Punto de llegada: ").strip().lower().title()
    costo, camino = algoritmo_dijkstra(grafo, origen, destino)
    
    if origen not in grafo or destino not in grafo:
        print("Error: Uno de los centros (o ambos) no existen en el sistema.")
        return

    if camino:
        camino_formateado = " -> ".join(camino)
        print(f"Ruta más económica encontrada: {camino_formateado}")
        print(f"Inversión total requerida: ${costo}")
    else:
        print("No se encontró ninguna ruta disponible entre los puntos.")

def accion_ver_regiones(raiz):
    print("\n--- ORGANIZACIÓN TERRITORIAL ---")
    for nombre_reg, nodo_reg in raiz.subregiones.items():
        print(f"Región: {nombre_reg}")
        for nombre_sub, nodo_sub in nodo_reg.subregiones.items():
            centros_texto = ", ".join(nodo_sub.centros)
            print(f"   Subregión {nombre_sub}: [{centros_texto}]")

# ------------------ USUARIOS ------------------
def registrar_usuario(ruta_usuarios):
    print("\n--- REGISTRO DE NUEVA CUENTA ---")
    while True:
        nombre = input("Ingrese su nombre: ").strip().lower().title()
        
        if not nombre:
            print("El campo no puede estar vacío.")
            continue
            
        es_valido = True
        for caracter in nombre:
            if not (caracter.isalpha() or caracter.isspace()):
                es_valido = False
                break
                
        if es_valido:
            break
        else:
            print("Error: El nombre solo debe contener letras y espacios.")

    while True:
        correo = input("Ingrese su correo: ").strip().lower()
        if validar_correo(correo):
            break
        else:
            print("Error: Ingrese un formato de correo válido (ej: usuario@epn.edu.ec).")
    
    while True:
        password = input("Contraseña: ").strip()
        if not password:
            print("La contraseña no puede estar vacía")
            continue
        else:
            break
    
    while True:
        print("Seleccione el tipo de cuenta:")
        print("1. Cliente")
        print("2. Administrador")
        
        tipo_cuenta = input("Seleccione una opción (1-2): ").strip()
        
        if tipo_cuenta == "1":
            rol = "Cliente"
            break
        elif tipo_cuenta == "2":
            rol = "Admin"
            break
        else:
            print("Error: Selección no válida. Por favor, ingrese 1 o 2.")
    
    if validar_password(password):
        try:
            archivo = open(ruta_usuarios, "a", encoding="utf-8")
            linea = f"{correo},{password},{nombre},{rol}\n"
            archivo.write(linea)
            archivo.close()
            print(f"Cuenta de {rol} creada exitosamente para {nombre}.")
        except Exception as e:
            print(f"Error técnico al escribir el archivo: {e}")
            
    else:
        print("Error: La contraseña no cumple con los requisitos mínimos.")
        print("Debe contener al menos una letra mayúscula, una letra minúscula, un número y al menos 6 caracteres")

def login(ruta_usuarios):
    print("\n--- INICIO DE SESIÓN ---")
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()
    
    if os.path.exists(ruta_usuarios):
        try:
            archivo = open(ruta_usuarios, "r", encoding="utf-8")
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) >= 4:
                    if partes[0] == email and partes[1] == password:
                        archivo.close()
                        datos = {
                            "email": partes[0],
                            "nombre": partes[2],
                            "rol": partes[3]
                        }
                        return datos
            archivo.close()
        except Exception as e:
            print(f"Error al leer la base de datos de usuarios: {e}")
            
    return None

# --- MENÚS (ESTRUCTURA DE FLUJO) ---

def menu_admin(grafo, ruta_archivo, arbol_regiones):
    while True:
        print("\n--- PANEL DE CONTROL: ADMINISTRADOR ---")
        print("1. Registrar nueva ruta")
        print("2. Listar centros registrados")
        print("3. Eliminar centro logístico")
        print("4. Guardar cambios y cerrar sesión")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            accion_registrar_ruta(grafo, arbol_regiones)
        elif opcion == "2":
            accion_listar_centros(grafo)
        elif opcion == "3":
            accion_eliminar_centro(grafo)
        elif opcion == "4":
            guardar_centros(ruta_archivo, grafo)
            break
        else:
            print("Error. Debe ingresar un número entero del 1 al 4")

def menu_cliente(grafo, raiz, usuario):
    while True:
        nombre = usuario['nombre']
        print(f"\n--- SERVICIOS PARA: {nombre} ---")
        print("1. Calcular ruta de envío económica")
        print("2. Consultar mapa de regiones")
        print("3. Finalizar sesión")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            accion_calcular_ruta(grafo)
        elif opcion == "2":
            accion_ver_regiones(raiz)
        elif opcion == "3":
            break
        else:
            print("Error. Ingrese un número entero del 1 al 3")

def main():
    ruta_script = os.path.abspath(__file__)
    directorio = os.path.dirname(ruta_script)
    
    f_centros = os.path.join(directorio, "centros.txt")
    f_usuarios = os.path.join(directorio, "usuarios.txt")
    
    red_logistica = {}
    arbol_regiones = NodoRegion("Ecuador")
    
    cargar_centros(f_centros, red_logistica, arbol_regiones)
    
    while True:
        print("\n--- BIENVENIDO A POLIDELIVERY ---")
        print("1. Iniciar Sesión")
        print("2. Registrar Usuario")
        print("3. Salir del Programa")
        
        seleccion = input("Seleccione: ")
        
        if seleccion == "1":
            usuario = login(f_usuarios)
            if usuario:
                if usuario["rol"] == "Admin":
                    print("¡Credenciales correctas! Bienvenido al Sistema - ADMIN ")
                    menu_admin(red_logistica, f_centros, arbol_regiones)
                else:
                    print("¡Credenciales correctas! Bienvenido al Sistema - CLIENTE ")
                    menu_cliente(red_logistica, arbol_regiones, usuario)
            else:
                print("Acceso denegado: Credenciales no válidas.")
        elif seleccion == "2":
            registrar_usuario(f_usuarios)
        elif seleccion == "3":
            print("Saliendo de PoliDelivery. ¡Hasta pronto!")
            break
        else:
            print("Error. Ingrese un número entero del 1 al 3")

main()
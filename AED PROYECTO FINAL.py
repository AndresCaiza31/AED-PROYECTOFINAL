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

def agregar_conexion(grafo, u, v, dist, costo):
    if u not in grafo:
        grafo[u] = {}
    if v not in grafo:
        grafo[v] = {}
        
    grafo[u][v] = {'dist': dist, 'costo': costo}
    grafo[v][u] = {'dist': dist, 'costo': costo}

def cargar_centros(ruta_archivo, grafo, raiz):
    if os.path.exists(ruta_archivo):
        try:
            archivo = open(ruta_archivo, "r", encoding="utf-8")
            for linea in archivo:
                datos = linea.strip().split(",")
                if len(datos) >= 6:
                    u1 = datos[0]
                    u2 = datos[1]
                    dist = float(datos[2])
                    costo = float(datos[3])
                    reg = datos[4]
                    subreg = datos[5]
                    
                    agregar_conexion(grafo, u1, u2, dist, costo)
                    agregar_jerarquia(raiz, reg, subreg, u1)
                    agregar_jerarquia(raiz, reg, subreg, u2)
            archivo.close()
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
                    linea = f"{u},{v},{distancia},{costo},Sierra,Quito\n"
                    archivo.write(linea)
                    visitados.add((u, v))
        archivo.close()
        print("Cambios guardados exitosamente en el archivo.")
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

# --- FUNCIONES DE LÓGICA DE ACCIÓN ---

def accion_registrar_ruta(grafo):
    try:
        centro_a = input("Ingrese el Centro Origen: ")
        centro_b = input("Ingrese el Centro Destino: ")
        dist_input = input("Ingrese la distancia en KM: ")
        distancia = float(dist_input)
        costo_input = input("Ingrese el costo de envío $: ")
        costo = float(costo_input)
        
        agregar_conexion(grafo, centro_a, centro_b, distancia, costo)
        print("La ruta ha sido registrada en el sistema temporal.")
    except ValueError:
        print("Error: Se requieren valores numéricos para distancia y costo.")

def accion_eliminar_centro(grafo):
    centro = input("Ingrese el nombre del centro a eliminar: ")
    if centro in grafo:
        grafo.pop(centro)
        for nodo in grafo:
            if centro in grafo[nodo]:
                grafo[nodo].pop(centro)
        print(f"El centro '{centro}' y sus rutas han sido eliminados.")
    else:
        print("El centro ingresado no existe.")



# ------------------ USUARIOS ------------------
def registrar_usuario(ruta_usuarios):
    print("\n--- REGISTRO DE NUEVA CUENTA ---")
    nombre = input("Nombre completo: ")
    email = input("Correo electrónico: ")
    password = input("Contraseña: ")
    
    print("Seleccione el tipo de cuenta:")
    print("1. Cliente")
    print("2. Administrador")
    op_rol = input("Opción: ")
    
    rol = "Cliente"
    if op_rol == "2":
        rol = "Admin"
    
    if validar_password(password):
        try:
            archivo = open(ruta_usuarios, "a", encoding="utf-8")
            linea = f"{email},{password},{nombre},{rol}\n"
            archivo.write(linea)
            archivo.close()
            print(f"Cuenta de {rol} creada exitosamente para {nombre}.")
        except Exception as e:
            print(f"Error técnico al escribir el archivo: {e}")
    else:
        print("Error: La contraseña no cumple con los requisitos mínimos.")

def login(ruta_usuarios):
    print("\n--- INICIO DE SESIÓN ---")
    email = input("Email: ")
    password = input("Password: ")
    
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
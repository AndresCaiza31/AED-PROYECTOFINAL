import re

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
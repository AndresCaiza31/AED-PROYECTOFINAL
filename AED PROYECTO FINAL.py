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
#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import hashlib
import sys
import getpass
import time
import Ice
from threading import Thread
#Ice.loadSlice('iceflix.ice')
import IceFlix

def get_opcion():
    while(True):
        try:
            opcion = int(input("Eleccion:"))
            if opcion==1 or opcion==2:
                break
            else:
                    print("Introduce un número del 1 al 2")
        except ValueError:
                print("Introduce un número")    
    return opcion

# Método para obtener los tags de los identificadores que devuelve una búsqueda    
def mostrar_busqueda(lista, token_usuario, catalog):
    pos = 0
    print("Resultado de búsqueda:")
    while pos < len(lista):
        media = catalog.getTile(lista[pos],token_usuario)
        pos +=1
        print(f"{bcolors.OKBLUE}",pos, "->", media.info.name,".Tags:", media.info.tags,f"{bcolors.ENDC}")
    return 0
    
def mostrar_busqueda_anonima(lista):
    pos = 0
    print("Resultado de búsqueda:")
    
    while pos < len(lista):
        print(f"{bcolors.OKBLUE}",str(pos+1) + "-"+ lista[pos],f"{bcolors.ENDC}")
        pos+=1

def titulo_existe(titulo, lista, catalog, token_usuario):
    pos = 0
    while pos < len(lista):
        media = catalog.getTile(lista[pos],token_usuario)
        pos +=1
        if (media.info.name == titulo):
            return True
    return False

def tags_existen(lista_tags,id,token_usuario,catalog):
    media = catalog.getTile(id,token_usuario)
    tags_existentes = media.info.tags
    pos = 0
    valido = False
    while pos < len(lista_tags):
        if lista_tags[pos] in tags_existentes:
            print(lista_tags[pos], " está en los tags")
            valido = True
        else:
            valido = False
            return valido
    return valido

def get_tags(media_id, token_usuario,catalog):
    media = catalog.getTile(media_id,token_usuario)
    tags = media.info.tags
    return tags
    
def busqueda_por_nombres(token_usuario,catalog):
    print("¿Desea realizar una búsqueda exacta del nombre? Introduzca S/N ó s/n")
    correcto = False
    opcion = ""
    while(correcto is False):
        opcion = input("Opción elegida:")
        if opcion.lower()=="s" or opcion.lower()=="n":
            correcto = True
        else:
            print("Introduce N/S")
    name = input("Introduce la palabra a buscar:")
    lista = catalog.getTilesByName(name,opcion==1)  
    if(len(lista) == 0):
        print("No se han encontrado resultados en la búsqueda.")
    elif token_usuario == "":
        mostrar_busqueda_anonima(lista)
    else:
        mostrar_busqueda(lista,token_usuario,catalog)
    return lista     

def busqueda_por_tags(nombre_usuario,hassed_pass, token_usuario,authenticator,catalog):
    print("¿Desea realizar una búsqueda exacta de los tags? Introduzca S/N ó s/n")
    opcion = ""
    correcto = False
    while(correcto is False):
        opcion = input("Opción elegida:")
        if opcion.lower()=="s" or opcion.lower()=="n":
            correcto = True
        else:
            print("Introduce S/N ó s/n")
    tag_list = input("Introduce los tags separados por comas: ")
    tag_list = (tag_list.replace(" ","")).split(',')
    # Comprobamos si el token ha caducado o no, y si es así, lo actualizamos
    comprobar_token(nombre_usuario,token_usuario,authenticator)
    lista = catalog.getTilesByTags(tag_list,opcion.lower=="s",token_usuario)
    if(len(lista) == 0):
        print("No se han encontrado resultados para la búsqueda.")
    else:
        mostrar_busqueda(lista,token_usuario,catalog)
    return lista

def añadir_tags(titulo, token_usuario,nombre_usuario, hassed_pass,authenticator,catalog):
    print("Escribe los tags que quieres añadir a ", titulo, " separados por comas:",end=" ")
    tags = input()
    tags_list = (tags.replace(" ","")).split(',')
    comprobar_token(nombre_usuario,hassed_pass,token_usuario,authenticator)
    mediaId = catalog.getTilesByName(titulo,token_usuario)
    comprobar_token(nombre_usuario,hassed_pass,token_usuario,authenticator)
    catalog.addTags(mediaId[0],tags_list, token_usuario)
    
def comprobar_token(nombre_usuario, hassed_pass, token_usuario, authenticator):
    if(authenticator.isAuthorized(token_usuario) is False):
                    token_usuario = authenticator.refreshAuthorization(nombre_usuario,hassed_pass)
    
def obtener_seleccion_usuario(lista,token_usuario,catalog):
    if (len(lista) != 0):
        while(True):
            titulo = input("Introduce el título que quieres seleccionar:")
            if titulo_existe(titulo,lista,catalog,token_usuario) is False:
                print("No hay ningun archivo buscado anteriormente con ese nombre.")
            else:
                break
    else:
        titulo = ""
    return titulo

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
           
class ClientShell(cmd.Cmd):
        intro = 'Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones.'
        prompt: str = '(Off-line)'
        # ----- Opciones del menú del cliente ----- #
        def do_login(self,arg):
            'Iniciar sesión como usuario o administrador'
            print("¿Quieres iniciar sesión como usuario o administrador? Introduce 1 ó 2")
            print("1. Usuario\n2. Administrador")
            opcion = get_opcion()
                    
            # Login para usuario
            if opcion == 1:
                user_name = input("Introduce tu nombre de usuario:")
                password = getpass.getpass("Contraseña: ")
                hassed_pash = hashlib.sha256(password.encode()).hexdigest()
                try:
                    user_token = self.authenticator.refreshAuthorization(user_name, hassed_pash)
                except IceFlix.Unauthorized:
                    print(f"{bcolors.FAIL}El usuario o contraseña son incorrectos.{bcolors.ENDC} \n")
                else:
                    print(f"{bcolors.OKCYAN}Inicio de sesión completado.{bcolors.ENDC}")
                    t = Thread(target=NormalUserShell(self.main, user_name, hassed_pash, user_token).cmdloop())
                    t.start()
                    t.join()
            # Login para administrador
            else:
                token = getpass.getpass("Introduce el token administrativo: ")
                #is_admin = self.authenticator.isAdmin(token)
                is_admin = True
                if (is_admin):
                    print("Es admin... \n")
                    t = Thread(target=AdminShell(self.main, token).cmdloop())
                    t.start()
                    t.join()
                
        def do_busquedaPorNombre(self,arg):
            'Opción para realizar una búsqueda por el catálogo introduciendo un nombre a buscar'
            busqueda_por_nombres("",self.catalog)
            
        def do_salir(self,arg):
            'Opción para salir de la aplicación del cliente.'
            print("Saliendo del cliente...")
            return 1
        
        def __init__(self, main):
            super(ClientShell, self).__init__()
            self.main = main
            self.authenticator = main.getAuthenticator()
            self.catalog = main.getCatalog()

class AdminShell(cmd.Cmd):
    intro = 'Menu de administrador. Escribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(Admin on-line)'
    # ----- Opciones del menú del administrador ----- #
    def do_agregarUsuario(self,arg):
        'Añadir un usuario a la base de datos del programa.'
        user_name = input("Introduce el nombre del usuario a añadir:")
        password = getpass.getpass("Contraseña:")
        hassed_pash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.authenticator.addUser(user_name, hassed_pash, self.admin_token)
        except IceFlix.Unauthorized:
            print(f"{bcolors.FAIL}No se le ha permitido realizar esta acción.")
        except IceFlix.TemporaryUnavailable:
            print(f"{bcolors.FAIL}No puedes realizar esta acción.")
        
    def do_borrarUsuario(self,arg):
        'Eliminar un usuario de la base de datos del programa.'
        user_name = input("Introduce el nombre del usuario a eliminar:")
        try:
            self.authenticator.removeUser(user_name,self.admin_token)
        except IceFlix.TemporaryUnavailable:
            print(f"{bcolors.FAIL}No se le ha permitido realizar esta acción.")
        except IceFlix.Unauthorized:
            print(f"{bcolors.FAIL}No puedes realizar esta acción.")
            
    def do_renombrarArchivo(self,arg):
        'Renombrar un fichero del catálogo.'
        nombre = input("Introduce el nombre del archivo del catálogo que quieres editar:")
        lista = self.catalog.getTilesByName(nombre,True)
        if(len(lista) == 0):
            print("No se ha encontrado ningún archivo con este nombre.")
        else:
            nombre_nuevo = input("Introduce el nuevo nombre del archivo:")
            self.catalog.renameTile(lista[0],nombre_nuevo,self.admin_token)
    def do_eliminarArchivo(self,arg):
        'Eliminar un fichero del catálogo.'
        nombre = input("Introduce el nombre exacto del fichero a eliminar:")
        lista = self.catalog.getTilesByName(nombre,True)
        if(len(lista) == 0):
            print("No existe ningún archivo con el nombre indicado.")
        else:
            self.catalog.removeMedia(lista[0],self.file_service)
            
    def do_downloadFile(self,arg):
        'Descargar un fichero del catálogo.'
        print("Downloading a file")
    
    def do_logout(self,arg):
        'Cerrar sesión como administrador.'
        print("Cerrando sesión del administrador...")
        return 1
        
    def __init__(self, main, admin_token):
        super(AdminShell, self).__init__()
        self.main = main
        self.selection = False
        self.authenticator = main.getAuthenticator()
        self.catalog = main.getCatalog()
        #self.file_service = main.getFileService()
        self.admin_token = admin_token

class NormalUserShell(cmd.Cmd):
    intro = '\nEscribe "help" ó "?" para listar las opciones.'
    prompt: str = '(on-line)'
    
    def do_realizarBusqueda(self,arg):
        'Realizar una búsqueda por nombre o por tags'
        print("Elije una opción (introduce un número 1 o 2).")
        print("1. Búsqueda por nombre")
        print("2. Búsqueda por tags")
        opcion = get_opcion()
        # Búsqueda por nombre
        if(opcion==1):
            comprobar_token(self.user_name,self.hassed_pass,self.user_token,self.authenticator)
            self.lista = busqueda_por_nombres(self.user_token,self.catalog)
        # Búsqueda por tag
        else:
            self.lista = busqueda_por_tags(self.user_name, self.hassed_pass,self.user_token,self.authenticator,self.catalog) 
        if(len(self.lista) == 0):
               return 0
        self.titulo = obtener_seleccion_usuario(self.lista,self.user_token,self.catalog)
        media_id = self.catalog.getTilesByName(self.titulo,True)
        tags = get_tags(media_id[0],self.user_token,self.catalog)
        print("El título seleccionado ha sido", f"{bcolors.BOLD}",self.titulo, f"{bcolors.ENDC}con los tags -->", tags,"\n")
        print("¿Que acción quieres realizar? Introduce 1 ó 2:")
        print("1. Añadir tags")
        print("2. Eliminar tags")
        opcion = get_opcion()
        # Añadir tags
        if(opcion == 1):
           añadir_tags(self.titulo, self.user_token,self.user_name,self.hassed_pass,self.authenticator,self.catalog)
        # Eliminar tags
        else:
            if(len(tags) == 0):
                print(f"No se pueden eliminar tags de su selección ya que no tiene ningún tag.\nVolviendo al menú...\n")
                return 0
            existen = False
            while(existen is False):
                print("Escribe los tags que quieres eliminar a ", self.titulo, " separados por comas:",end=" ")
                tags = input()
                tags_list = (tags.replace(" ","")).split(',')
                comprobar_token(self.user_name,self.hassed_pass,self.user_token,self.authenticator)
                existen = tags_existen(tags_list,media_id[0],self.user_token,self.catalog)
                if tags == "":
                    print("\nNo se ha añadido ningún tag.")
                    break
                elif existen is True:
                    comprobar_token(self.user_name,self.hassed_pass,self.user_token,self.authenticator)
                    self.catalog.removeTags(media_id[0],tags_list, self.user_token)
       
    def do_logout(self,arg):
        'Cerrar sesión en el usuario'
        print("Cerrando sesión de", self.user_name)
        return 1
    
    def __init__(self, main, user_name, hassed_pass, user_token):
        super(NormalUserShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.catalog = main.getCatalog()
        self.user_name = user_name
        self.hassed_pass = hassed_pass
        self.user_token = user_token
        self.lista = ""
        self.titulo = ""
        
class Client(Ice.Application):
    # ----- Clase Cliente ----- #
    def run(self, argv):
        print("Cliente iniciado:")
        if(len(sys.argv) != 2):
            print("Tienes que insertar el proxy del main. \nSaliendo del programa...")
            return -1

        counter = 0
        comprobacion = False
        while(counter != 3):
            counter +=1
            try:
                proxy = self.communicator().stringToProxy(argv[1])
                main = IceFlix.MainPrx.checkedCast(proxy)
                comprobacion = True
            except:
                print("Intento número",counter,"de conexión fallido por el proxy.")
                time.sleep(5)
            else:
                break
        if not comprobacion:
            raise RuntimeError('Se han realizado todos los intentos de conexión. Error con el proxy')
        else:
            ClientShell(main).cmdloop()
        
        return -1

sys.exit(Client().main(sys.argv))
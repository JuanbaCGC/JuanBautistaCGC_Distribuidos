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
    
    # Método para obtener los tags de los identificadores que devuelve una búsqueda    
def mostrar_busqueda(lista, token_usuario, catalog):
    pos = 0
    print("Resultado de búsqueda:")
    while pos < len(lista):
        media = catalog.getTile(lista[pos],token_usuario)
        pos +=1
        print(pos, "->", media.info.name,".Tags:", media.info.tags)
    return 0
    
def mostrar_busqueda_anonima(lista):
    pos = 0
    print("Resultado de búsqueda:")
    while pos < len(lista):
        print(str(pos+1) + "-"+ lista[pos])
        pos+=1
    return 0

def titulo_existe(nombre, lista, catalog, token_usuario):
    pos = 0
    while pos < len(lista):
        media = catalog.getTile(lista[pos],token_usuario)
        pos +=1
        if (media.info.name == nombre):
            return True
    return False

def tags_existen(lista_tags,id,token_usuario,catalog):
    media = catalog.getTile(id,token_usuario)
    tags_existentes = media.info.tags
    pos = 0
    valido = False
    while pos < len(lista_tags):
        if(lista_tags[pos] in tags_existentes):
            valido = True
        else:
            valido = False
            return valido
    return valido

def get_tags(media_id, token_usuario,catalog):
    media = catalog.getTile(media_id,token_usuario)
    print(media.info.tags)
    
def busqueda_por_nombres(token_usuario,catalog):
    name = input("Introduce el nombre para realizar la búsqueda:")
    print("Elije una opción (introduce un número 1 o 2).")
    print("1. Búsqueda por término exacto.")
    print("2. Búsqueda títulos que incluyan la palabra a buscar.")
    correcto = False
    while(correcto is False):
        try:
            opcion = int(input())
        except ValueError:
            print("Debes introducir un número.")
        if opcion==1 or opcion==2:
            correcto = True
        else:
            print("Introduce un número del 1 al 2.")
    lista = catalog.getTilesByName(name,opcion==1)  
    if(len(lista) == 0):
        print("No se han encontrado resultados en la búsqueda.")
    elif token_usuario == "":
        mostrar_busqueda_anonima(lista)
    else:
        mostrar_busqueda(lista,token_usuario,catalog)
    return lista        

class ClientShell(cmd.Cmd):
        intro = 'Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones. \n'
        prompt: str = '(Off-line)'
        # ----- Opciones del menú del cliente ----- #
        def do_adminLogin(self, arg):
            'Inicia sesión como administrador para gestionar la aplicación distribuida'
            token = input("Introduce el token:")
            #is_admin = self.authenticator.isAdmin(token)
            is_admin = True
            if (is_admin):
                print("Es admin... \n")
                t = Thread(target=AdminShell(self.main, token).cmdloop())
                t.start()
                t.join()

        def do_userLogin(self,arg):
            'Inicia sesión como usuario para hacer búsquedas por nombres y por tags'
            user_name = input("Introduce tu nombre de usuario:")
            password = getpass.getpass("Contraseña: ")
            hassed_pash = hashlib.sha256(password.encode()).hexdigest()
            try:
                user_token = self.authenticator.refreshAuthorization(user_name, hassed_pash)
            except IceFlix.Unauthorized:
                print("El usuario o contraseña son incorrectos.")
            else:
                t = Thread(target=NormalUserShell(self.main, user_name, hassed_pash, user_token).cmdloop())
                t.start()
                t.join()

        def do_searchByName(self,arg):
            'Opción para realizar una búsqueda por el catálogo introduciendo un nombre a buscar'
            busqueda_por_nombres("",self.catalog)
            
        def do_exit(self,arg):
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
    def do_addUser(self,arg):
        'Añadir un usuario a la base de datos del programa.'
        user_name = input("Introduce el nombre del usuario a añadir:")
        password = getpass.getpass("Contraseña:")
        hassed_pash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.authenticator.addUser(user_name, hassed_pash, self.admin_token)
        except IceFlix.Unauthorized:
            print("No se ha añadido al usuario, token de administrador no válido.")
        except IceFlix.TemporaryUnavailable:
            print("No puedes realizar esta acción.")
        
    def do_removeUser(self,arg):
        'Eliminar un usuario de la base de datos del programa.'
        user_name = input("Introduce el nombre del usuario a eliminar:")
        try:
            self.authenticator.removeUser(user_name,self.admin_token)
        except IceFlix.TemporaryUnavailable:
            print("El nombre del usuario introducido no existe.")
        except IceFlix.Unauthorized:
            print("No puedes realizar esta acción.")
            
    def do_renameFile(self,arg):
        'Renombrar un fichero del catálogo.'
        media = input("Introduce el nombre del archivo del catálogo que quieres editar: ")
        nombre_nuevo = input("Introduce el nuevo nombre del archivo:")
        try:
            self.catalog.getTile(media,self.admin_token)
        except IceFlix.WrongMediaId:
            print("No se ha encontrado ningún archivo en el catálogo con el id ", media,".")
        except:
            print("Error al obtener el archivo del catálogo.")
        
    def do_deleteFile(self,arg):
        'Eliminar un fichero del catálogo.'
        id = input("Introduce el id del archivo del catálogo a eliminar:")
        lista = self.catalog.getTilesByName(id,True)
        if(len(lista) == 0):
            print("No existe ningún archivo con el id indicado")
        else:
            self.catalog.removeMedia(id,self.file_service)
            
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
        self.file_service = main.getFileService()
        self.admin_token = admin_token

class NormalUserShell(cmd.Cmd):
    intro = 'Inicio de sesión completado. \nEscribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(on-line)'
    def do_SearchByName(self,arg):
        'Búsqueda por nombre en los archivos del catálogo.'
        # ¿Se debería de comprobar el token al hacer búsqueda por nombre un usuario normal?
        self.lista = busqueda_por_nombres(self.user_token,self.catalog)
        
    def do_SearchByTags(self,arg):
        'Búsqueda por tags en los archivos del catálogo.'
        tag_list = input("Introduce los tags separados por comas: ")
        tag_list = tag_list.split(sep=',')
        print("Elije una opción (introduce un número 1 o 2).")
        print("1. Búsqueda de todos los tags")
        print("2. Búsqueda que incluya algún tag")
        correcto = False
        while(correcto is False):
            try:
                opcion = int(input("Eleccion:"))
                if opcion==1 or opcion==2:
                    correcto = True
                else:
                    print("Introduce un número del 1 al 2")
            except ValueError:
                print("Introduce un número")
        # Comprobamos si el token ha caducado o no, y si es así, lo actualizamos
        if(self.authenticator.isAuthorized(self.user_token) is False):
            self.user_token = self.authenticator.refreshAuthorization(self.user_name,self.hassed_pas)
        
        lista = self.catalog.getTilesByTags(tag_list,opcion==1,self.user_token)
        if(len(lista) == 0):
            print("No se han encontrado resultados para la búsqueda")
        else:
            self.lista = busqueda_por_nombres(self.user_token,self.catalog)
            
    def do_selectionTile(self,arg):
        'Seleccionar un título para gestionarlo'
        if(len(self.lista) == 0):
            print("No se ha realizado ninguna búsqueda anteriormente, debes realizar una antes de seleccionar una película.")
        else:
            while(True):
                tile = input("Introduce la película que quieres selecionar:")
                if titulo_existe(tile,self.lista,self.catalog, self.user_token) is False:
                    print("No hay ninguna película buscada anteriormente con ese nombre.")
                else:
                    print("La película", tile, "ha sido seleccionada correctamente.")
                    self.selection = True
                    self.tile = tile
                    break
    
    def do_addTags(self,arg):
        if(self.tile == ""):
            print("Para añadir algún tag tienes que haber seleccionado antes algún título")
            return 0
        print("Escribe los tags que quieres añadir a ", self.tile, " separados por comas:",end=" ")
        tags = input()
        tags_list = (tags.replace(" ","")).split(',')
        if(self.authenticator.isAuthorized(self.user_token) is False):
            self.user_token = self.authenticator.refreshAuthorization(self.user_name,self.hassed_pas)
        mediaId = self.catalog.getTilesByName(self.tile,self.user_token)
        self.catalog.addTags(mediaId[0],tags_list, self.user_token)
        
    def do_eliminarTags(self,arg):
        if(self.tile == ""):
            print("Para añadir algún tag tienes que haber seleccionado antes algún título")
            return 0
        if(self.authenticator.isAuthorized(self.user_token) is False):
            self.user_token = self.authenticator.refreshAuthorization(self.user_name,self.hassed_pas)
        media_id = self.catalog.getTilesByName(self.tile,self.user_token)
        valido = False
        while(valido is False):
            print("Escribe los tags que quieres eliminar a ", self.tile, " separados por comas:",end=" ")
            tags = input()
            tags_list = (tags.replace(" ","")).split(',')
            valido = tags_existen(tags_list,media_id[0],self.user_token,self.catalog)
            if tags == "":
                print("\nNo se ha añadido ningún tag.")
                break
            elif valido is False:
                print("El título ", self.tile, " no tiene los tags que has introducido para eliminarlos.")
                # Actualizamos el token si es necesario
                if(self.authenticator.isAuthorized(self.user_token) is False):
                    self.user_token = self.authenticator.refreshAuthorization(self.user_name,self.hassed_pas)
                print(self.tile, "tiene los siguientes tags --> ", get_tags(media_id[0],self.user_token,self.catalog))
                print("Introduce los tags a eliminar de nuevo:")
                
        if valido is True:
            if(self.authenticator.isAuthorized(self.user_token) is False):
                self.user_token = self.authenticator.refreshAuthorization(self.user_name,self.hassed_pas)
        
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
        self.hassed_pas = hassed_pass
        self.user_token = user_token
        self.lista = ""
        self.tile = ""
        
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
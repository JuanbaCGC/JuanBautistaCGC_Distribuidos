#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import hashlib
import sys
import getpass
import time
import Ice
from threading import Thread
Ice.loadSlice('iceflix.ice')
import IceFlix

def show_sequence(lista_nombres):
    pos=0
    while pos < len(lista_nombres):
        print(str(pos+1) + "-"+ lista_nombres[pos])
        pos+=1

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
            name = input("Introduce el nombre para realizar la búsqueda:")
            print("Elije una opción (introduce un número 1 o 2).")
            print("1. Búsqueda por término exacto.")
            print("2. Búsqueda títulos que incluyan la palabra a buscar.")
            correcto = False
            while(correcto is False):
                try:
                    opcion = int(input())
                    if opcion==1 or opcion==2:
                        correcto = True
                    else:
                        print("Introduce un número del 1 al 2.")
                except ValueError:
                    print("Debes introducir un número.")
            
            lista = self.catalog.getTilesByName(name,opcion==1)  
            if(len(lista) == 0):
                print("No se han encontrado resultados en la búsqueda.")
            else:
                show_sequence(lista)
            
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
        user_name = input("Introduce el nombre del usuario a eliminar:")
        try:
            self.authenticator.removeUser(user_name,self.admin_token)
        except IceFlix.TemporaryUnavailable:
            print("El nombre del usuario introducido no existe.")
        except IceFlix.Unauthorized:
            print("No puedes realizar esta acción.")
            
    def do_renameFile(self,arg):
        media = input("Introduce el nombre del archivo del catálogo que quieres editar: ")
        nombre_nuevo = input("Introduce el nuevo nombre del archivo:")
        try:
            self.catalog.getTile(media,self.admin_token)
        except IceFlix.WrongMediaId:
            print("No se ha encontrado ningún archivo en el catálogo con el id ", media,".")
        except:
            print("Error al obtener el archivo del catálogo.")
        
    def do_deleteFile(self,arg):
        id = input("Introduce el id del archivo del catálogo a eliminar:")
        lista = self.catalog.getTilesByName(id,True)
        if(len(lista) == 0):
            print("No existe ningún archivo con el id indicado")
        else:
            self.catalog.removeMedia(id,self.file_service)
            
    def do_downloadFile(self,arg):
        print("Downloading a file")
        
    def do_logout(self,arg):
        print("Cerrando sesión del administrador...")
        return 1
        
    def __init__(self, main, admin_token):
        super(AdminShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.catalog = main.getCatalog()
        self.file_service = main.getFileService()
        self.admin_token = admin_token

class NormalUserShell(cmd.Cmd):
    intro = 'Inicio de sesión completado. \nEscribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(on-line)'
    
    def do_SearchByName(self,arg):
        print("Buscando archivos por nombre...")
        
    def do_SearchByTags(self,arg):
        tag_list = input("Introduce los tags separados por comas: ")
        tag_list = tag_list.split(sep=',')
        print("AAA->",self.user_name)
        print("Elije una opción (introduce un número 1 o 2).")
        print("1. Búsqueda de todos los tags")
        print("2. Búsqueda que incluya algún tag")
        correcto = False
        while(correcto is False):
            try:
                opcion = int(input())
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
            show_sequence(lista)
        
    def do_logout(self,arg):
        print("Cerrando sesión del usuario", self.user_name)
        return 1
    
    def __init__(self, main, user_name, hassed_pass, user_token):
        super(NormalUserShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.catalog = main.getCatalog()
        self.user_name = user_name
        self.hassed_pas = hassed_pass
        self.user_token = user_token
        
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
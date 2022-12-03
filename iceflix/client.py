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
            print("Introduce el token:")
            token = input()
            #is_admin = self.authenticator.isAdmin(token)
            is_admin = True
            if (is_admin):
                print("Es admin... \n")
                t = Thread(target=AdminShell(self.main, token).cmdloop())
                t.start()
                t.join()

        def do_userLogin(self,arg):
            print("Introduce tu nombre de usuario:")
            user_name = input()
            print("Introduce la contraseña:")
            password = getpass.getpass("Contraseña: ")
            pass_hash = hashlib.sha256(password.encode()).hexdigest()
            #user_token = ""
            try:
                user_token = self.authenticator.refreshAuthorization(user_name, pass_hash)
            except IceFlix.Unauthorized:
                print("El usuario o contraseña son incorrectos.")
            else:
                t = Thread(target=NormalUserShell(self.main, user_name,user_token).cmdloop())
                t.start()
                t.join()

        def do_searchByName(self,arg):
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
                    print("Introduce un número.")
            
            lista = self.catalog.getTilesByName(name,opcion==1)  
            if(len(lista) == 0):
                print("No se han encontrado resultados en la búsqueda.")
            else:
                show_sequence(lista)
            
        def do_exit(self,arg):
            print("Saliendo del cliente...")
            return 1
        
        def __init__(self, main):
            super(ClientShell, self).__init__()
            self.main = main
            self.authenticator = main.getAuthenticator()
            self.catalog = main.getCatalog()

class AdminShell(cmd.Cmd):
    intro = 'Menu de administrador. Escribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(Admin loggeado)'
    # ----- Opciones del menú del administrador ----- #
    def do_addUser(self,arg):
        print("Introduce el nombre del usuario a añadir:")
        user_name = input()
        print("Introduce la contraseña:")
        password = getpass.getpass("Contraseña: ")
        hassed_pash = hashlib.sha256(password.encode()).hexdigest()
        self.authenticator.addUser(user_name, hassed_pash, self.admin_token)
        
    def do_removeUser(self,arg):
        print("Introduce el nombre del usuario a eliminar:")
        user_name = input()
        self.authenticator.removeUser(user_name,self.admin_token)
        
    def do_renameFile(self,arg):
        print("Renaming a file")
        
    def do_deleteFile(self,arg):
        print("Deleting a file")
        
    def do_downloadFile(self,arg):
        print("Downloading a file")
        
    def do_logout(self,arg):
        print("Cerrando sesión del administrador...")
        return 1
        
    def __init__(self, main, admin_token):
        super(AdminShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.admin_token = admin_token

class NormalUserShell(cmd.Cmd):
    intro = 'Inicio de sesión completado. \nEscribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(on-line)'
    
    def do_SearchByName(self,arg):
        print("Buscando archivos por nombre...")
        
    def do_SearchByTag(self,arg):
        tag_list = input("Introduce los tags separados por comas: ")
        tag_list = tag_list.split(sep=',')
        print("AAA->",tag_list)
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
        lista = self.catalog.getTilesByTags(tag_list,opcion==1,self.user_token)
        if(len(lista) == 0):
            print("No se han encontrado resultados para la búsqueda")
        else:
            show_sequence(lista)
        
    def do_logout(self,arg):
        print("Cerrando sesión del usuario")
        return 1
    
    def __init__(self, main, user_name,user_token):
        super(NormalUserShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.catalog = main.getCatalog()
        self.user_name = user_name
        self.user_token = user_token
        
class Client(Ice.Application):
    # ----- Clase Cliente -----
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
            raise RuntimeError('Error con el proxy')
        else:
            ClientShell(main).cmdloop()
        
        return -1

sys.exit(Client().main(sys.argv))
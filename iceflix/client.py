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

class ClientShell(cmd.Cmd):
        intro = 'Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones. \n'
        prompt: str = '(Client menu)'
        # ----- Opciones del menú del cliente ----- #
        def do_adminLogin(self, arg):
            print("Introduce el token:")
            token = input()
            is_admin = self.authenticator.isAdmin(token)
            # is_admin = True
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
            user_token = self.authenticator.refreshAuthorization(user_name, pass_hash)
            t = Thread(target=NormalUserShell(self.main, user_token).cmdloop())
            t.start()
            t.join()

        def do_exit(self,arg):
            print("Saliendo del cliente...")
            return 1
        
        def __init__(self, main):
            super(ClientShell, self).__init__()
            self.main = main
            self.authenticator = main.getAuthenticator()

class AdminShell(cmd.Cmd):
    intro = 'Menu de administrador. Escribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(Admin menu)'
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
    prompt: str = '(User)'
    
    def do_TilesByName(self,arg):
        print("Buscando archivos por nombre...")
        
    def do_TilesByTag(self,arg):
        print("Buscando archivos por tag...")
        
    def do_logout(self,arg):
        print("Cerrando sesión del usuario")
        return 1
    
    def __init__(self, main, user_token):
        super(NormalUserShell, self).__init__()
        self.main = main
        self.authenticator = main.getAuthenticator()
        self.user_token = user_token
        
class Client(Ice.Application):
    # ----- Clase Cliente -----
    def run(self, argv):
        print("Cliente iniciado:")
        if(len(sys.argv) != 2):
            print("Tienes que insertar el proxy del main. \nSaliendo del programa...")
            return -1

        counter = 0
        checked = False
        #main=""
        proxy = self.communicator().stringToProxy(argv[1])
        while(counter != 3 or checked):
            counter+=1
            try:
                main = IceFlix.MainPrx.checkedCast(proxy)
                checked = True
            except:
                print("Intento número",counter,"de conexión fallido por el proxy.")
                time.sleep(5)

        if(checked):
            ClientShell(main).cmdloop()
        else:
            print("Se ha alcanzado el máximo de intentos de conexión. \nSaliendo del programa del cliente...")
            return -1

sys.exit(Client().main(sys.argv))
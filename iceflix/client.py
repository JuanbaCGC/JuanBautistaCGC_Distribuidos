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
        # ----- Opciones del menú -----
        def do_adminLogin(self, arg):
            print("Introduce el token:")
            token = input()
            is_admin = self.authenticator.isAdmin(token)
            is_admin = True
            if (is_admin):
                print("Es admin... \n")
                t = Thread(target=AdminShell(self.main).cmdloop())
                t.start()
                t.join()
                

        def do_userLogin(self,arg):
            print("Introduce tu nombre de usuario:")
            user_name = input()
            print("Introduce ahora la contraseña:")
            password = getpass.getpass("Contraseña: ")
            pass_hash = hashlib.sha256(password.encode()).hexdigest()
            print(pass_hash)
            self.authenticator.refreshAuthorization(user_name, pass_hash)

        

        def __init__(self, main):
            super(ClientShell, self).__init__()
            self.main = main
            self.authenticator = main.getAuthenticator()

class AdminShell(cmd.Cmd):
    intro = 'Menu de administrador. Escribe "help" ó "?" para listar las opciones. \n'
    prompt: str = '(Admin menu)'
        
    def do_addUser(self,arg):
        print("Adding a user")
        
    def do_deleteUser(self,arg):
        print("Deleting a user")
        
    def do_renameFile(self,arg):
        print("Renaming a file")
        
    def do_deleteFile(self,arg):
        print("Deleting a file")
        
    def do_downloadFile(self,arg):
        print("Downloading a file")
        
    def do_logout(self,arg):
        print("Loging out...")
        return 1
        
    def __init__(self, main):
            super(AdminShell, self).__init__()
            self.main = main
            self.authenticator = main.getAuthenticator()

class Client(Ice.Application):
    # ----- Clase Cliente -----

    def run(self, argv):
        print("Cliente iniciado:")
        if(len(sys.argv) != 2):
            print("Tienes que insertar el proxy del main. \nSaliendo del programa...")
            return -1

        counter = 0
        checked = False
        main=""
        proxy = self.communicator().stringToProxy(argv[1])
        while(counter != 3 or checked):
            counter+=1
            try:
                main = IceFlix.MainPrx.checkedCast(proxy)
                checked = True
            except:
                print("Intento número ",counter," de conexión fallido por el proxy.")
                time.sleep(1)
                continue

        if(checked):
            ClientShell(main).cmdloop()
        else:
            print("Saliendo del programa del cliente...")
        return -1

sys.exit(Client().main(sys.argv))
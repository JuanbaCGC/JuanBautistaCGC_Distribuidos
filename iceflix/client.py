#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import sys
import getpass
import Ice
Ice.loadSlice('iceflix.ice')

class ClientShell(cmd.Cmd):
        intro = 'Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones. \n'
        prompt: str = '(Client)'
        # ----- Opciones del menú -----
        def do_adminLogin(self, arg):
            print("Introduce tu nombre de usuario:")
            user_name = input()
            print("Introduce ahora la contraseña:")
            password = getpass.getpass("Contraseña: ")
        
        def do_userLogin(self,arg):
            print("Introduce tu nombre de usuario:")
            user_name = input()
            print("Introduce ahora la contraseña:")
            password = getpass.getpass("Contraseña: ")
        
        def do_nameSearch(self,arg):
            print("Vas a buscar por nombre...")
    
        def do_logout(self,arg):
            print("Vas a salir de tu usuario...")
            return True

class Client(Ice.Application):
    # ----- Clase Cliente -----
        
    def run(self, argv):
        ClientShell().cmdloop()
        
sys.exit(Client().main(sys.argv))
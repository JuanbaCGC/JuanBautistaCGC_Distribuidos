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
        print("Cliente iniciado:")
        if(len(sys.argv) != 2):
            print("Tienes que insertar el proxy del main. \nSaliendo del programa...")
            return -1
        
        counter = 0
        if(counter != 3):
            counter+=1
            proxy = self.communicator().stringToProxy(argv[1])
            main = IceFlix.MainPrx.checkedCast(proxy)
            
            if not main:
                raise TemporaryUnavailable('Invalid proxy: ', proxy)
            
        ClientShell().cmdloop()
        
sys.exit(Client().main(sys.argv))
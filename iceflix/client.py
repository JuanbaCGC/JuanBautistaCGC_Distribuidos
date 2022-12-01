#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import sys
import getpass
import time
import Ice
Ice.loadSlice('iceflix.ice')
import IceFlix

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

        # def do_nameSearch(self,arg):
        #     print("Introduce el nombre por búsqueda...")

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
        checked = False
        proxy = self.communicator().stringToProxy(argv[1])
        while(counter != 3 or checked == False):
            counter+=1
            try:
                main = IceFlix.MainPrx.checkedCast(proxy)
            except IceFlix.Exception:
                print("LSJAFLSDJFSL")
                continue
            if not main:
                print("Intento número ",counter," de conexión fallido por el proxy.")
                time.sleep(5)
            else:
                checked = True


        ClientShell().cmdloop()

sys.exit(Client().main(sys.argv))
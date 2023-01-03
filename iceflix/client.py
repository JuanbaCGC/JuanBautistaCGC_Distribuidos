#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import hashlib
import sys
import getpass
import time
import threading
from threading import Thread
import tkinter.filedialog
import Ice
import IceFlix
import IceStorm

# pylint: disable=too-many-arguments

def get_opcion(opciones):
    """Método para obtener la opción que introduzca el usuario"""
    while True:
        try:
            opcion = int(input("Eleccion:"))
            if opcion in opciones:
                break
            else:
                    print("Introduce un número del 1 al 2")
        except ValueError:
                print("Introduce un número.")    
    return opcion
   
def mostrar_busqueda(lista, token_usuario, catalog):
    """Método para obtener los tags de los identificadores que devuelve una búsqueda """
    pos = 0
    print("Hay",len(lista),"resultados:")
    while pos < len(lista):
        try:
            media = catalog.getTile(lista[pos],token_usuario)
        except:
            print(f"{bcolors.FAIL}Error con el catalog.{bcolors.ENDC}")
        else:
            
            print(f"{bcolors.OKBLUE}",pos+1, "->", media.info.name,".Tags:", 
                  media.info.tags, ".Id:",lista[pos],f"{bcolors.ENDC}")
            pos +=1
    
def mostrar_busqueda_anonima(lista):
    """Método para recorrer una lista de un usuario no logeado"""
    pos = 0
    print("Hay",len(lista),"resultados:")
    while pos < len(lista):
        print(f"{bcolors.OKBLUE}",str(pos+1),"-",lista[pos],f"{bcolors.ENDC}")
        pos+=1

def titulo_existe(titulo, lista, catalog, token_usuario):
    """Método para saber si un título de un archivo está en una lista o no"""
    try:
        existe = any(catalog.getTile(media_id, token_usuario).info.name == titulo for media_id in lista)
    except:
        print(f"{bcolors.FAIL}Error con el catalog.{bcolors.ENDC}")
        return False
    return existe

def tags_existen(lista_tags,id,token_usuario,catalog):
    """Método para saber si una serie de tags existen en los tags de un archivo"""
    try:
        media = catalog.getTile(id,token_usuario)
    except:
        print(f"{bcolors.FAIL}Error con el catalog.{bcolors.ENDC}")
        return False

    return all(tag in media.info.tags for tag in lista_tags)

def get_tags(media_id, token_usuario,catalog):
    """Método para obtener los tags de un archivo"""
    try:
        media = catalog.getTile(media_id,token_usuario)
    except:
        print(f"{bcolors.FAIL}Error con el catalog.{bcolors.ENDC}")
        tags = ""
    else:
        tags = media.info.tags
    return tags
    
def busqueda_por_nombres(token_usuario,catalog):
    """Método para realizar una búsqueda en el catálogo por nombre"""
    opcion = input("¿Desea realizar una búsqueda exacta del nombre? Introduzca SI/NO ó si/no: ").lower()
    while opcion!= "si" and opcion != "no":
        opcion = input("Opción no válida. ¿Desea realizar una búsqueda exacta del nombre? Introduzca SI/NO ó si/no: ")
    name = input("Introduce la palabra a buscar: ")
    lista = catalog.getTilesByName(name, opcion == "si")  
    if len(lista) == 0:
        print("No se han encontrado resultados en la búsqueda.")
    elif token_usuario == "":
        mostrar_busqueda_anonima(lista)
    else:
        mostrar_busqueda(lista,token_usuario,catalog)
    return lista

def busqueda_por_tags(nombre_usuario,hassed_pass, token_usuario,authenticator,catalog):
    """Método para realizar una búsqueda por tags"""
    opcion = input("¿Desea realizar una búsqueda exacta de los tags? Introduzca SI/NO ó si/no: ").lower()
    while opcion!="si" and opcion!="no":
        opcion = input("Opción no válida. ¿Desea realizar una búsqueda exacta de los tags? Introduzca SI/NO ó si/no: ")
    tag_list = input("Introduce los tags separados por comas: ")
    tag_list = (tag_list.replace(" ","")).split(',')
    token_usuario = comprobar_token(nombre_usuario,hassed_pass,token_usuario,authenticator)
    lista = catalog.getTilesByTags(tag_list,opcion=="si",token_usuario)
    if len(lista) == 0:
        print("No se han encontrado resultados para la búsqueda.")
    else:
        mostrar_busqueda(lista,token_usuario,catalog)
    return lista

def añadir_tags(titulo, token_usuario,nombre_usuario, hassed_pass,authenticator,catalog):
    """Método para añadir tags a un archivo seleccionado"""
    print("Escribe los tags que quieres añadir a ", titulo, " separados por comas:",end=" ")
    tags = input()
    tags_list = (tags.replace(" ","")).split(',')
    token_usuario = comprobar_token(nombre_usuario,hassed_pass,token_usuario,authenticator)
    media_id = catalog.getTilesByName(titulo,token_usuario)
    token_usuario = comprobar_token(nombre_usuario,hassed_pass,token_usuario,authenticator)
    catalog.addTags(media_id[0],tags_list, token_usuario)
    print(f"{bcolors.OKCYAN}Se han añadido los tags indicados.\n{bcolors.ENDC}")
    
def comprobar_token(nombre_usuario, hassed_pass, token_usuario, authenticator):
    """Método para actualizar el token de los usuarios cuando sea necesario"""
    if(authenticator.isAuthorized(token_usuario) is False):
        return authenticator.refreshAuthorization(nombre_usuario,hassed_pass)
    return token_usuario

def obtener_seleccion_usuario(lista,token_usuario,catalog):
    """Método para obtener el título que selecciona un usuario"""
    if not lista:
        return ""
    titulo = ""
    while not titulo_existe(titulo, lista, catalog, token_usuario):
        titulo = input("Introduce el título que quieres seleccionar: ")
    return titulo

class bcolors:
    """Clase para hacer prints de distintas formas"""
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class Uploader(IceFlix.FileUploader):
    """Clase para realizar la subida de archivos por el administrador"""
    def receive(self,size):
        return self.f.read(size)
        
    def close(self, user_token):
        if self.authenticator.isAdmin(user_token):
            self.f.close()
        
    def __init__(self,main):
        self.authenticator = main.getAuthenticator()
        self.filename = tkinter.filedialog.askopenfilename()
        self.f = open(self.filename)

class ClientShell(cmd.Cmd):
        """Clase que implementa el menú de un usuario no logeado"""
        intro = 'Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones.\nEscribe help <opcion> para obtener un resumen.'
        prompt: str = '(Off-line)'
        
        # ----- Opciones del menú del cliente ----- #
        def do_login(self,arg):
            """Iniciar sesión como usuario o administrador"""
            if self.conexion is False:
                print(f"{bcolors.FAIL}No se ha podido conectar con los servicios. Saliendo de IceFlix{bcolors.ENDC}")
                self.broker.shutdown()
                return 1
            
            print("¿Quieres iniciar sesión como usuario o administrador? Introduce 1 ó 2")
            print("1. Usuario\n2. Administrador")
            opcion = get_opcion([1,2])
                    
            # Login para usuario
            if opcion == 1:
                nombre_usuario = input("Introduce tu nombre de usuario:")
                password = getpass.getpass("Contraseña: ")
                hassed_pass = hashlib.sha256(password.encode()).hexdigest()
                try:
                    token_usuario = self.authenticator.refreshAuthorization(nombre_usuario, hassed_pass)
                except IceFlix.Unauthorized:
                    print(f"{bcolors.FAIL}El usuario o contraseña son incorrectos.{bcolors.ENDC} \n")
                else:
                    print(f"{bcolors.OKCYAN}Inicio de sesión completado.{bcolors.ENDC}")
                    hilo = Thread(target=NormalUserShell(self.main, nombre_usuario, hassed_pass, token_usuario).cmdloop())
                    hilo.start()
                    hilo.join()
            # Login para administrador
            else:
                token = getpass.getpass("Introduce el token administrativo: ")
                is_admin = self.authenticator.isAdmin(token)
                if (is_admin):
                    print(f"{bcolors.OKCYAN}Inicio de sesión para administrador completado \n{bcolors.ENDC}")
                    hilo = Thread(target=AdminShell(self.main, token,self.broker).cmdloop())
                    hilo.start()
                    hilo.join()
                
        def do_busquedaPorNombre(self,arg):
            """Opción para realizar una búsqueda por el catálogo introduciendo un nombre a buscar"""
            if self.conexion is False:
                print(f"{bcolors.FAIL}No se ha podido conectar con los servicios.Saliendo de IceFlix...{bcolors.ENDC}")
                self.broker.shutdown()
                return 1
            else:
                busqueda_por_nombres("",self.catalog)
            
        def do_salir(self,arg):
            """Opción para salir de la aplicación del cliente."""
            self.broker.shutdown()
            print(f"{bcolors.FAIL}Saliendo de IceFlix...{bcolors.ENDC}")
            return 1
        
        def __init__(self, main,broker):
            super(ClientShell, self).__init__()
            self.broker = broker
            try:
                self.main = main
                self.authenticator = main.getAuthenticator()
                self.catalog = main.getCatalog()
                self.file_service = main.getFileService()
                self.conexion = True
            except:
                self.conexion = False
                
class AdminShell(cmd.Cmd):
    """Clase que implementa el menú del administrador"""
    intro = 'Menu de administrador. Escribe "help" ó "?" para listar las opciones.\nEscribe help <opcion> para obtener un resumen.'
    prompt: str = '(Admin on-line)'
    
    # ----- Opciones del menú del administrador ----- #
    def do_agregarUsuario(self,arg):
        """Añadir un usuario a la base de datos del programa."""
        if self.conexion is True:
            nombre_usuario = input("Introduce el nombre del usuario a añadir: ")
            password = getpass.getpass("Contraseña:")
            hassed_pass = hashlib.sha256(password.encode()).hexdigest()
            try:
                self.authenticator.addUser(nombre_usuario, hassed_pass, self.admin_token)
                print(f"{bcolors.OKCYAN}Se ha creado al usuario", nombre_usuario, f"{bcolors.ENDC}")
            except IceFlix.Unauthorized:
                print(f"{bcolors.FAIL}No se le ha permitido realizar esta acción.{bcolors.ENDC}")
            except IceFlix.TemporaryUnavailable:
                print(f"{bcolors.FAIL}No se ha podido realizar esta acción.{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}No se puede añadir ningún usuario ya que no está el servicio authenticator.{bcolors.ENDC}")
        
    def do_borrarUsuario(self,arg):
        """Eliminar un usuario de la base de datos del programa."""
        if self.conexion is True:
            nombre_usuario = input("Introduce el nombre del usuario a eliminar:")
            try:
                self.authenticator.removeUser(nombre_usuario,self.admin_token)
            except IceFlix.Unauthorized:
                print(f"{bcolors.FAIL}No se le ha permitido realizar esta acción.")
            except IceFlix.TemporaryUnavailable:
                print(f"{bcolors.FAIL}No se ha podido realizar esta acción.")
        else:
            print(f"{bcolors.FAIL}No se puede eliminar ningún usuario ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
            
    def do_renombrarArchivo(self,arg):
        """Renombrar un fichero del catálogo."""
        if self.conexion is True:
            nombre = input("Introduce el nombre del archivo a editar: ")
            lista = self.catalog.getTilesByName(nombre,True)
            if(len(lista) == 0):
                print(f"{bcolors.WARNING}No se ha encontrado ningún archivo con este nombre.{bcolors.ENDC}")
            else:
                nombre_nuevo = input("Introduce el nuevo nombre del archivo:")
                try:
                    self.catalog.renameTile(lista[0],nombre_nuevo,self.admin_token)
                    print(f"{bcolors.OKCYAN}Se ha actualizado el nombre en el catálogo.{bcolors.ENDC}")
                except:
                    print(f"{bcolors.FAIL}Error con el catalog.{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}No se puede renombrar ningún archivo ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
            
    def do_eliminarArchivo(self,arg):
        """Eliminar un fichero del catálogo."""
        if self.conexion is True:
            nombre = input("Introduce el nombre exacto del fichero a eliminar:")
            lista = self.catalog.getTilesByName(nombre,True)
            if(len(lista) == 0):
                print("No existe ningún archivo con el nombre indicado.")
            else:
                # self.catalog.removeMedia(lista[0],self.file_service)
                self.file_service.removeFile(lista[0],self.admin_token)
        else:
            print(f"{bcolors.FAIL}No se puede eliminar ningún archivo ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
    
    def do_subirArchivo(self,arg):
        """Subir un archivo al catálogo."""
        if self.conexion is True:
            try:
                servant = Uploader(self.main)
            except:
                print("No se ha podido crear el uploader.")
            else:
                adapter = self.broker.createObjectAdapterWithEndpoints("FileUploaderAdapter","default")
                base_prx = adapter.addWithUUID(servant)
                proxy = IceFlix.FileUploaderPrx.checkedCast(base_prx)
                id = self.file_service.uploadFile(proxy,self.admin_token)
                sys.stdout.flush()        
                adapter.activate()
        else:
            print(f"{bcolors.FAIL}No se puede subir ningún archivo ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
            
    def do_cerrarSesion(self,arg):
        """Cerrar sesión como administrador."""
        print("Cerrando sesión del administrador...")
        return 1
        
    def __init__(self, main, admin_token,broker):
        super(AdminShell, self).__init__()
        self.broker = broker
        self.main = main
        try:
            self.authenticator = main.getAuthenticator()
            self.catalog = main.getCatalog()
            self.file_service = main.getFileService()
            self.conexion = True
        except:
            self.conexion = False
        self.admin_token = admin_token

class NormalUserShell(cmd.Cmd):
    """Clase que implementa el menú de un usuario que ha iniciado sesión"""
    intro = '\nEscribe "help" ó "?" para listar las opciones.\nEscribe help <opcion> para obtener un resumen.'
    prompt: str = '(on-line)'
    
    def do_realizarBusqueda(self,arg):
        """Realizar una búsqueda de títulos por nombre o por tags."""
        if self.conexion is False:
            print(f"{bcolors.FAIL}No se puede realizar la búsqueda ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
            return 0
        print("Elije una opción (introduce un número 1 o 2).\n1. Búsqueda por nombre\n2. Búsqueda por tags")
        opcion = get_opcion([1,2])
        # Búsqueda por nombre
        if(opcion==1):
            self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
            lista = busqueda_por_nombres(self.token_usuario,self.catalog)
        # Búsqueda por tag
        else:
            lista = busqueda_por_tags(self.nombre_usuario, self.hassed_pass,self.token_usuario,self.authenticator,self.catalog) 
        if(len(lista) == 0):
               return 0
        # Obtener título de la lista obtenida
        self.titulo = obtener_seleccion_usuario(lista,self.token_usuario,self.catalog)
        media_id = self.catalog.getTilesByName(self.titulo,True)
        self.id_titulo = media_id[0]
        self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
        tags = get_tags(media_id[0],self.token_usuario,self.catalog)
        print("El título seleccionado ha sido",f"{bcolors.BOLD}",self.titulo, f"{bcolors.ENDC}con los tags -->", tags,"\n")
        print("¿Deseas añadir o eliminar tags? Introduce 1 ó 2:\n1. Añadir tags\n2. Eliminar tags. \n3 No quiero editar los tags.")
        opcion = get_opcion([1,2,3])
        # Añadir tags
        if(opcion == 1):
           añadir_tags(self.titulo, self.token_usuario,self.nombre_usuario,self.hassed_pass,self.authenticator,self.catalog)
        # Eliminar tags
        elif (opcion == 2):
            if(len(tags) == 0):
                print("No se pueden eliminar tags de su selección ya que no tiene ningún tag.\nVolviendo al menú...\n")
                return 0
            existen = False
            while existen is False:
                print("Escribe los tags que quieres eliminar a ", self.titulo, " separados por comas:",end=" ")
                tags = input()
                tags_list = (tags.replace(" ","")).split(',')
                self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
                existen = tags_existen(tags_list,media_id[0],self.token_usuario,self.catalog)
                if tags == "":
                    print("\nNo se ha añadido ningún tag.")
                    break
                elif existen is True:
                    self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
                    self.catalog.removeTags(media_id[0],tags_list, self.token_usuario)
                    print(f"{bcolors.OKCYAN}Se han eliminado los tags.\n{bcolors.ENDC}")
        else:
            print(f"{bcolors.OKCYAN}No se ha editado ningún tag.\n{bcolors.ENDC}")
        return 0
       
    def do_realizarDescarga(self,arg):
        """Descargar un archivo una vez seleccionado un título anteriormente."""
        if self.conexion is True:
            if(self.titulo == ""):
                print(f"{bcolors.FAIL}No tienes ningún título seleccionado. /Debes realizar una búsqueda y seleccionar un título.\n{bcolors.ENDC}")
            else:
                self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
                file_handler = self.file_service.openFile(self.id_titulo,self.token_usuario)
                with open("archivo", "wb") as file_descriptor:
                    while True:
                        try:
                            recibido = file_handler.receive(4096)
                            if len(recibido) == 0:
                                break
                        except IceFlix.Unauthorized:
                            self.token_usuario = comprobar_token(self.nombre_usuario,self.hassed_pass,self.token_usuario,self.authenticator)
                        file_descriptor.write(recibido)
                file_handler.close()
        else:
            print(f"{bcolors.FAIL}No se puede subir descargar ningún archivo ya que no se ha podido conectar con los servicios.{bcolors.ENDC}")
            
    def do_cerrarSesion(self,arg):
        """Cerrar sesión en el usuario"""
        print("Cerrando sesión de", self.nombre_usuario,"\n")
        return 1
    
    def __init__(self, main, nombre_usuario, hassed_pass, token_usuario):
        super(NormalUserShell, self).__init__()
        self.main = main
        try:
            self.authenticator = main.getAuthenticator()
            self.catalog = main.getCatalog()
            self.file_service = main.getFileService()
            self.conexion = True
        except:
            self.conexion = False
        self.nombre_usuario = nombre_usuario
        self.hassed_pass = hassed_pass
        self.token_usuario = token_usuario
        self.titulo = ""
        self.id_titulo = ""

class AnnouncementI(IceFlix.Announcement):
    def __init__(self):
        self.main = None
        self.all_mains = {}
        self.event = threading.Event()
        
    def announce(self,service, srvId):
        if service.ice_isA("::IceFlix::Main"):
            self.allmains[srvId] = IceFlix.MainPrx.uncheckedCast(service)
            self.main = IceFlix.MainPrx.uncheckedCast(service)
            print("Servidor principal conectado")
            self.event.set()
        
class Client(Ice.Application):
    """Clase en la que se intenta conectar con el proxy del main pasado por parámetros"""
    # ----- Clase Cliente ----- #
    def run(self, args):
        # if(len(sys.argv) != 2):
        #     print("Tienes que insertar el proxy del main. \nSaliendo del programa...")
        #     return -1
        # contador = 0
        # comprobacion = False
        # while contador != 3:
        #     contador +=1
        #     try:
        #         proxy = self.communicator().stringToProxy(args[1])
        #         main = IceFlix.MainPrx.checkedCast(proxy)
        #         comprobacion = True
        #     except:
        #         print(f"{bcolors.WARNING}Intento número",contador,f"de conexión fallido por el proxy.{bcolors.ENDC}")
        #         time.sleep(5)
        #     else:
        #         break
        # if comprobacion is True:
        broker = self.communicator()
            
        proxy = broker.stringToProxy("IceStorm/TopicManager:tcp -p 10000")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(proxy)
            
        announcement_topic = topic_manager.retrieve("Announcements")
        announ_ser = AnnouncementI()
            
        adapter = broker.createObjectAdapter("ClientAdapter")
        announcement_proxy = adapter.addWithUUID(announ_ser)
            
        announcement_topic.subscribeAndGetPublisher({},announcement_proxy)
            
        if not announ_ser.event.wait(timeout=60):
            raise RuntimeError(f'{bcolors.FAIL}No se ha encontrado ningún main en 60 segundos{bcolors.ENDC}')
        else:
            hilo = Thread(target=ClientShell(announ_ser.main,broker).cmdloop(), daemon=True)
            hilo.start()
            sys.stdout.flush()
            self.shutdownOnInterrupt()
            broker.waitForShutdown() 
        # else:
        #     raise RuntimeError(f'{bcolors.FAIL}Se han realizado todos los intentos de conexión. Error con el proxy{bcolors.ENDC}')
              
        return 1

sys.exit(Client().main(sys.argv))
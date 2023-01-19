#! /usr/bin/env python
# -- coding: utf-8 --

import cmd
import hashlib
import sys
import getpass
import threading
from threading import Thread
import time
import tkinter.filedialog
import Ice # pylint: disable=import-error
import IceFlix # pylint: disable=import-error
import IceStorm # pylint: disable=import-error


class Colors:
    """Clase para hacer prints de forma más vistosa"""
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    PURPLE = '\033[35m'
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


ERROR_NUMBER_INPUT = "Introduce un número."
ERROR_OPTION_INPUT = "Introduce un número del 1 al {}."
ERROR_CATALOG = f"{Colors.FAIL}Error con el catalog.{Colors.ENDC}"


def get_option(options):
    """Método para obtener la opción que introduzca el usuario"""
    while True:
        try:
            opcion = int(input("Eleccion:"))
            if opcion in options:
                break
            else:
                print(ERROR_OPTION_INPUT.format(options[-1]))
        except ValueError:
            print(ERROR_NUMBER_INPUT)
    return opcion


def show_search(results, user_token, catalog):
    """Método para obtener los tags de los identificadores que devuelve una búsqueda """
    pos = 0
    print("Hay {} resultados:".format(len(results)))
    while pos < len(results):
        try:
            media = catalog.getTile(results[pos], user_token)
        except:
            print(f"{Colors.FAIL}Error con el catalog.{Colors.ENDC}")
        else:

            print(f"{Colors.OKBLUE}", pos+1, "->", media.info.name, ".Tags:",
                  media.info.tags, ".Id:", results[pos], f"{Colors.ENDC}")
            pos += 1


def show_anonymous_search(results_list):
    """Método para recorrer una lista de un usuario no logeado"""
    pos = 0
    print("Hay", len(results_list), "resultados:")
    while pos < len(results_list):
        print(f"{Colors.OKBLUE}", str(pos+1), "-",
              results_list[pos], f"{Colors.ENDC}")
        pos += 1


def title_exists(title, results_list, catalog, user_token):
    """Método para saber si un título de un archivo está en una lista o no"""
    try:
        exists = any(catalog.getTile(media_id, user_token).info.name ==
                     title for media_id in results_list)
    except:
        print(ERROR_CATALOG)
        return False
    return exists


def tags_exist(tags_list, media_id, user_token, catalog):
    """Método para saber si una serie de tags existen en los tags de un archivo"""
    try:
        media = catalog.getTile(media_id, user_token)
    except:
        print(ERROR_CATALOG)
        return False
    return all(tag in media.info.tags for tag in tags_list)


def get_tags(media_id, user_token, catalog):
    """Método para obtener los tags de un archivo"""
    try:
        media = catalog.getTile(media_id, user_token)
    except:
        print(ERROR_CATALOG)
        tags = ""
    else:
        tags = media.info.tags
    return tags


def name_search(user_token, catalog):
    """Método para realizar una búsqueda en el catálogo por nombre"""
    option = input(
        "¿Desea realizar una búsqueda exacta del nombre? Introduzca SI/NO ó si/no: ").lower()
    while option not in ('si', 'no'):
        option = input(
            "Opción no válida. ¿Desea realizar una búsqueda exacta del nombre? "
            "Introduzca SI/NO ó si/no: ").lower()
    name = input("Introduce la palabra a buscar: ")
    results_list = catalog.getTilesByName(name, option == "si")
    if len(results_list) == 0:
        print("No se han encontrado resultados en la búsqueda.")
    elif user_token == "":
        show_anonymous_search(results_list)
    else:
        show_search(results_list, user_token, catalog)
    return results_list


def search_by_tags(username, hashed_password, user_token, authenticator, catalog):
    """Método para realizar una búsqueda por tags"""
    prompt = "¿Desea realizar una búsqueda exacta de los tags? Introduzca SI/NO ó si/no: "
    option = input(prompt).lower()
    while option not in ('si', 'no'):
        option = input("Opción no válida. " + prompt).lower()
    tag_list = input("Introduce los tags separados por comas: ")
    tag_list = (tag_list.replace(" ", "")).split(",")
    user_token = validate_token(
        username, hashed_password, user_token, authenticator)
    result_list = catalog.getTilesByTags(tag_list, option == "si", user_token)
    if not result_list:
        print("No se han encontrado resultados para la búsqueda.")
    else:
        show_search(result_list, user_token, catalog)
    return result_list


def add_tags(title, user_token, username, hashed_password, authenticator, catalog):
    """Método para añadir tags a un archivo seleccionado"""
    print("Escribe los tags que quieres añadir a",
          title, "separados por comas:", end=" ")
    tags = input()
    tag_list = (tags.replace(" ", "")).split(",")
    user_token = validate_token(
        username, hashed_password, user_token, authenticator)
    media_id = catalog.getTilesByName(title, user_token)
    user_token = validate_token(
        username, hashed_password, user_token, authenticator)
    catalog.addTags(media_id[0], tag_list, user_token)
    print(f"{Colors.OKCYAN}Se han añadido los tags indicados.\n{Colors.ENDC}")


def validate_token(nombre_usuario, hashed_pass, token_usuario, authenticator):
    """Método para actualizar el token de los usuarios cuando sea necesario"""
    if not authenticator.isAuthorized(token_usuario):
        return authenticator.refreshAuthorization(nombre_usuario, hashed_pass)
    return token_usuario


def get_user_selection(title_list, user_token, catalog):
    """Método para obtener el título que selecciona un usuario"""
    if not title_list:
        return ""
    selected_title = ""
    while not title_exists(selected_title, title_list, catalog, user_token):
        selected_title = input("Enter the title you want to select: ")
    return selected_title


class Uploader(IceFlix.FileUploader):
    """Clase para realizar la subida de archivos por el administrador"""

    def __init__(self, main):
        """Método constructor de la clase Uploader"""
        self.authenticator = main.get_authenticator()
        self.filename = tkinter.filedialog.askopenfilename()
        self.f_open = open(self.filename)

    def receive(self, size):
        """Método para recibir los bytes del fichero a descargar"""
        return self.f_open.read(size)

    def close(self, user_token):
        """Método para terminar la transferencia"""
        if self.authenticator.is_admin(user_token):
            self.f_open.close()

class AnnouncementI(IceFlix.Announcement):
    """Clase que implementa la interfaz Announcement para el topic Announcements"""

    def __init__(self, boolean):
        self.search_main = boolean
        self.ids = []
        self.services = []
        self.main = None
        self.event = threading.Event()

    def announce(self, service, srv_id, current=None): # pylint: disable=unused-argument
        """Método para obtener el main u obtener anunciamientos"""
        if self.search_main is True:
            if service.ice_isA('::IceFlix::Main'):
                self.main = IceFlix.MainPrx.uncheckedCast(service)
                print("Servidor principal conectado")
                self.event.set()
        elif not srv_id in self.ids and not service in self.services:
            self.ids.append(srv_id)
            self.services.append(service)
            if service.ice_isA('::IceFlix::Main'):
                print(f"{Colors.OKCYAN}\nNuevo Main anunciado:",
                      service, ", id:", srv_id, f"{Colors.ENDC}")
            elif service.ice_isA('::IceFlix::MediaCatalog'):
                print(f"{Colors.OKCYAN}\nNuevo MediaCatalog anunciado:",
                      service, ", id:", srv_id, f"{Colors.ENDC}")
            elif service.ice_isA('::IceFlix::Authenticator'):
                print(f"{Colors.OKCYAN}\nNuevo Authenticator anunciado:",
                      service, ", id:", srv_id, f"{Colors.ENDC}")
            elif service.ice_isA('::IceFlix::FileService'):
                print(f"{Colors.OKCYAN}\nNuevo FileService anunciado:",
                      service, ", id:", srv_id, f"{Colors.ENDC}")


class UserUpdateI(IceFlix.UserUpdate):
    """Clase que implementa la interfaz UserUpdate"""

    def newToken(self, user, token, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que se ha creado un nuevo token para un usuario"""
        print(f"{Colors.PURPLE}\nSe ha creado un nuevo token", token,
              "para el usuario", user, "por el Authenticator", service_id, f"{Colors.ENDC}")

    def revokeToken(self, token, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que se ha anulado un token"""
        print(f"{Colors.PURPLE}\nSe ha anulado el token", token,
              "por el Authenticator", service_id, f"{Colors.ENDC}")

    def newUser(self, user, password_hash, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que se ha añadido un usuario"""
        print(f"{Colors.PURPLE}\nEl usuario", user, "con su contraseña en hass", password_hash,
              "ha sido creado por el Authenticator", service_id, f"{Colors.ENDC}")

    def removeUser(self, user, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que un usuario ha sido eliminado"""
        print(f"{Colors.PURPLE}\nEl usuario", user,
              "ha sido eliminado por el Authenticator", service_id, f"{Colors.ENDC}")


class CatalogUpdateI(IceFlix.CatalogUpdate):
    """Clase que implementa la interfaz CatalogUpdate para el topic CatalogUpdates"""

    def renameTile(self, media_id, newName, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia el cambio de nombre de un fichero"""
        print(f"{Colors.GREEN}\nEl fichero con id", media_id, "ha sido renombrado a ",
              newName, "por el Catalog", service_id, f"{Colors.ENDC}")

    def addTags(self, media_id, user, tags, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que se han añadido unos tags a un fichero"""
        print(f"{Colors.GREEN}\nEl usuario", user, "ha añadido los tags", tags,
              "al fichero con id ", media_id, "con el Catalog", service_id, f"{Colors.ENDC}")

    def removeTags(self, media_id, user, tags, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método en el que se anuncia que se han eliminado unos tags a un fichero"""
        print(f"{Colors.GREEN}\nEl usuario", user, "ha eliminado los tags", tags,
              "del fichero con id ", media_id, "con el Catalog", service_id, f"{Colors.ENDC}")


class FileAvailabilityAnnounceI(IceFlix.FileAvailabilityAnnounce):
    """Clase que implementa la interfaz FileAvailabilityAnnounce"""

    def announceFiles(self, media_ids, service_id, current=None): # pylint: disable=invalid-name,unused-argument
        """Método para anunciar los identificadores de un FileService"""
        print(f"{Colors.WHITE}\nLa lista de identificadores de los archivos del FileService",
              service_id, "es:", media_ids, f"{Colors.ENDC}")


class ClientShell(cmd.Cmd):
    """Clase que implementa el menú de un usuario no logeado"""
    intro = """Bienvenido al IceFlix menu. Escribe "help" ó "?" para listar las opciones.
Escribe help <opcion> para obtener un resumen."""
    prompt: str = '(Off-line)'

    # ----- Opciones del menú del cliente ----- #
    def do_login(self, arg):
        """Iniciar sesión como usuario o administrador"""
        if self.conexion is False:
            print(
                f"{Colors.FAIL}No se ha podido conectar con los servicios."
                f"Saliendo de IceFlix{Colors.ENDC}")
            self.broker.shutdown()
            return 1

        print("¿Quieres iniciar sesión como usuario o administrador? Introduce 1 ó 2")
        print("1. Usuario\n2. Administrador")
        opcion = get_option([1, 2])

        # Login para usuario
        if opcion == 1:
            nombre_usuario = input("Introduce tu nombre de usuario:")
            password = getpass.getpass("Contraseña: ")
            hassed_pass = hashlib.sha256(password.encode()).hexdigest()
            try:
                token_usuario = self.authenticator.refreshAuthorization(
                    nombre_usuario, hassed_pass)
            except IceFlix.Unauthorized:
                print(
                    f"{Colors.FAIL}El usuario o contraseña son incorrectos.{Colors.ENDC} \n")
            else:
                print(f"{Colors.OKCYAN}Inicio de sesión completado.{Colors.ENDC}")
                hilo = Thread(target=NormalUserShell(
                    self.main, nombre_usuario, hassed_pass, token_usuario).cmdloop())
                hilo.start()
                hilo.join()
        # Login para administrador
        else:
            token = getpass.getpass("Introduce el token administrativo: ")
            is_admin = self.authenticator.isAdmin(token)
            if is_admin:
                print(
                    f"{Colors.OKCYAN}Inicio de sesión para administrador completado \n{Colors.ENDC}")
                hilo = Thread(target=AdminShell(
                    self.main, token, self.broker).cmdloop())
                hilo.start()
                hilo.join()

    def do_busqueda_por_nombre(self, arg):
        """Opción para realizar una búsqueda por el catálogo introduciendo un nombre a buscar"""
        if self.conexion is False:
            print(
                f"{Colors.FAIL}No se ha podido conectar con los servicios.Saliendo de IceFlix...{Colors.ENDC}")
            self.broker.shutdown()
            return 1
        name_search("", self.catalog)
        return 0

    def do_salir(self, arg):
        """Opción para salir de la aplicación del cliente."""
        self.broker.shutdown()
        print(f"{Colors.FAIL}Saliendo de IceFlix...{Colors.ENDC}")
        return 1

    def __init__(self, main, broker):
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
    intro = """Menu de administrador. Escribe "help" ó "?" para listar las opciones.
Escribe help <opcion> para obtener un resumen."""
    prompt: str = '(Admin on-line)'

    def run(self):
        """Método que se ejecutará al acceder al menú administrador"""
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(self.broker.propertyToProxy("IceStorm.TopicManager"))

        # Topic "Announcements"
        announcement_topic = topic_manager.retrieve("Announcements")
        announcement_servant = AnnouncementI(False)
        self.adapter_announcements = self.broker.createObjectAdapter(
            "AdminAdapter")
        announcement_proxy = self.adapter_announcements.addWithUUID(
            announcement_servant)
        announcement_topic.subscribeAndGetPublisher({}, announcement_proxy)
        # Topic "UserUpdates"
        user_updates_topic = topic_manager.retrieve("UserUpdates")
        user_updates_servant = UserUpdateI()
        user_updates_proxy = self.adapter_announcements.addWithUUID(
            user_updates_servant)
        user_updates_topic.subscribeAndGetPublisher({}, user_updates_proxy)
        # Topic "CatalogUpdates"
        catalog_updates_topic = topic_manager.retrieve("CatalogUpdates")
        catalog_updates_servant = CatalogUpdateI()
        catalog_updates_proxy = self.adapter_announcements.addWithUUID(
            catalog_updates_servant)
        catalog_updates_topic.subscribeAndGetPublisher(
            {}, catalog_updates_proxy)
        # Topic "FileAvailabilityAnnounces"
        file_availability_topic = topic_manager.retrieve(
            "FileAvailabilityAnnounces")
        file_availability_servant = FileAvailabilityAnnounceI()
        file_availability_proxy = self.adapter_announcements.addWithUUID(
            file_availability_servant)
        file_availability_topic.subscribeAndGetPublisher(
            {}, file_availability_proxy)

        self.adapter_announcements.activate()

    # ----- Opciones del menú del administrador ----- #
    def do_agregar_usuario(self, arg):
        """Añadir un usuario a la base de datos del programa."""
        if self.conexion is True:
            nombre_usuario = input(
                "Introduce el nombre del usuario a añadir: ")
            password = getpass.getpass("Contraseña:")
            hassed_pass = hashlib.sha256(password.encode()).hexdigest()
            try:
                self.authenticator.addUser(
                    nombre_usuario, hassed_pass, self.admin_token)
                print(f"{Colors.OKCYAN}Se ha creado al usuario",
                      nombre_usuario, f"{Colors.ENDC}")
            except IceFlix.Unauthorized:
                print(
                    f"{Colors.FAIL}No se le ha permitido realizar esta acción.{Colors.ENDC}")
            except IceFlix.TemporaryUnavailable:
                print(
                    f"{Colors.FAIL}No se ha podido realizar esta acción.{Colors.ENDC}")
        else:
            print(
                f"{Colors.FAIL}No se puede añadir ningún usuario ya que no está el servicio authenticator.{Colors.ENDC}")

    def do_borrar_usuario(self, arg):
        """Eliminar un usuario de la base de datos del programa."""
        if self.conexion is True:
            nombre_usuario = input(
                "Introduce el nombre del usuario a eliminar:")
            try:
                self.authenticator.removeUser(nombre_usuario, self.admin_token)
            except IceFlix.Unauthorized:
                print(f"{Colors.FAIL}No se le ha permitido realizar esta acción.")
            except IceFlix.TemporaryUnavailable:
                print(f"{Colors.FAIL}No se ha podido realizar esta acción.")
        else:
            print(f"{Colors.FAIL}No se puede eliminar ningún usuario ya que "
            f"no se ha podido conectar con los servicios.{Colors.ENDC}")

    def do_renombrar_archivo(self, arg):
        """Renombrar un fichero del catálogo."""
        if self.conexion is True:
            nombre = input("Introduce el nombre del archivo a editar: ")
            lista = self.catalog.getTilesByName(nombre, True)
            if len(lista) == 0:
                print(
                    f"{Colors.WARNING}No se ha encontrado ningún archivo con este nombre.{Colors.ENDC}")
            else:
                nombre_nuevo = input("Introduce el nuevo nombre del archivo:")
                try:
                    self.catalog.renameTile(
                        lista[0], nombre_nuevo, self.admin_token)
                    print(
                        f"{Colors.OKCYAN}Se ha actualizado el nombre en el catálogo.{Colors.ENDC}")
                except:
                    print(f"{Colors.FAIL}Error con el catalog.{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}No se puede renombrar ningún archivo ya que "
            f"no se ha podido conectar con los servicios.{Colors.ENDC}")

    def do_eliminar_archivo(self, arg):
        """Eliminar un fichero del catálogo."""
        if self.conexion is True:
            nombre = input(
                "Introduce el nombre exacto del fichero a eliminar:")
            lista = self.catalog.getTilesByName(nombre, True)
            if len(lista) == 0:
                print("No existe ningún archivo con el nombre indicado.")
            else:
                # self.catalog.removeMedia(lista[0],self.file_service)
                self.file_service.removeFile(lista[0], self.admin_token)
        else:
            print(f"{Colors.FAIL}No se puede eliminar ningún archivo ya que "
            f"no se ha podido conectar con los servicios.{Colors.ENDC}")

    def do_subir_archivo(self, arg):
        """Subir un archivo al catálogo."""
        if self.conexion is True:
            try:
                servant = Uploader(self.main)
            except:
                print("No se ha podido crear el uploader.")
            else:
                adapter = self.broker.createObjectAdapterWithEndpoints(
                    "FileUploaderAdapter", "default")
                base_prx = adapter.addWithUUID(servant)
                proxy = IceFlix.FileUploaderPrx.checkedCast(base_prx)
                self.file_service.uploadFile(proxy, self.admin_token)
                sys.stdout.flush()
                adapter.activate()
        else:
            print(f"{Colors.FAIL}No se puede subir ningún archivo ya que "
            f"no se ha podido conectar con los servicios.{Colors.ENDC}")

    def do_cerrar_sesion(self, arg):
        """Cerrar sesión como administrador."""
        print("Cerrando sesión del administrador...")
        self.adapter_announcements.destroy()
        return 1

    def __init__(self, main, admin_token, broker):
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
        self.adapter_announcements = None
        self.run()


class NormalUserShell(cmd.Cmd):
    """Clase que implementa el menú de un usuario que ha iniciado sesión"""
    intro = '\nEscribe "help" ó "?" para listar las opciones.\nEscribe help <opcion> para obtener un resumen.'
    prompt: str = '(on-line)'

    def do_realizar_busqueda(self, arg):
        """Realizar una búsqueda de títulos por nombre o por tags."""
        if self.conexion is False:
            print(f"{Colors.FAIL}No se puede realizar la búsqueda ya "
            f"que no se ha podido conectar con los servicios.{Colors.ENDC}")
            return 0
        print("Elije una opción (introduce un número 1 o 2).\n1. Búsqueda por nombre\n2. Búsqueda por tags")
        opcion = get_option([1, 2])
        # Búsqueda por nombre
        if opcion == 1:
            self.token_usuario = validate_token(
                self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
            lista = name_search(self.token_usuario, self.catalog)
        # Búsqueda por tag
        else:
            lista = search_by_tags(self.nombre_usuario, self.hassed_pass,
                                   self.token_usuario, self.authenticator, self.catalog)
        if len(lista) == 0:
            return 0
        # Obtener título de la lista obtenida
        self.titulo = get_user_selection(
            lista, self.token_usuario, self.catalog)
        media_id = self.catalog.getTilesByName(self.titulo, True)
        self.id_titulo = media_id[0]
        self.token_usuario = validate_token(
            self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
        tags = get_tags(media_id[0], self.token_usuario, self.catalog)
        print("El título seleccionado ha sido",
              f"{Colors.BOLD}", self.titulo, f"{Colors.ENDC}con los tags -->", tags, "\n")
        print("¿Deseas añadir o eliminar tags? Introduce 1 ó 2:\n"
            "1. Añadir tags\n2. Eliminar tags. \n3 No quiero editar los tags.")
        opcion = get_option([1, 2, 3])
        # Añadir tags
        if opcion == 1:
            add_tags(self.titulo, self.token_usuario, self.nombre_usuario,
                     self.hassed_pass, self.authenticator, self.catalog)
        # Eliminar tags
        elif opcion == 2:
            if len(tags) == 0:
                print(
                    "No se pueden eliminar tags de su selección ya que no tiene ningún tag.\nVolviendo al menú...\n")
                return 0
            existen = False
            while existen is False:
                print("Escribe los tags que quieres eliminar a ",
                      self.titulo, " separados por comas:", end=" ")
                tags = input()
                tags_list = (tags.replace(" ", "")).split(',')
                self.token_usuario = validate_token(
                    self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
                existen = tags_exist(
                    tags_list, media_id[0], self.token_usuario, self.catalog)
                if tags == "":
                    print("\nNo se ha añadido ningún tag.")
                    break
                elif existen is True:
                    self.token_usuario = validate_token(
                        self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
                    self.catalog.removeTags(
                        media_id[0], tags_list, self.token_usuario)
                    print(
                        f"{Colors.OKCYAN}Se han eliminado los tags.\n{Colors.ENDC}")
        else:
            print(f"{Colors.OKCYAN}No se ha editado ningún tag.\n{Colors.ENDC}")
        return 0

    def do_realizar_descarga(self, arg):
        """Descargar un archivo una vez seleccionado un título anteriormente."""
        if self.conexion is True:
            if self.titulo == "":
                print(
                    f"{Colors.FAIL}No tienes ningún título seleccionado. "
                    f"Debes realizar una búsqueda y seleccionar un título.\n{Colors.ENDC}")
            else:
                self.token_usuario = validate_token(
                    self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
                file_handler = self.file_service.openFile(
                    self.id_titulo, self.token_usuario)
                with open("archivo", "wb") as file_descriptor:
                    while True:
                        try:
                            recibido = file_handler.receive(4096)
                            if len(recibido) == 0:
                                break
                        except IceFlix.Unauthorized:
                            self.token_usuario = validate_token(
                                self.nombre_usuario, self.hassed_pass, self.token_usuario, self.authenticator)
                        file_descriptor.write(recibido)
                file_handler.close()
        else:
            print(f"{Colors.FAIL}No se puede subir descargar ningún archivo ya "
            f"que no se ha podido conectar con los servicios.{Colors.ENDC}")

    def do_cerrar_sesion(self, arg):
        """Cerrar sesión en el usuario"""
        print("Cerrando sesión de", self.nombre_usuario, "\n")
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


class Client(Ice.Application):
    """Clase en la que se intenta conectar con el proxy del main pasado por parámetros"""
    # ----- Clase Cliente ----- #

    def run(self, args):
        """Método que se ejecutará cuando se llame a esta clase para conectar al main"""
        attempts  = 5
        tries = 0
        broker = self.communicator()
        while tries < attempts:
            try:
                topic_manager = IceStorm.TopicManagerPrx.checkedCast(
                    self.communicator().propertyToProxy("IceStorm.TopicManager")
                )
                break
            except Ice.ConnectionRefusedException:
                print(f"{Colors.FAIL}Error de conexión al Topic Manager,"
                f"intentando de nuevo en 5 segundos...{Colors.ENDC}")
                time.sleep(5)
                tries += 1
        else:
            raise RuntimeError(f"{Colors.FAIL}No se ha contectado al Topic Manager en {attempts}"
            f"intentos{Colors.ENDC}")

        announcement_topic = topic_manager.retrieve("Announcements")
        announcement_servant = AnnouncementI(True)

        adapter = broker.createObjectAdapter("ClientAdapter")
        adapter.activate()
        announcement_proxy = adapter.addWithUUID(announcement_servant)

        announcement_topic.subscribeAndGetPublisher({}, announcement_proxy)
        print("Esperando a recibir mains del topic Announcements")
        if not announcement_servant.event.wait(timeout=60):
            raise RuntimeError(
                f'{Colors.FAIL}No se ha encontrado ningún main en 60 segundos{Colors.ENDC}')
        
        announcement_topic.unsubscribe(announcement_proxy)
        hilo = Thread(target=ClientShell(
            announcement_servant.main, broker).cmdloop(), daemon=True)
        hilo.start()
        sys.stdout.flush()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 1

sys.exit(Client().main(sys.argv))

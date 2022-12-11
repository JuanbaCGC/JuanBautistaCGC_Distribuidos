# Manual del Cliente de IceFlix

Para ejecutar el cliente, hay que hacer la siguiente instalación.

## Instalación

Una vez que se tenga el repositorio clonado, hay que crear un entorno virtual:
```bash
source ~/.venv/bin/activate
```
Una vez creado este entorno, estando en la carpeta raíz del directorio, ejecutamos en el terminal:

```bash
pip install -e .
```
Y acto seguido se instalarán las dependencias necesarias.

## Ejecución
Para la ejecución del cliente, una vez que tengamos el proxy del main, hay que realizar (con el proxy del main entre comillas):
```bash
iceflix <proxy del main>
```
Y se lanzará el cliente.
## Uso
Una vez ejecutado el cliente y se haya conectado con el main, veremos el menú principal. Para listar las opciones del menú, basta con introducir "?". Estas opciones son:

* ***Login:***
opción para iniciar sesión, ya sea como usuario o como administrador. 
* ***Búsqueda por nombre:*** realizar una búsqueda en el catálogo insertando un nombre.
* ***Salir:*** al ejecutar esta opción, se acabará la ejecución del cliente.

Dependiendo de qué forma se inicia sesión, el siguiente menú será de una forma u otra.
* ***Menú usuario:*** en este menú, el usuario podrá:
    * *realizarBúsqueda:* el usuario podrá buscar títulos por su nombre o por sus tags
    * *realizarDescarga:* una vez el usuario haya seleccionado anteriormente un título, se podrá descargar.
    * *cerrarSesión:* el usuario podrá cerrar su sesión para volver al menú principal.
* ***Menú administrador:*** en este menú, el usuario administrador podrá:
    * *agregarUsuario:* opción con la que el administrador puede añadir un usuario introduciendo su nombre y contraseña.
    * *borrarUsuario:* el administrador introducirá el nombre del usuario que quiera borrar.
    * *renombrarArchivo:* opción para cambiarle el nombre a un archivo existente en el catálogo.
    * *eliminarArchivo:* opción para eliminar un archivo existente del catálogo.
    * *subirArchivo:* opción para subir un archivo al catálogo de IceFlix.
    * *cerrarSesión:* el administrador podrá cerrar su sesión para volver al menú principal.

#### Nota
En los diferentes menús, se puede hacer uso del tabulador para completar la opción a introducir. Es decir, si estando en el menú principal se introduce:
```bash
realiz
```
Y se pulsa la tecla ``⇥ Tab``, la opción a introducir del menú será:
```bash
realizarBusqueda
```

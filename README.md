# Manual del Cliente de IceFlix

Para ejecutar el cliente, hay que hacer las siguientes operaciones.

## Instalación

Una vez que se tenga el repositorio clonado, hay que crear un entorno virtual:
```bash
source ~/.venv/bin/activate
```
Una vez realizado este paso, estando en la carpeta raíz del directorio, tenemos a nuestra disposición un Makefile que se ha creado con la finalidad de hacer más facil el lanzamiento de la práctica. El Makefile tiene las siguientes opciones:
* ***install:*** se instalan las dependencias necesarias para la correcta ejecución de la práctica.
* ***icestorm:*** esta regla debe de ser ejecutada antes que la regla "client", ya que lanza IceStorm y crea los topics necesarios para la comunicación de los servicios. 
* ***run-test:*** se lanzan los test que se han creado para comprobar que los diferentes eventos de los topics son captados correctamente. Se corre un test.sh en el que se lanzan eventos en los diferentes topics.
* ***client:*** se lanza la ejecución del cliente.
* ***clean:*** al igual que icestorm crea los topics, clean los destruye.
* ***all-client:*** realiza todas las operaciones necesarias para lanzar el cliente en un terminal: se instalan primero las dependencias y finalmente se ejecuta el cliente.

El contenido del Makefile es:
```Makefile
install:
	pip install -e .
	sudo apt install zeroc-ice-utils
	sudo apt-get install libzeroc-icestorm3.7 zeroc-icebox

icestorm:
	./run_icestorm

run-test:
	cd tests && \
	./test.sh && \
	cd ..

client:
	./run_client

clean:
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy Announcements"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy UserUpdates"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy CatalogUpdates"
	icestormadmin --Ice.Config=configs/icestorm.config -e "destroy FileAvailabilityAnnounces"

all-client: install client

```

## Ejecución
Para la ejecución del cliente, como ya he explicado, hay que abrir dos terminales, con un entorno virtual en cada una. En el primer terminal hacer:
```bash
make install
make icestorm
```
En el otro, mientras tanto hacemos: 
```bash
make all-client
```
Para acabar con ejectuar también en el primer terminal:
```bash
make run-test
```

En el terminal que lanzaremos make all-client, se lanzará el cliente que quedará a la espera del anunciamiento de un Main. Si este anunciamiento no llega en 60 segundos, se acabará la ejecución del programa. Por otro lado, en el otro terminal, se lanzarán los tests.

## Uso
Una vez ejecutado el cliente y se haya conectado con el Main, veremos el menú principal. Para listar las opciones del menú, basta con introducir "?". Estas opciones son:

* ***Login:*** opción para iniciar sesión, ya sea como usuario o como administrador. 
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

Destacar que en el menú administrador, cuando llegue cualquier evento a los topics: Announcements, UserUpdates, CatalogUpdates ó FileAvailabilityAnnounces, se verá por pantalla la descripción del evento ocurrido.

### Puntos extra
En cuanto a los puntos extra, a parte de la creación de los test ya mencionados anteriormente,se ha realizado la práctica de manera que obtiene un 9,03 de nota con la herramienta pylint. Para comprobarlo, se tiene que tener instalado Pylint, por lo que se debe de hacer:
```bash
pip3 install pylint
```
Y una vez instalado, ejecutar en el repositorio raíz del proyecto:
```bash
pylint --max-line-length=125 --rcfile=configs/client.config iceflix/client.py
```
Además, como he explicado anteriormente, el proyecto es instalable con pip install.
#### Nota
En los diferentes menús, se puede hacer uso del tabulador para completar la opción a introducir. Es decir, si estando en el menú principal se introduce:
```bash
realiz
```
Y se pulsa la tecla ``⇥ Tab``, la opción a introducir del menú será:
```bash
realizarBusqueda
```

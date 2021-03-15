Cómo utilizar **nesim**
=======================

Por ahora **nesim** solo puede simular la capa física de una red de computadoras (en próximos *releases* se irán agregando las siguientes capas de la red). Se pueden crear *hubs* y *hosts*, conectarlos entre sí y enviar y recibir información entre los *hosts*.

Instrucciones
-------------

Cada acción de la simulación (*crear*, *conectar*, *enviar*, etc) está definda por una instrucción. Todas las instrucciones son de la forma:

.. code-block:: shell
    
    <time> <action> <args1>

donde ``time`` es el milisegundo en el que se ejecutará la instrucción, ``action`` la instrucción en sí y ``args`` los argumentos de la misma.

Acontinuación se muestran las instrucciones válidas que **nesim** puede reconocer.

Crear hub
+++++++++

.. code-block:: shell
    
    <time> create hub <hub_name> <ports_count>

* `hub_name` : Nombre del hub
* `ports_count` : Cantidad de puertos

Ejemplo: ``0 create hub H 4``

Crear host
++++++++++

.. code-block:: shell
    
    <time> create host <host_name>

* `host_name` : Nombre del host

Ejemplo: ``0 create host PC``

Conectar
++++++++

.. code-block:: shell
    
    <time> connect <port1> <port2>

* `port1`, `port2` : Nombres de los puertos a conectar.

Ejemplo: ``0 connect PC_1 H_2``

Enviar
++++++

.. code-block:: shell
    
    <time> send <host_name> <data>

* `host_name` : Nombre del host que enviará la información.
* `data` : Serie de bits a evniar.

Ejemplo: ``0 send PC 10111010``

Desconectar
+++++++++++

.. code-block:: shell
    
    <time> disconnect <port>

* `port` : Puerto a desconectar.

Ejemplo: ``0 disconnect PC_1``

Cargar instrucciones
--------------------

Estas instrucciones pueden ser cargadas desde un archivo de texto como el que se muestra a continuación:

.. code-block:: text

    0 create hub H 4
    0 create host PCA
    0 create host PCB
    0 connect PCA_1 H_1
    0 connect PCB_1 H_2
    0 send PCA 01110101

En este ejemplo se crea un `hub` (``H``) y dos `hosts` (``PCA``, ``PCB``), luego se conecta cada puerto de cada host a diferentes puertos del hub (los puertos ``PCA_1`` y ``PCB_1`` con ``H_1`` y ``H_2`` respectivamente). Finalmente se ordena al host ``PCA`` a enviar los bits ``01110101``.

Para cargar un archivo de instrucciones se utiliza la función :py:func:`~inst_parser.load_instructions`:

.. code-block:: python

    import nesim
    instr = nesim.load_instructions()

Esta función busca por defecto un archivo ``script.txt`` donde mismo se ejectuta el ``.py``. En caso que se quiera cargar otro archivo podemos especificar la ruta del mismo:

.. code-block:: python

    instr = nesim.load_instructions('path/of/instructions/file.txt')

Crear y ejecutar una simulación
-------------------------------

Una vez cargada las instrucciones crear una simulación es tán sencillo como:

.. code-block:: python

    sim = nesim.NetSimulation()

Al crearla también se puede especificar la ruta donde serán guardados los logs (por default en la raíz donde se ejecute el ``.py``):

.. code-block:: python

    sim = nesim.NetSimulation('logs/folder/path')

Para ejecutar esta simulación solo es necesario llamar al método :py:func:`~simulation.NetSimulation.start` dándole las instrucciones a ejecutar:

.. code-block:: python

    sim.start(instr)

Timepo de señal
---------------

El tiempo de señal (``signal_time``) define cuantos milisegundos debe estar en transmisión cada bit que se va a enviar. Por defecto su valor es 10 pero el mismo puede ser configurado como se muestra en la siguente sección.

Archivo de configuración
------------------------

Al comenzar una simulación se carga un archivo llamado ``config.txt`` (En caso de no existir se crea uno por defecto). Este archivo contiene la configuración básica para las simulaciones. Cada línea de este archivo contiene un par (``key`` ``value``) donde cada llave representa el nombre de uno de los parámetros a configurar y a su lado el valor correspondiente. Por ahora el único parámetro a configurar es el ``signal_time`` cuyo valor por defecto es 10.

Logs
----

Al finalizar la ejecución de la simulación queda guardado por cada dispositivo un archivo `.txt` con los logs de cada uno respectivamente.

Por ejemplo, al ejecuar la simulación anterior los logs del host ``PCA`` que se guardan en ``PCA.txt`` son:

.. code-block:: text

    -----------------------------------------------------------------------
    | Time (ms)  |   Port   |   Action   |              Info              |
    -----------------------------------------------------------------------
    |     0      |   PCA    |    Sent    | 0                              |
    |     10     |   PCA    |    Sent    | 1                              |
    |     20     |   PCA    |    Sent    | 1                              |
    |     30     |   PCA    |    Sent    | 1                              |
    |     40     |   PCA    |    Sent    | 0                              |
    |     50     |   PCA    |    Sent    | 1                              |
    |     60     |   PCA    |    Sent    | 0                              |
    |     70     |   PCA    |    Sent    | 1                              |
    |     89     |   PCA    |  Received  | 0                              |
    -----------------------------------------------------------------------
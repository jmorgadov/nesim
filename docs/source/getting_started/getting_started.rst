Cómo funciona **nesim**
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
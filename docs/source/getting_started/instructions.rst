Instrucciones
=============

Cada acción de la simulación (*crear*, *conectar*, *enviar*, etc) está definda por una instrucción. Todas las instrucciones son de la forma:

.. code-block:: shell
    
    <time> <action> <args1>

donde ``time`` es el milisegundo en el que se ejecutará la instrucción, ``action`` la instrucción en sí y ``args`` los argumentos de la misma.

Acontinuación se muestran las instrucciones válidas que **nesim** puede reconocer.

Crear hub
---------

.. code-block:: shell
    
    <time> create hub <hub_name> <ports_count>

* `hub_name` : Nombre del hub
* `ports_count` : Cantidad de puertos

Ejemplo: ``0 create hub H 4``

Crear switch
------------

.. code-block:: shell
    
    <time> create switch <switch_name> <ports_count>

* `switch_name` : Nombre del switch
* `ports_count` : Cantidad de puertos

Ejemplo: ``0 create switch S 4``

Crear host
----------

.. code-block:: shell
    
    <time> create host <host_name>

* `host_name` : Nombre del host

Ejemplo: ``0 create host PC``


Crear router
------------

.. code-block:: shell
    
    <time> create router <router_name> <interfaces>

* `router_name` : Nombre del router
* `interfaces` : Cantidad de interfases del router

Ejemplo: ``0 create router R 4``

Conectar
--------

.. code-block:: shell
    
    <time> connect <port1> <port2>

* `port1`, `port2` : Nombres de los puertos a conectar.

Ejemplo: ``0 connect PC_1 H_2``

Enviar
------

.. code-block:: shell
    
    <time> send <host_name> <data>

* `host_name` : Nombre del host que enviará la información.
* `data` : Serie de bits a evniar.

Ejemplo: ``0 send PC 10111010``

Enviar Frame
------------

.. code-block:: shell
    
    <time> send_frame <host_name> <destiny_mac> <hex_data>

* `host_name` : Nombre del host que enviará la información.
* `destiny_mac` : Dirección MAC destino.
* `hex_data` : Serie de bits a evniar en hexagesimal.

Ejemplo: ``0 send_frame PC 03EC F2CC48A3``

Al enviar un frame existe la probabilidad que los datos cambien debido a la simulación de errores. Esta probabilidad es bastante baja y será señalado por cada frame si existe en el log de los datos recibidos de cada host.


Enviar paquete IP
-----------------

.. code-block:: shell

    <time> send_packet <host_name> <destiny_ip> <hex_data>

* `host_name` : Nombre del host que enviará la información.
* `destiny_ip` : Dirección IP destino.
* `hex_data` : Serie de bits a evniar en hexagesimal.

Ejemplo: ``0 send_packet PC 10.6.100.20 F2CC48A3``

Desconectar
-----------

.. code-block:: shell
    
    <time> disconnect <port>

* `port` : Puerto a desconectar.

Ejemplo: ``0 disconnect PC_1``

Asignar Mac
-----------

.. code-block:: shell
    
    <time> mac <device_name>[:<interface>] <mac>

* `device_name` : Nombre del dispositivo.
* `interface` : Interfase a la que se le assigna la Mac
* `mac` : Mac a asignar.

Ejemplos:

  * ``0 mac PC 000A``
  * ``0 mac routerA:3 00A3``


Asignar IP
----------

.. code-block:: shell
    
    <time> ip <device_name>[:<interface>] <ip> <mask>

* `device_name` : Nombre del dispositivo.
* `interface` : Interfase a la que se le assigna la dirección IP
* `ip` : IP a asignar.
* `mask` : Máscara para identificar la subred.

Ejemplos:

  * ``0 ip PC 10.6.100.20 255.255.255.0``
  * ``0 ip routerA:3 10.6.100.1 255.255.0.0``

Editar las rutas de host o routers
----------------------------------

.. code-block:: shell
    
    <time> route <action:[add|remove|reset]> <device_name> <ip> <mask> <gateway> <interface>

* `action` : Una de las 3 opciones (``add``, ``remove`` o ``reset``). Crea, eleimina (una ruta) o reseta las rutas de un dispositivo.
* `device_name` : Nombre del dispositivo.
* `ip` : IP de la ruta.
* `mask` : Máscara de la ruta.
* `gateway` : Puerta de salida. Es el IP al cual se enviarán los datos que sean enrutados por esta ruta. Si es 0.0.0.0 entonces se envian directamente a la dirección IP de destino que tenía el paquete.
* `interface` : Interfase por la cual saldrán los paquetes que sean enrutados por esta ruta

Ejemplos:

  * ``0 route add routerA 10.6.122.0 255.255.255.0 10.6.100.122 1``
  * ``0 route remove routerA 10.6.122.0 255.255.255.0 10.6.100.122 1``
  * ``0 route reset routerA``



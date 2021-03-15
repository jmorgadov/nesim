Cómo funciona **nesim**
=======================

Dispositivos
------------

Nesim dispone de dos dispositivos principales: :py:class:`~devices.Hub` y :py:class:`~devices.PC` (host). Cada dispositivo contiene 1 o más puertos. El nombre de cada puerto es de la forma:

.. code-block:: text

    {Nombre del dispositivo}_{Número del puerto}

.. note::

    Las :py:class:`~devices.PC` solo tienen un puerto y su nombre es ``{Nombre de la PC}_1``

Hub
+++

    Un :py:class:`~devices.Hub` es un dispositivo que tiene varios puertos. Cuando un host envía información por un puerto el hub retransmite la misma por los demás puertos. Más adelante se explicará como se manejan las colisiones.

PC
++

    Una :py:class:`~devices.PC` (host) es un dispositivo que puede enviar y recibir información. El mismo puede ser conectado a otra :py:class:`~devices.PC` o un :py:class:`~devices.Hub`.

Un :py:class:`~devices.Cable` puede conectar dos puertos de dos dispositivos diferentes y además contiene en el campo :py:data:`~devices.Cable.value` el valor del bit que se encuentra en dicho cable.


Simulación
----------

Una vez comenzada la simulación se ejecuta el ciclo de la simulación (que reprensenta el paso de un milisegundo) mientras quede algún dispositivo enviando información, tenga por enviar, o queden instucciones por ejecutar. 

En cada milisegundo simulado ``t`` (iteración del ciclo) se ejecutan una serie de pasos que en su conjunto constituyen la base de la simulación de la red:

 * Ejecutar las instrucciones.
 * Resetear todos los dispositivos.
 * Actualizar todos los hosts.
 * Actualizar todos los hubs.
 * Recibir información en todos los hosts.

Ejecutar instrucciones
++++++++++++++++++++++

Al inicio de cada iteración del ciclo se cargan todas las instrucciones cuyo tiempo de ejecución coincida con el tiempo de simulación. Luego se ejecutan en el mismo orden que fueron escritas.

Resetear dispositivos
+++++++++++++++++++++

Luego de ejecutar las instruccones correspondientes se ejecuta el método :py:func:`~devices.Device.reset`. En este punto todos los hubs `escriben` 0 por cada uno de sus puertos.

Actualizar hosts
++++++++++++++++

Una vez todos los cables tienen valor 0, si un host debe transmitir información envía el bit correspondiente (se actualiza el valor del cable conectado al puerto del mismo).

Para el envío de información se dividen todos los datos en paquetes, aunque la información se sigue transmitiendo bit a bit. Cuando se termina de transmitir el ultimo bit de un paquete se carga el siguiente paquete a enviar si queda todavía información. 

Actualizar hubs
+++++++++++++++

Cuando todos los host escribieron la información que debían enviar (aquellos que estaban transmitiendo), entonces los hubs retransmiten esa información por todos sus puertos atendiendo a las siguientes reglas:

    * Si luego de actualizar los hosts todos los puertos del hub tienen como valor el bit 0, entonces se queda el bit 0 en cada puerto.
    * Si uno de los puertos tiene como valor el bit 1, entonces el hub escribe 1 en todos sus puertos.

.. note::

    Cada hub se actualiza un número de veces igual a la cantidad de hubs total en la red. Esto garantiza que la información de cada uno es retransitida a todos. En un futuro se optimizará este proceso.

Recibir información en los hosts
++++++++++++++++++++++++++++++++

Una vez todos los hubs han retransmitido la información entonces todos los hosts leen la información que queda en el cable. Luego se puede dividir el comportamiento en dos casos dependiendo si el host estaba o no enviando infomración:

* Si el host se encuentra transmitiendo información:

    Se comprueba que el bit que envió es igual al bit que se encuentra en el cable. En caso afirmativo no ocurre nada más y se pasa al siguiente host. En caso de que el bit leído sea diferente al bit transimitido entonces existe una colisión. En este último caso se detiene el envío y se espera una cantidad de milisegundos aleatoria para volver a enviar la información. 

    Cuando se detiene la transmisión en un host se define un tiempo aleatorio en el que tiene que esperar para reintenar el envío. Este tiempo está entre 1ms y 16ms por defecto. Por cada colision el tiempo máximo de este rango se dubplica (Si vuelve a ocurrir una colisión entonces se espera un tiempo aleatorio entre 1ms y 32ms). Además se reinicia el envío del paquete actual, o sea, si se estaba enviando el 3er bit del paquete, cuando se pueda seguir transmitiendo se empezará a enviar desde el primer bit del paquete actual.

    Una vez se termina de enviar un paquete y se carga el siguiente, el tiempo máximo de espera en caso de colisión se vuelve a setear en 16ms.    


* Si el host no está transmitiendo información:

    Se almacena momentaneamente cada cierto tiempo (menor que el ``signal_time``) el bit que lee. Finalmente a cada intervalo de ``signal_time`` se guarda como leído la moda de todos los bits almacenados en el último intervalo de ``signal_time``.

En caso de que ningún host esté transmitiendo y todavía la simulación esté en ejecución todos los host leerán el bit 0.
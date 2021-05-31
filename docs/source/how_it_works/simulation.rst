Simulación
==========

Una vez comenzada la simulación se ejecuta el ciclo de la simulación (que reprensenta el paso de un milisegundo) mientras quede algún dispositivo enviando información, tenga por enviar, o queden instucciones por ejecutar. 

En cada milisegundo simulado ``t`` (iteración del ciclo) se ejecutan una serie de pasos que en su conjunto constituyen la base de la simulación de la red:

 * Ejecutar las instrucciones.
 * Resetear todos los dispositivos.
 * Actualizar todos los dispositivos.
 * Recibir información en todos los dispositivos.

Ejecutar instrucciones
----------------------

Al inicio de cada iteración del ciclo se cargan todas las instrucciones cuyo tiempo de ejecución coincida con el tiempo de simulación. Luego se ejecutan en el mismo orden que fueron escritas.

Resetear dispositivos
---------------------

Luego de ejecutar las instruccones correspondientes se ejecuta el método :py:func:`~devices.Device.reset`. En este punto todos los hubs `escriben` 0 por cada uno de sus puertos.

Actualizar dispositivos y recibir información
---------------------------------------------

Al actualizar cada dispositivo, los mismos envían la información que deben transimitir. Posteriormente cada uno lee de cada uno de sus puertos y realiza las operaciones según el tipo de dispositivo.

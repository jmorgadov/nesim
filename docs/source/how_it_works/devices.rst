Dispositivos
============

Nesim dispone de dos dispositivos principales: :py:class:`~devices.Hub` y :py:class:`~devices.PC` (host). Cada dispositivo contiene 1 o más puertos. El nombre de cada puerto es de la forma:

.. code-block:: text

    {Nombre del dispositivo}_{Número del puerto}

.. note::

    Los :py:class:`~devices.Host` solo tienen un puerto y su nombre es ``{Nombre del host}_1``

Host
----

    Un :py:class:`~devices.Host` es un dispositivo que puede enviar y recibir información. Puede enviar y recibir paquetes de IP (mediante frames). El mismo contiene una tabla de rutas con las que puede (dado un paquete IP) decidir a que IP enviar el frame.

Hub
---

    Un :py:class:`~devices.Hub` es un dispositivo que tiene varios puertos. Cuando una información es recibida en alguno de sus puertos la misma es enviada por los puertos restantes. Si se recibe información por dos o más puertos a la vez se realiza una operación OR entre todos los datos y esta es la que se envía por los puertos. Esto permite que el dispositivo que envía un 0 note la colisión cuando hay otro dispositivo transmitiendo un 1.

Switch
------

    Los switch son dispositivos parecidos a los Hubs. El mismo restransmite la información que le llega de un puerto por los restantes. Se diferencia con el hub en que el switch recibe frames. Estos frames contienen información sobre la dirección MAC del dispositivo que los envía y el destinatario. El switch va guardando por cuales puertos están conectados los dispositivos según sus direcciones MAC y de esta forma al recibir un frame sabe por que puerto enviarlo directamente. En caso de no tener esta información para una dirección MAC determinada entonces se envía el frame por todos los puertos.

Routers
-------

    Los routers son como hosts con varios puertos. Tienen también una tabla de rutas y varias interfases (puertos). Se encargan de dirigir los paquetes IP hasta su destino entre las diferentes subredes.


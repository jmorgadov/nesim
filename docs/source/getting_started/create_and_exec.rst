Crear y ejecutar una simulación
===============================

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

Al comenzar una simulación se carga un archivo llamado ``config.txt`` (En caso de no existir se crea uno por defecto). Este archivo contiene la configuración básica para las simulaciones. Cada línea de este archivo contiene un par (``key`` ``value``) donde cada llave representa el nombre de uno de los parámetros a configurar y a su lado el valor correspondiente. Los parametros modificables son:

 - ``signal_time``, cuyo valor por defecto es ``10``.
 - ``error_detection``, cuyo valor por defecto es ``simple_hash``.

El parámetro ``error_detection`` (puede ser: ``simple_hash`` o ``hamming``).

Logs
----

Al finalizar la ejecución de la simulación queda guardado por cada dispositivo un archivo `.txt` con los logs de cada uno respectivamente.

Por ejemplo, al ejecuar la simulación anterior los logs del host ``PCA`` que se guardan en ``PCA.txt`` son:

.. code-block:: text

    -------------------------------------------------------------------------------
    | Time (ms)  |    Device    |     Action     |              Info              |
    -------------------------------------------------------------------------------
    |     0      |     PCA      |   Connected    |                                |
    |     0      |     PCA      |      Sent      | 0                              |
    |     10     |     PCA      |      Sent      | 1                              |
    |     20     |     PCA      |      Sent      | 1                              |
    |     30     |     PCA      |      Sent      | 1                              |
    |     40     |     PCA      |      Sent      | 0                              |
    |     50     |     PCA      |      Sent      | 1                              |
    |     60     |     PCA      |      Sent      | 0                              |
    |     70     |     PCA      |      Sent      | 1                              |
    |     89     |     PCA      |    Received    | 0                              |
    -------------------------------------------------------------------------------

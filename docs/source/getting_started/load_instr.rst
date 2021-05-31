Cargar instrucciones
====================

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

Esta función busca por defecto un archivo ``script.txt`` donde mismo se ejectuta el ``.py``. En caso que se quiera cargar otro archivo se puede especificar la ruta del mismo:

.. code-block:: python

    instr = nesim.load_instructions('path/of/instructions/file.txt')
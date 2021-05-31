Diagrama de clases de dispositivos
==================================

.. figure:: /how_it_works/class_diagram.jpg
   :alt: Diagrama de clases de los dispositivos
   :align: center
   :width: 400

Es válido aclarar que el hub no es incluido en los dispositivos con múltiples puertos ya que estos últimos reciben la información por frames. Tambíen se aclara que los switchs no son de tipo ``FrameSender`` ya que ellos por si solos no envían frames. Solo reenvian la información de un puerto a otro. 
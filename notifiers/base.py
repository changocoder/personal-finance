# notifiers/base.py
"""
Definición del Protocol base para todos los notificadores.
Cualquier clase que implemente el método `send` es un Notifier válido.
"""

from typing import Protocol


class Notifier(Protocol):
    """
    Protocol que define la interfaz para todos los notificadores.

    Cualquier clase que tenga un método `send` con esta firma
    será considerada un Notifier válido (Duck Typing).
    """

    def send(self, consumos: list, cotizacion: float) -> bool:
        """
        Envía una notificación con el reporte de consumos.

        Args:
            consumos: Lista de diccionarios con los consumos procesados
            cotizacion: Cotización del dólar utilizada

        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        ...


# inventory_api/app/utils/enums.py

import enum

class TransactionType(enum.Enum):
    """Defines allowed types for inventory transactions."""
    entrada = 'entrada'
    salida = 'salida'
    ajuste = 'ajuste'
    # You might add 'transferencia_origen' and 'transferencia_destino' here
    # if you use them internally, matching your service logic.
    # Let's include them as per potential internal use:
    transferencia_origen = 'transferencia_origen'
    transferencia_destino = 'transferencia_destino'

    def __str__(self):
        return self.value

class UnitMeasure(enum.Enum):
    """Defines allowed unit measures for products."""
    unidad = 'unidad'
    litro = 'litro'
    kilogramo = 'kilogramo'
    metro = 'metro'
    caja = 'caja'

    def __str__(self):
        return self.value
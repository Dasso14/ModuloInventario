from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    ENTRADA = "entrada"  # Alineado con el ENUM de PostgreSQL
    SALIDA = "salida"
    AJUSTE = "ajuste"


@dataclass
class Transaction:
    # Campos obligatorios (sin valores por defecto)
    transaction_id: int
    product_id: int
    location_id: int
    quantity: float
    transaction_type: TransactionType
    user_id: int  # Campo requerido por el esquema de la DB

    # Campos opcionales (con valores por defecto)
    transaction_date: datetime = datetime.now()
    reference_number: str = None
    notes: str = None
    related_transaction: int = None
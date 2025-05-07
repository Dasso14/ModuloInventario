# inventory_api/app/models/supplier.py

from ..db import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True, name='supplier_id')
    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255), nullable=True) # Matches schema name
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True) # Matches schema length
    address = db.Column(db.Text, nullable=True)
    tax_id = db.Column(db.String(50), nullable=True) # Added based on schema

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # products backref defined in Product model

    def __repr__(self):
        return f"<Supplier {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_name': self.contact_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'tax_id': self.tax_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
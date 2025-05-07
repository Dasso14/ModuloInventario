# inventory_api/app/models/barcode.py
from ..db import db
from datetime import datetime

class Barcode(db.Model):
    __tablename__ = 'barcodes'

    id = db.Column(db.Integer, primary_key=True, name='barcode_id') # Map to barcode_id
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False) # Map to product_id
    barcode = db.Column(db.String(255), unique=True, nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = db.relationship('Product', backref=db.backref('barcodes', lazy='dynamic'))

    def __repr__(self):
        return f"<Barcode {self.barcode} for Product {self.product_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'barcode': self.barcode,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
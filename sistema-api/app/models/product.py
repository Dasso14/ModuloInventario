# inventory_api/app/models/product.py

from ..db import db
from datetime import datetime
# Import the enum from utils
from ..utils.enums import UnitMeasure
from .category import Category # Import Category for relationship
from .supplier import Supplier # Import Supplier for relationship


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, name='product_id')
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=True)

    unit_cost = db.Column(db.Numeric(15, 2), nullable=True)
    unit_price = db.Column(db.Numeric(15, 2), nullable=True)
    # Use the imported enum
    unit_measure = db.Column(db.Enum(UnitMeasure), default=UnitMeasure.unidad, nullable=False)
    weight = db.Column(db.Numeric(10, 2), nullable=True)
    volume = db.Column(db.Numeric(10, 2), nullable=True)
    min_stock = db.Column(db.Integer, default=0, nullable=False)
    max_stock = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))
    supplier = db.relationship('Supplier', backref=db.backref('products', lazy='dynamic'))


    def __repr__(self):
        return f"<Product {self.sku} - {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'unit_price': str(self.unit_price) if self.unit_price is not None else None,
            'unit_cost': str(self.unit_cost) if self.unit_cost is not None else None,
            'unit_measure': self.unit_measure.value, # Return the string value
            'weight': str(self.weight) if self.weight is not None else None,
            'volume': str(self.volume) if self.volume is not None else None,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'is_active': self.is_active,
            'category_id': self.category_id,
            'supplier_id': self.supplier_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_name': self.category.name if self.category else None,
            'supplier_name': self.supplier.name if self.supplier else None
        }
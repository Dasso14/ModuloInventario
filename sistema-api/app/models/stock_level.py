# inventory_api/app/models/stock_level.py

from ..db import db
from datetime import datetime
from sqlalchemy import UniqueConstraint, text # Import UniqueConstraint and text for view mapping


class StockLevel(db.Model):
    __tablename__ = 'stock_levels'

    # Maps to schema's stock_id SERIAL PRIMARY KEY
    id = db.Column(db.Integer, primary_key=True, name='stock_id')

    # Maps to schema's product_id and location_id, part of the UNIQUE constraint
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)

    quantity = db.Column(db.Numeric(15, 2), nullable=False) # Matches schema precision
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) # Schema default is CURRENT_TIMESTAMP

    # Explicitly define the unique constraint matching the schema
    __table_args__ = (UniqueConstraint('product_id', 'location_id', name='stock_levels_product_id_location_id_key'),)


    # Relationships
    # Using viewonly=True because updates to stock_levels are handled by the DB trigger,
    # not directly via model relationships from Product/Location instances.
    product = db.relationship('Product', backref=db.backref('stock_levels', lazy='dynamic', viewonly=True))
    location = db.relationship('Location', backref=db.backref('stock_levels', lazy='dynamic', viewonly=True))

    def __repr__(self):
        return f"<StockLevel Product {self.product_id} at Location {self.location_id}: {self.quantity}>"

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'location_id': self.location_id,
            'quantity': str(self.quantity),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            # Include names from relationships for API responses
            'product_name': self.product.name if self.product else None,
            'location_name': self.location.name if self.location else None
        }


# Model for the low_stock VIEW
# Mapping to a view requires careful configuration.
# We define the columns that the VIEW is expected to return.
# The primary key for a view mapping can be tricky;
# a composite key based on product_id and location_id is a reasonable approach.
class LowStockItem(db.Model):
    # Use __tablename__ to specify the view name
    __tablename__ = 'low_stock'

    # Define columns matching the view's output
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    sku = db.Column(db.String(50), nullable=False) # From products table via view
    product_name = db.Column(db.String(255), nullable=False) # From products table via view

    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), primary_key=True)
    location_name = db.Column(db.String(255), nullable=False) # From locations table via view

    quantity = db.Column(db.Numeric(15, 2), nullable=False) # From stock_levels via view
    min_stock = db.Column(db.Integer, nullable=False) # From products table via view

    # Important: Mapping to a view typically means reads only.
    # You usually don't have created_at/updated_at on a view result set directly.
    # If the view included timestamps, you could map them here.

    # Note: __table_args__ can be used for views, e.g., to specify autoload=True
    # but defining columns explicitly is clearer if you know the view structure.
    # __table_args__ = {'autoload': True, 'extend_existing': True} # Example if you let SQLAlchemy inspect the view

    # Relationships (Optional but can make queries easier if view joins correctly)
    # These relationships are based on the columns present IN THE VIEW.
    # If the view joins products and locations, these relationships can work.
    product_rel = db.relationship('Product', foreign_keys=[product_id], uselist=False, viewonly=True)
    location_rel = db.relationship('Location', foreign_keys=[location_id], uselist=False, viewonly=True)


    def __repr__(self):
        return f"<LowStockItem Product {self.product_id} at Location {self.location_id} - Qty: {self.quantity} Min: {self.min_stock}>"

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'sku': self.sku,
            'product_name': self.product_name,
            'location_id': self.location_id,
            'location_name': self.location_name,
            'quantity': str(self.quantity),
            'min_stock': self.min_stock,
        }
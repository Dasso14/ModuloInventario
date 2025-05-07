# inventory_api/app/models/inventory_transaction.py

from ..db import db
from datetime import datetime
# Import the enum from utils
from ..utils.enums import TransactionType
from .product import Product # Import Product for relationship
from .location import Location # Import Location for relationship
from .user import User # Import User for relationship


class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    id = db.Column(db.Integer, primary_key=True, name='transaction_id')
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Use the imported enum
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)
    quantity = db.Column(db.Numeric(15, 2), nullable=False)

    reference_number = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Schema is NOT NULL

    related_transaction_id = db.Column(db.Integer, db.ForeignKey('inventory_transactions.transaction_id'), name='related_transaction', nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    # Relationships
    product = db.relationship('Product', backref=db.backref('transactions', lazy='dynamic'))
    location = db.relationship('Location', backref=db.backref('transactions', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('inventory_transactions', lazy='dynamic'))

    related_transaction = db.relationship('InventoryTransaction',
                                          remote_side=[id],
                                          backref=db.backref('linked_transaction', uselist=False))

    def __repr__(self):
        return f"<InventoryTransaction {self.transaction_type.value} of {self.quantity} for Product {self.product_id} at Location {self.location_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_type': self.transaction_type.value, # Return the string value
            'product_id': self.product_id,
            'location_id': self.location_id,
            'quantity': str(self.quantity),
            'reference_number': self.reference_number,
            'notes': self.notes,
            'user_id': self.user_id,
            'related_transaction_id': self.related_transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product_name': self.product.name if self.product else None,
            'location_name': self.location.name if self.location else None,
            'user_name': self.user.username if self.user else None
        }
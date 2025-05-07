# inventory_api/app/models/location_transfer.py

from ..db import db
from datetime import datetime

class LocationTransfer(db.Model):
    __tablename__ = 'location_transfers'

    id = db.Column(db.Integer, primary_key=True, name='transfer_id')
    transfer_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Schema default is CURRENT_TIMESTAMP

    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)
    to_location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=False)

    quantity = db.Column(db.Numeric(15, 2), nullable=False) # Matches schema precision

    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Schema is NOT NULL

    # Schema DOES NOT have from_transaction_id or to_transaction_id in this table.
    # Remove these columns from the model to match the schema exactly.
    # from_transaction_id = db.Column(db.Integer, db.ForeignKey('inventory_transactions.transaction_id'), nullable=False)
    # to_transaction_id = db.Column(db.Integer, db.ForeignKey('inventory_transactions.transaction_id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # Schema default is CURRENT_TIMESTAMP
    # Schema does not have 'updated_at'. Remove.
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    product = db.relationship('Product', backref=db.backref('transfers', lazy='dynamic'))
    # Specify foreign_keys for relationships to the same table (locations)
    from_location = db.relationship('Location', foreign_keys=[from_location_id], backref=db.backref('outgoing_transfers', lazy='dynamic'))
    to_location = db.relationship('Location', foreign_keys=[to_location_id], backref=db.backref('incoming_transfers', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('location_transfers', lazy='dynamic'))

    # Removed relationships to transaction IDs as they are not in schema's transfer table
    # from_transaction = db.relationship('InventoryTransaction', foreign_keys=[from_transaction_id], backref=db.backref('outgoing_transfer_link', uselist=False))
    # to_transaction = db.relationship('InventoryTransaction', foreign_keys=[to_transaction_id], backref=db.backref('incoming_transfer_link', uselist=False))


    def __repr__(self):
        return f"<LocationTransfer Product {self.product_id} from {self.from_location_id} to {self.to_location_id} quantity {self.quantity}>"

    def to_dict(self):
        return {
            'id': self.id,
            'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
            'product_id': self.product_id,
            'from_location_id': self.from_location_id,
            'to_location_id': self.to_location_id,
            'quantity': str(self.quantity),
            'notes': self.notes,
            'user_id': self.user_id,
            # Removed transaction IDs
            # 'from_transaction_id': self.from_transaction_id,
            # 'to_transaction_id': self.to_transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None, # Removed
            'product_name': self.product.name if self.product else None,
            'from_location_name': self.from_location.name if self.from_location else None,
            'to_location_name': self.to_location.name if self.to_location else None,
            'user_name': self.user.username if self.user else None # Assuming User model has username
        }
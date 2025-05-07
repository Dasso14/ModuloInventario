# inventory_api/app/models/location.py

from ..db import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, name='location_id')
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    storage_capacity = db.Column(db.Numeric(15, 2), nullable=True) # Added based on schema

    # Self-referential relationship mapping to parent_location schema column
    parent_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'), name='parent_location', nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    parent = db.relationship('Location', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    # transactions backref defined in InventoryTransaction model
    # stock_levels backref defined in StockLevel model
    # outgoing_transfers backref defined in LocationTransfer
    # incoming_transfers backref defined in LocationTransfer


    def __repr__(self):
        return f"<Location {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'storage_capacity': str(self.storage_capacity) if self.storage_capacity is not None else None,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
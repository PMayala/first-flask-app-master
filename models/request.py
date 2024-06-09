from db import db


class RequestModel(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), unique=False, nullable=False)
    household = db.relationship("HouseholdModel", back_populates="requests")
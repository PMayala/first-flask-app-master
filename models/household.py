from db import db


class HouseholdModel(db.Model):
    __tablename__ = "households"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    requests = db.relationship("RequestModel", back_populates="household", lazy="dynamic")
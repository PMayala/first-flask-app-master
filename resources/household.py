import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from  sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import HouseholdSchema
from db import db
from models.household import HouseholdModel


household_blp = Blueprint(
    "households",
    __name__,
    description="Operations on households"
    )


@household_blp.route("/households")
class HouseholdsList(MethodView):
    """
    Represents a collection of households.
    """
    @household_blp.response(200, HouseholdSchema(many=True))
    def get(self):
        """
        Retrieves a list of all households.
        
        Returns:
            dict: A dictionary containing the list of households.
        """
        households = HouseholdModel.query.all()
        return households

    @household_blp.arguments(HouseholdSchema)
    @household_blp.response(201, HouseholdSchema)
    def post(self, household_data):
        """
        Create a new household with the provided data.

        Returns:
            tuple: A tuple containing the new household data and the HTTP
            status code.

        Raises:
            HTTPException: If the request data is missing required keys or
            if the household already exists.
        """
        new_household = HouseholdModel(**household_data)
        try:
            db.session.add(new_household)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A household with the same area and address already exists."
            )
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while inserting the household.")
        
        return {
            'id': new_household.id,
            'area': new_household.area,
            'address': new_household.address
        }, 201



@household_blp.route("/households/<string:household_id>")
class Household(MethodView):
    """
    Represents a single household.
    """

    @household_blp.response(200, HouseholdSchema)
    def get(self, household_id):
        """
        Retrieve a household by its ID.

        Args:
            household_id (int): The ID of the household to retrieve.

        Returns:
            dict: The household information.

        Raises:
            404: If the household is not found.
        """
        household = HouseholdModel.query.get_or_404(household_id)
        return household

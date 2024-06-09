import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.request import RequestModel
from schemas import RequestSchema
from db import db
from  sqlalchemy.exc import SQLAlchemyError

request_blp = Blueprint(
    "requests",
    __name__,
    description="Operations on collection requests"
    )


@request_blp.route("/requests")
class Request(MethodView):
    @request_blp.arguments(RequestSchema)
    def post(self, request_data):
        """
        Create a new request with the provided data.

        This function creates a new request based on the data provided in
        the request payload.

        Returns:
            tuple: A tuple containing the newly created request and
            the HTTP status code.
        """
        new_request = RequestModel(**request_data)
        try:
            db.session.add(new_request)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))
        return {
        'id': new_request.id,
        'amount': new_request.amount,
        'status': new_request.status,
        'household_id': new_request.household_id
        }, 201


@request_blp.route("/requests/<int:request_id>")
class RequestDetails(MethodView):
    @request_blp.response(200, RequestSchema)
    def get(self, request_id):
        """
        Retrieve a request by its ID.

        Args:
            request_id (int): The ID of the request to retrieve.

        Returns:
            dict: The request object.

        Raises:
            NotFound: If the request with the given ID is not found.
        """
        req = RequestModel.query.get_or_404(request_id)
        return req
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from db import db
from models.admin import AdminModel
from models.user import UserModel
from schemas import AdminSchema, UserSchema
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_blp = Blueprint("admins", "admins", description="Operations on admins")

@admin_blp.route("/admin/register")
class AdminRegister(MethodView):
    @admin_blp.arguments(AdminSchema)
    def post(self, admin_data):
        if AdminModel.query.filter(AdminModel.username == admin_data["username"]).first():
            abort(409, message="Admin already exists")

        admin = AdminModel(
            username=admin_data["username"],
            password=pbkdf2_sha256.hash(admin_data["password"]),
            email=admin_data["email"]
        )
        try:
            db.session.add(admin)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logger.error("IntegrityError: Admin creation failed due to existing admin.")
            abort(409, message="Admin already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemyError: {e}")
            abort(500, message="An error occurred while creating the admin.")
        
        logger.info(f"Admin {admin.username} created successfully.")
        return {"message": "Admin created successfully"}, 201

@admin_blp.route("/admin/login")
class AdminLogin(MethodView):
    @admin_blp.arguments(AdminSchema)
    def post(self, admin_data):
        admin = AdminModel.query.filter(AdminModel.username == admin_data["username"]).first()
        if not admin or not pbkdf2_sha256.verify(admin_data["password"], admin.password):
            logger.warning(f"Invalid login attempt for admin username: {admin_data['username']}")
            abort(401, message="Invalid username or password")

        access_token = create_access_token(identity=admin.id)
        logger.info(f"Admin {admin.username} logged in successfully.")
        return {"access_token": access_token}, 201

@admin_blp.route("/admin/users")
class AdminManageUsers(MethodView):
    @jwt_required()
    @admin_blp.response(200, UserSchema(many=True))
    def get(self):
        admin_id = get_jwt_identity()
        AdminModel.query.get_or_404(admin_id)
        users = UserModel.query.all()
        return users

    @jwt_required()
    @admin_blp.arguments(UserSchema)
    @admin_blp.response(201, UserSchema)
    def post(self, user_data):
        admin_id = get_jwt_identity()
        AdminModel.query.get_or_404(admin_id)

        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="User already exists")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"]
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logger.error("IntegrityError: User creation failed due to existing user.")
            abort(409, message="User already exists.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemyError: {e}")
            abort(500, message="An error occurred while creating the user.")
        
        logger.info(f"User {user.username} created successfully.")
        return {"message": "User created successfully"}, 201

@admin_blp.route("/admin/users/<int:user_id>")
class AdminManageSingleUser(MethodView):
    @jwt_required()
    @admin_blp.response(200, UserSchema)
    def get(self, user_id):
        admin_id = get_jwt_identity()
        AdminModel.query.get_or_404(admin_id)
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    @admin_blp.arguments(UserSchema)
    @admin_blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        admin_id = get_jwt_identity()
        AdminModel.query.get_or_404(admin_id)
        user = UserModel.query.get_or_404(user_id)

        user.username = user_data["username"]
        user.password = pbkdf2_sha256.hash(user_data["password"]) if user_data.get("password") else user.password
        user.email = user_data["email"]

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemyError: {e}")
            abort(500, message="An error occurred while updating the user.")
        
        logger.info(f"User {user.username} updated successfully.")
        return user

    @jwt_required()
    @admin_blp.response(200, AdminSchema)
    def delete(self, user_id):
        admin_id = get_jwt_identity()
        AdminModel.query.get_or_404(admin_id)
        user = UserModel.query.get_or_404(user_id)
        
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemyError: {e}")
            abort(500, message="An error occurred while deleting the user.")
        
        logger.info(f"User {user.username} deleted successfully.")
        return {"message": "User deleted successfully"}

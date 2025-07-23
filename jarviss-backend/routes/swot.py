from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from services.ia_service import swot_from_db

swot_bp = Blueprint('swot', __name__)

@swot_bp.route('/swot', methods=['GET'])
@jwt_required()
def get_swot():
    user_id = get_jwt_identity()
    swot = swot_from_db(user_id, db)
    return jsonify(swot) 
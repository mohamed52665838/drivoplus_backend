from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from model.NotificationModel import NotificationModel
from database import databaseInstance
import requests
import json



# This only for test

notification_bp = Blueprint('notification', __name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(token, message):
    headers = {
        'Content-Type': 'application/json',
    }
    payload = {
        "to": token,
        "title": message.get("title"),
        "body": message.get("body"),
        "data": message.get("data"),
    }

    response = requests.post(EXPO_PUSH_URL, json=payload, headers=headers)
    return response.json()

@notification_bp.route('/send_notification', methods=['POST'])
def send_notification():
    """
        @data:
            -token: str
            -category: enum(distraction_alert, physical_alert, mental_alert)
            -user_id
    """
    data = request.json
    token = data.get('token')
    category = data.get('category')

    print(data)
    print(token) 
    print(category) 
    print(data.get('user_id'))
    if not token or not category:
        return jsonify({"error": "Token and category are required"}), 400

    # Logique de notification basée sur la catégorie
    messages = {
        "distraction_alert": {
            "title": "🚨 Distraction Alert",
            "body": "Vous êtes distrait. Faites attention à la route !",
            "data": {"category": "distraction_alert"}
        },
        "physical_alert": {
            "title": "⚠️ Physical Condition Alert",
            "body": "Prenez une pause, votre état physique nécessite de l'attention.",
            "data": {"category": "physical_alert"}
        },
        "mental_alert": {
            "title": "🔔 Mental Condition Alert",
            "body": "Prenez une pause, votre état mental nécessite de l'attention.",
            "data": {"category": "mental_alert"}
        }
    }

    message = messages.get(category, {"title": "General Alert", "body": "You have a new notification", "data": {"category": "general"}})

    # Envoi de la notification push
    result = send_push_notification(token, message)

    # Enregistrement de la notification dans la base de données
    user_id = data.get("user_id")  # Assure-toi que l'ID utilisateur est passé dans la requête
    if user_id:
        try:
            # Créer et enregistrer la notification dans la base de données MongoDB
            notification = NotificationModel(
                user_id=user_id,
                category=category,
                title=message["title"],
                body=message["body"],
                data=message["data"]
            )
            notification.timestamp_snapshot()  # Met à jour les timestamps
            databaseInstance.db.notifications.insert_one(notification.dict())  # Enregistre dans MongoDB
        except ValidationError as e:
            return jsonify({"error": "Invalid notification data", "details": str(e)}), 400

    return jsonify(result)

@notification_bp.route('/user_notifications', methods=['GET'])
def get_user_notifications():
    user_id = request.args.get('user_id')  # Récupérer l'ID utilisateur via les paramètres de l'URL
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Pagination (optionnelle)
    page = int(request.args.get('page', 1))  # Page par défaut = 1
    limit = int(request.args.get('limit', 10))  # Limite par défaut = 10 notifications par page
    skip = (page - 1) * limit

    # Récupération des notifications de l'utilisateur
    notifications = list(databaseInstance.db.notifications.find({"user_id": user_id}).skip(skip).limit(limit))

    # Transformer les résultats pour les renvoyer sous un format JSON valide
    for notification in notifications:
        notification["_id"] = str(notification["_id"])  # Convertir l'ObjectId en string pour le JSON

    return jsonify(notifications)


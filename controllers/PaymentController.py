import stripe
import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from database import databaseInstance
from util import Collections

# Charger les variables d'environnement
load_dotenv()

# Configurer Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Créer le Blueprint
payment_blueprint = Blueprint('payment', __name__)

@payment_blueprint.route("/create-payment-intent", methods=["POST"])
def create_payment():
    try:
        data = request.json
        print("📌 Requête reçue :", data)

        amount = int(data["amount"])  # Montant en centimes (ex: 10€ = 1000)
        currency = data.get("currency", "usd")  # Devise par défaut
        user_email = data.get("email")  # Email de l'utilisateur

        print("✅ Données extraites - Amount:", amount, "Currency:", currency, "Email:", user_email)

        # ✅ Créer un PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            receipt_email=user_email,
            automatic_payment_methods={"enabled": True}  # 🔥 Active automatiquement les méthodes de paiement
        )

        print("💳 Paiement Intent Créé :", intent)

        # ✅ Une fois le paiement réussi, on met à jour l'état de l'utilisateur
        if intent["status"] == "requires_payment_method":
            user_collection = databaseInstance.db.get_collection(Collections.USER)
            user_collection.update_one(
                {"email": user_email},
                {"$set": {"is_active_premium": True}}  # 🟢 Activation Premium
            )
            print(f"🎉 Utilisateur {user_email} est maintenant Premium!")

        return jsonify({
            "message": "PaymentIntent créé avec succès ✅",
            "clientSecret": intent["client_secret"]
        })

    except Exception as e:
        print("❌ ERREUR :", str(e))
        return jsonify({"error": str(e)}), 400

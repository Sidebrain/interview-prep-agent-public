import os
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import stripe

from app.services.env_keys import STRIPE_API_KEY

# from dotenv import load_dotenv

# load_dotenv(".env.local")

stripe.api_key = STRIPE_API_KEY


router = APIRouter()


@router.post("/create-checkout-session")
async def create_checkout_session() -> dict:
    try:
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=[
                {
                    "price": "price_1Q9okcAMWKJyocPOqCnfhizh",
                    "quantity": 2,
                }
            ],
            mode="payment",
            return_url=os.getenv("CLIENT_URL")
            + "/return?session_id={CHECKOUT_SESSION_ID}",
        )
    except Exception as e:
        return {"error": str(e)}
    return jsonable_encoder({"clientSecret": session.client_secret})

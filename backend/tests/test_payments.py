import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app

client = TestClient(app)


@pytest.fixture
def mock_stripe_session():
    mock_session = MagicMock()
    mock_session.client_secret = "client_secret"
    return mock_session


@patch("stripe.checkout.Session.create")
def test_create_checkout_session(mock_create, mock_stripe_session):
    mock_create.return_value = mock_stripe_session
    response = client.post("/api/v1/payments/create-checkout-session")
    assert response.status_code == 200
    assert response.json() == {"clientSecret": "client_secret"}

    mock_create.assert_called_once_with(
        ui_mode="embedded",
        line_items=[
            {
                "price": "price_1Q9okcAMWKJyocPOqCnfhizh",
                "quantity": 2,
            }
        ],
        mode="payment",
        return_url="http://localhost:3000/return?session_id={CHECKOUT_SESSION_ID}",
    )


@patch("stripe.checkout.Session.create")
def test_create_checkout_session_error(mock_create):
    mock_create.side_effect = Exception("Stripe API error")
    response = client.post("/api/v1/payments/create-checkout-session")

    assert response.status_code == 200
    assert response.json() == {"error": "Stripe API error"}

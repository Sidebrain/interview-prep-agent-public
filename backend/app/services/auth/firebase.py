from firebase_admin import credentials, initialize_app, auth

default_app = initialize_app(
    credential=credentials.Certificate("secrets/firebase-admin-key.json")
)


async def verify_token(token: str) -> dict:
    try:
        # verify the token
        decoded_token = auth.verify_id_token(token, app=default_app)

        # get the user id from the decoded token
        uid = decoded_token.get("uid")

        # user data
        user = auth.get_user(uid)
        print(user)
        return {
            "uid": uid,
            "email": user.email,
            "email_verified": user.email_verified,
        }

    except auth.InvalidIdTokenError:
        return {"error": "Invalid token"}
    except auth.ExpiredIdTokenError:
        return {"error": "Expired token"}
    except auth.RevokedIdTokenError:
        return {"error": "Revoked token"}
    except auth.CertificateFetchError:
        return {"error": "Unable to fetch certificate"}
    except auth.UserDisabledError:
        return {"error": "User is disabled"}

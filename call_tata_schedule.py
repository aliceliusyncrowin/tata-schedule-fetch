import base64
import os
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

BASE = "https://analytics-dev.tatapower.com/TpcDSMPortal/api"

# Headers that make us look like a normal client (defeats WAF 406 blocks)
COMMON_HEADERS = {
    "User-Agent": "PostmanRuntime/7.39.0",   # or a browser UA string
    "Accept": "*/*",
}

# --- Step 1: encrypt the password using the public key ---
def load_public_key_from_vault():
    pem_text = os.environ["PUBLIC_KEY_PEM"]
    return serialization.load_pem_public_key(
        pem_text.encode("utf-8"))

def encrypt_public_key():
    public_key = load_public_key_from_vault()

    if not public_key:
        raise ValueError("PUBLIC_KEY environment variable is not set.")
    encrypted = public_key.encrypt(
        os.environ["TATA_SCHEDULE_PASSWORD"].encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),            
            label=None
        )
    )

    encrypted_password = base64.b64encode(encrypted).decode()
    return encrypted_password


# --- Step 2: get an access token ---
def get_token(password: str) -> str:
    resp = requests.post(
        f"{BASE}/token",
        headers=COMMON_HEADERS,
        data={  # form-urlencoded, matches Postman's "urlencoded" body
            "grant_type": "password",
            "username": os.environ["TATA_SCHEDULE_USERNAME"],
            "password": password,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]  # adjust key if the response differs


# --- Step 3: call the utilityData endpoint ---
def get_utility_data(token: str, plant_name: str, date: str, schd_rev_no: int = -1) -> dict:
    resp = requests.post(
        f"{BASE}/utilityData",
        headers={**COMMON_HEADERS, "Authorization": f"Bearer {token}"},
        json={  # JSON body, matches Postman's "raw"/json body
            "plant_name": plant_name,
            "date": date,
            "schd_rev_no": schd_rev_no,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()




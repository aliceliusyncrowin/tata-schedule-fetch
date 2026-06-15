import base64
import os
import logging
import requests
from typing import cast
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

BASE = "https://analytics-dev.tatapower.com/TpcDSMPortal/api"

# Headers that make us look like a normal client (defeats WAF 406 blocks)
COMMON_HEADERS = {
    "User-Agent": "PostmanRuntime/7.39.0",  # or a browser UA string
    "Accept": "*/*",
}


# --- Step 1: encrypt the password using the public key ---
def load_public_key_from_vault() -> rsa.RSAPublicKey:
    pem_value = os.environ.get("PUBLIC_KEY_PEM")
    if not pem_value:
        raise ValueError("PUBLIC_KEY_PEM environment variable is not set.")

    pem_text = pem_value.strip().replace("\\r\\n", "\n").replace("\\n", "\n")

    try:
        return cast(
            rsa.RSAPublicKey,
            serialization.load_pem_public_key(pem_text.encode("utf-8")),
        )
    except ValueError as exc:
        raise ValueError(
            "PUBLIC_KEY_PEM does not contain a valid PEM-encoded public key."
        ) from exc


def encrypt_public_key():
    public_key = load_public_key_from_vault()
    encrypted = public_key.encrypt(
        os.environ["TATA_SCHEDULE_PASSWORD"].encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    encrypted_password = base64.b64encode(encrypted).decode()
    logging.info(
        "Encrypted password generated, length=%d", len(encrypted_password)
    )
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
    logging.info("Token response status=%s", resp.status_code)
    if resp.status_code >= 400:
        logging.info("Token response body=%s", resp.text[:1000])
    resp.raise_for_status()
    token = resp.json()["access_token"]  # adjust key if the response differs
    logging.info("Token received, length=%d", len(token))
    return token


# --- Step 3: call the utilityData endpoint ---
def get_utility_data(
    token: str, plant_name: str, date: str, schd_rev_no: int = -1
) -> dict:
    payload = {
        "plant_name": plant_name,
        "date": date,
        "schd_rev_no": schd_rev_no,
    }
    logging.info(
        "UtilityData request prepared, plant_name=%s date=%s schd_rev_no=%s",
        plant_name,
        date,
        schd_rev_no,
    )
    resp = requests.post(
        f"{BASE}/utilityData",
        headers={**COMMON_HEADERS, "Authorization": f"Bearer {token}"},
        json=payload,  # JSON body, matches Postman's "raw"/json body
        timeout=30,
    )
    logging.info("UtilityData response status=%s", resp.status_code)
    if resp.status_code >= 400:
        logging.info("UtilityData response body=%s", resp.text[:1000])
    resp.raise_for_status()
    data = resp.json()
    logging.info(
        "UtilityData response type=%s keys=%s",
        type(data).__name__,
        list(data.keys()) if isinstance(data, dict) else "n/a",
    )
    return data

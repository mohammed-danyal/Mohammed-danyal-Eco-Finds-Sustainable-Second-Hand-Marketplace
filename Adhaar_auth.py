"""
EcoFinds DigiLocker Sandbox KYC Prototype
Streamlit front-end + Python backend (single file).

HOW TO USE:
1. Register on a DigiLocker sandbox provider (Setu/Decentro/APISetu sandbox) and get sandbox credentials.
   - You will typically receive: x-client-id, x-client-secret, x-product-instance-id and base URLs for initiate_session / token / fetch.
   - See links in the chat for where to register.
2. Paste those values into the Streamlit input fields below.
3. Click 'Initiate DigiLocker Session' → app will display an authorizationUrl. Click it, login on DigiLocker sandbox and grant consent.
4. After consent, DigiLocker will redirect to your redirect_uri with a code param. Copy that code and paste into the app where requested.
5. Click 'Exchange Code' to get access token, then 'Fetch Documents' to pull the selected documents (Aadhaar/PAN/etc.).

NOTE: This is a sandbox/prototype flow. In production you will use the official DigiLocker partner onboarding process and the production endpoints/headers.
"""

import streamlit as st
import requests
import webbrowser
import time
from urllib.parse import urlencode

st.set_page_config(page_title="EcoFinds DigiLocker KYC Prototype", layout="wide")

st.title("EcoFinds — DigiLocker Sandbox KYC Prototype")
st.markdown("Build/demo Aadhaar/PAN verification using DigiLocker sandbox (consent-based). This is a prototype — configure sandbox provider endpoints and headers below.")

# ----------------------
# Configuration inputs
# ----------------------
st.sidebar.header("Sandbox / Credentials")
provider = st.sidebar.selectbox("Sandbox provider (choose one you registered with)", ["Setu / APISetu sandbox", "Decentro staging", "Other - custom endpoints"])

if provider == "Setu / APISetu sandbox":
    default_initiate = "https://sandbox.api-setu.in/digilocker/initiate-session"
    default_exchange = "https://sandbox.api-setu.in/digilocker/exchange-code"
    default_fetch = "https://sandbox.api-setu.in/digilocker/fetch-document"
elif provider == "Decentro staging":
    default_initiate = "https://in.staging.decentro.tech/v2/kyc/digilocker/initiate_session"
    default_exchange = "https://in.staging.decentro.tech/v2/kyc/digilocker/exchange_code"
    default_fetch = "https://in.staging.decentro.tech/v2/kyc/digilocker/fetch_document"
else:
    default_initiate = "https://your-sandbox/initiate"
    default_exchange = "https://your-sandbox/exchange"
    default_fetch = "https://your-sandbox/fetch"

initiate_url = st.sidebar.text_input("Initiate Session (POST)", value=default_initiate)
exchange_url = st.sidebar.text_input("Exchange Code (POST)", value=default_exchange)
fetch_url = st.sidebar.text_input("Fetch Document (GET/POST)", value=default_fetch)

x_client_id = st.sidebar.text_input("x-client-id / client_id", value="")
x_client_secret = st.sidebar.text_input("x-client-secret / client_secret", value="", type="password")
product_instance = st.sidebar.text_input("x-product-instance-id (if provided)", value="")
redirect_uri = st.sidebar.text_input("Redirect URI (set in sandbox app)", value="https://example.com/callback")

st.sidebar.markdown("---")
st.sidebar.write("For sandbox registration, visit APISetu / DigiLocker partner resources. Use sandbox credentials, not production.")

# ----------------------
# Helper functions
# ----------------------
headers_common = lambda: {
    **({"x-client-id": x_client_id} if x_client_id else {}),
    **({"x-client-secret": x_client_secret} if x_client_secret else {}),
    **({"x-product-instance-id": product_instance} if product_instance else {})
}

def initiate_session(payload=None):
    """Call the sandbox initiate-session endpoint. Many providers expect POST with basic payload.
    If your provider responds with an authorizationUrl, return it.
    """
    if payload is None:
        payload = {"requested_docs": ["Aadhaar", "PAN"], "purpose": "EcoFinds verification"}
    try:
        r = requests.post(initiate_url, json=payload, headers=headers_common(), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "status_code": getattr(e, 'response', None)}

def exchange_code(code):
    """Exchange the authorization code for an access token. Exact parameters depend on provider.
    Many providers accept a POST with code + redirect_uri.
    """
    body = {"code": code, "redirect_uri": redirect_uri}
    try:
        r = requests.post(exchange_url, json=body, headers=headers_common(), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_document(access_token, doc_type="Aadhaar"):
    """Fetch a document using the access token. Implementation depends on provider: some use GET with headers Authorization: Bearer <token>.
    """
    try:
        h = {**headers_common(), **{"Authorization": f"Bearer {access_token}"}}
        # Try GET first
        r = requests.get(fetch_url, params={"docType": doc_type}, headers=h, timeout=15)
        if r.status_code == 405 or r.status_code == 404:
            # try POST fallback
            r = requests.post(fetch_url, json={"docType": doc_type}, headers=h, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ----------------------
# Streamlit UI
# ----------------------
st.subheader("1) Initiate DigiLocker session")
with st.form("init_form"):
    requested = st.multiselect("Requested documents", options=["Aadhaar","PAN","DrivingLicense","VoterID"], default=["Aadhaar","PAN"])
    purpose = st.text_input("Purpose (shown to user in consent)", value="EcoFinds seller verification")

    submitted = st.form_submit_button("Initiate DigiLocker Session")
    if submitted:
        payload = {"requested_docs": requested, "purpose": purpose, "redirect_uri": redirect_uri}
        resp = initiate_session(payload)
        st.write("Response from initiate-session:")
        st.json(resp)
        if isinstance(resp, dict) and resp.get("authorizationUrl"):
            st.markdown("**Click below to open Sandbox DigiLocker and grant consent**")
            st.write(resp["authorizationUrl"])
            if st.button("Open Authorization URL in browser"):
                webbrowser.open(resp["authorizationUrl"], new=2)

st.subheader("2) Paste authorization code (after consent)")
code = st.text_input("Paste 'code' (the authorization code received in redirect)")
if st.button("Exchange code for token"):
    if not code:
        st.error("Paste the code param from the redirect URL.")
    else:
        token_resp = exchange_code(code)
        st.write("Token response:")
        st.json(token_resp)
        if token_resp.get("access_token"):
            st.success("Access token received — you can now fetch documents.")

st.subheader("3) Fetch documents & mark verified")
access_token = st.text_input("Access token (or paste token response access_token)")
doc_choice = st.selectbox("Document to fetch", ["Aadhaar","PAN","DrivingLicense","VoterID"]) 
if st.button("Fetch Document"):
    if not access_token:
        st.error("Provide access token (from token response) or exchange code first.")
    else:
        doc = fetch_document(access_token, doc_choice)
        st.write("Document response:")
        st.json(doc)
        # Simple verification logic: check for presence of name + verified flag
        name = None
        verified = False
        if isinstance(doc, dict):
            name = doc.get("name") or doc.get("data", {}).get("name")
            verified = doc.get("verified") or doc.get("data", {}).get("verified")
        if name:
            st.success(f"Document belongs to: {name}")
        if verified:
            st.balloons()
            st.markdown(":white_check_mark: **EcoFinds Verified** — show Verified badge on profile")

st.markdown("---")
st.markdown("**Notes & Next steps:**\n- Fill sandbox credentials and correct provider endpoints.\n- For production, register as DigiLocker requester or use MeitY-approved partner.\n- Keep keys secret; use server-side storage and secure redirect URIs.")


# --- end of file

import os
import random
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load environment variables
load_dotenv()

BREVO_API_KEY = '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'#os.getenv("BREVO_API_KEY")
SENDER_EMAIL = 'mddaniyal752@gmail.com'#os.getenv("SENDER_EMAIL")

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_brevo(to_email, otp):
    print("API Key:", BREVO_API_KEY)
    print("Sender Email:", SENDER_EMAIL)
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    


    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "Your OTP Verification Code"
    html_content = f"<p>Your OTP is: <b>{otp}</b></p>"

    sender = {"name": "OTP System", "email": SENDER_EMAIL}
    to = [{"email": to_email}]

    email = sib_api_v3_sdk.SendSmtpEmail(to=to, sender=sender, subject=subject, html_content=html_content)

    try:
        api_response = api_instance.send_transac_email(email)
        print("✅ OTP sent successfully via Brevo!")
    except ApiException as e:
        print(f"❌ Error: {e}")
send_email_brevo('nitte0505@gmail.com',generate_otp())

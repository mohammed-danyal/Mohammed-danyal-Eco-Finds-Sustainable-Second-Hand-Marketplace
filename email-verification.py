import os
import random
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load environment variables
load_dotenv()

BREVO_API_KEY =  os.getenv("BREVO_API_KEY")
SENDER_EMAIL =  os.getenv("SENDER_EMAIL")
SMS_SENDER = os.getenv("BREVO_SMS_SENDER")

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_brevo(to_email):
    otp = generate_otp()
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
    entered_otp = input('enter otp: ')
    if otp == entered_otp:
        print("Sucessfully logged in")
        return True
    else:
        return False

def send_otp_via_sms(phone_number, otp):
    """Send OTP via SMS using Brevo."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalSMSApi(sib_api_v3_sdk.ApiClient(configuration))

    message = f"Your OTP code is: {otp}"
    try:
        send_sms = sib_api_v3_sdk.SendTransacSms(
            sender=SMS_SENDER,
            recipient=phone_number,
            content=message
        )
        api_response = api_instance.send_transac_sms(send_sms)
        print("✅ OTP sent successfully via SMS!")
        return True
    except ApiException as e:
        print(f"❌ Error sending SMS: {e}")
        return False


def verify_otp(sent_otp):
    """Prompt user for OTP input and verify it."""
    entered_otp = input("Enter the OTP you received: ").strip()
    if entered_otp == sent_otp:
        print("✅ OTP verified successfully.")
        return True
    else:
        print("❌ Invalid OTP.")
        return False


def send_and_verify_sms_otp(phone_number):
    """Main function to send and verify OTP via SMS."""
    otp = generate_otp()
    if send_otp_via_sms(phone_number, otp):
        return verify_otp(otp)
    else:
        print("❌ Failed to send OTP via SMS.")
        return False


    
send_email_brevo('mddaniyal752@gmail.com')

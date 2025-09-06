import os
import sqlite3
import hashlib
import random
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import sib_api_v3_sdk

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME", "")

# Configure Brevo (Sendinblue) client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = API_KEY
smtp_client = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Initialize SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    is_verified INTEGER,
    otp_code TEXT,
    otp_expiry INTEGER
)
''')
conn.commit()

# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_user(name, email, password):
    pwd_hash = hash_password(password)
    try:
        c.execute("INSERT INTO users (name, email, password_hash, is_verified) VALUES (?, ?, ?, 0)",
                  (name, email, pwd_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(email):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    return c.fetchone()

def set_user_verified(email):
    c.execute("UPDATE users SET is_verified=1, otp_code=NULL, otp_expiry=NULL WHERE email=?", (email,))
    conn.commit()

def update_password(email, new_password):
    pwd_hash = hash_password(new_password)
    c.execute("UPDATE users SET password_hash=?, otp_code=NULL, otp_expiry=NULL WHERE email=?", (pwd_hash, email))
    conn.commit()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, context):
    otp = generate_otp()
    expiry = int(datetime.now().timestamp()) + 300
    c.execute("UPDATE users SET otp_code=?, otp_expiry=? WHERE email=?", (otp, expiry, email))
    conn.commit()
    # Email content with the OTP
    subject = "Your verification code"
    content = f"<p>Your OTP code is: <strong>{otp}</strong>. It will expire in 5 minutes.</p>"
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        html_content=content,
        sender={"name": SENDER_NAME, "email": SENDER_EMAIL},
        subject=subject
    )
    try:
        smtp_client.send_transac_email(send_smtp_email)
    except Exception as e:
        print("Error sending email:", e)

def verify_user_otp(email, otp_input):
    user = get_user(email)
    if not user:
        return False, "User not found"
    otp_stored, expiry = user[5], user[6]
    if otp_stored is None:
        return False, "No OTP to verify"
    if int(datetime.now().timestamp()) > expiry:
        return False, "OTP expired"
    if otp_input == otp_stored:
        return True, "OTP verified"
    return False, "Invalid OTP"

# Inject custom CSS for styling
st.markdown("""
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f9f9f9;
    }
    .stApp {
        max-width: 500px;
        margin: auto;
        padding: 2rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 2px 2px 12px #aaa;
    }
    input[type="text"], input[type="password"] {
        border-radius: 5px;
        padding: 0.5rem;
        width: 100%;
        box-sizing: border-box;
    }
    button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        margin-top: 1rem;
        cursor: pointer;
        border-radius: 4px;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }
    button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'register_email' not in st.session_state:
    st.session_state.register_email = ""
if 'reset_email' not in st.session_state:
    st.session_state.reset_email = ""
if 'reset_verified' not in st.session_state:
    st.session_state.reset_verified = False

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Login", "Register", "Reset Password"])

# Logged-in view
if st.session_state.logged_in:
    user = get_user(st.session_state.user_email)
    st.title(f"Welcome, {user[1]}!")
    st.write("You have successfully logged in and verified your email.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
else:
    # Login page
    if page == "Login":
        st.title("Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(login_email)
            if user:
                pwd_hash = hash_password(login_password)
                if pwd_hash == user[3]:
                    if user[4] == 1:
                        st.session_state.logged_in = True
                        st.session_state.user_email = login_email
                        st.experimental_rerun()
                    else:
                        st.error("Email not verified. Please register or verify.")
                else:
                    st.error("Incorrect password.")
            else:
                st.error("User not found.")

    # Registration page
    elif page == "Register":
        st.title("Register")
        if not st.session_state.register_email:
            reg_name = st.text_input("Name")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Password", type="password")
            reg_password2 = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if reg_password != reg_password2:
                    st.error("Passwords do not match.")
                elif get_user(reg_email):
                    st.error("Email already registered. Please log in.")
                else:
                    success = create_user(reg_name, reg_email, reg_password)
                    if success:
                        send_otp(reg_email, context="register")
                        st.session_state.register_email = reg_email
                        st.info("An OTP has been sent to your email. Enter it below.")
                    else:
                        st.error("Registration failed.")
        else:
            st.info(f"Enter the OTP sent to {st.session_state.register_email}")
            otp_input = st.text_input("OTP Code")
            if st.button("Verify OTP"):
                ok, msg = verify_user_otp(st.session_state.register_email, otp_input)
                if ok:
                    set_user_verified(st.session_state.register_email)
                    st.success("Email verified! You can now log in.")
                    st.session_state.register_email = ""
                else:
                    st.error(msg)

    # Password reset page
    elif page == "Reset Password":
        st.title("Reset Password")
        if not st.session_state.reset_email:
            reset_email = st.text_input("Registered Email")
            if st.button("Send OTP"):
                user = get_user(reset_email)
                if user:
                    send_otp(reset_email, context="reset")
                    st.session_state.reset_email = reset_email
                    st.info("An OTP has been sent to your email. Enter it below.")
                else:
                    st.error("Email not found.")
        elif not st.session_state.reset_verified:
            st.info(f"Enter the OTP sent to {st.session_state.reset_email}")
            otp_input = st.text_input("OTP Code (for password reset)")
            if st.button("Verify OTP"):
                ok, msg = verify_user_otp(st.session_state.reset_email, otp_input)
                if ok:
                    st.session_state.reset_verified = True
                    st.info("OTP verified. You can set a new password.")
                else:
                    st.error(msg)
        else:
            new_password = st.text_input("New Password", type="password")
            new_password2 = st.text_input("Confirm New Password", type="password")
            if st.button("Reset Password"):
                if new_password != new_password2:
                    st.error("Passwords do not match.")
                else:
                    update_password(st.session_state.reset_email, new_password)
                    st.success("Password reset! You can now log in.")
                    st.session_state.reset_email = ""
                    st.session_state.reset_verified = False

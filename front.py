
import streamlit as st
import json
import os
import hashlib
import re
import emailverification as verify   # OTP + email/SMS sender
import dashbaordn as dashboard
import backend_db as bd
import home 

USER_FILE = "users.json"
bd.create_product_table()


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def valid_name(name):
    return bool(re.match(r"^[A-Za-z]+( [A-Za-z]+)+$", name))

st.set_page_config(page_title="EcoFinds Login", page_icon="🛒", layout="centered")

# session-state initializations
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "registered_email" not in st.session_state:
    st.session_state.registered_email = ""
if "pending_otp" not in st.session_state:
    st.session_state.pending_otp = ""
if "pending_otp_time" not in st.session_state:
    st.session_state.pending_otp_time = 0
if "email_verified" not in st.session_state:
    st.session_state.email_verified = False

# ------------------- Styling block (unchanged) -------------------
st.markdown(""" ... (CSS block unchanged) ... """, unsafe_allow_html=True)

users = load_users()
page = st.session_state.page

if page == "Login":
    # --- Login UI ---
    st.markdown(
        """
        <div class='brand-row'>
            <div class='brand-cart'>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#006D77" width="44" height="44">
                  <path d="M7 4h-2l-1 2h2l3.6 7.59-1.35 2.45C8.89 16.37 9.5 17 10.25 17H19v-2h-8.1c-.14 0-.25-.11-.29-.24L11 13h6.55c.75 0 1.39-.41 1.72-1.03l2.54-5.02A1 1 0 0 0 20.8 5H7z"/>
                  <circle cx="10.5" cy="19.5" r="1.5" fill="#006D77"/>
                  <circle cx="18.5" cy="19.5" r="1.5" fill="#006D77"/>
                </svg>
            </div>
            <div>
                <h1 class='brand-title'>EcoFinds</h1>
                <div class='brand-sub'>Premium Eco Shopping</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("Sign in")

    email = st.text_input("Email address", placeholder="Enter your email here")
    password = st.text_input("Password", type="password", placeholder="Enter your password here")

    if st.button("Login"):
        if email in users and users[email]["password"] == hash_password(password):
            st.success(f"Welcome back, {users[email]['name']}!")
            st.session_state.page = "Main"
            st.rerun()
        else:
            st.error("Invalid email or password")

    st.write("New to EcoFinds?")
    if st.button("Create your EcoFinds account"):
        st.session_state.page = "Register"
        st.session_state.registered_email = ""
        st.session_state.pending_otp = ""
        st.session_state.pending_otp_time = 0
        st.session_state.email_verified = False
        st.rerun()

    if st.button("Forgot Password"):
        st.session_state.page = "Forgot"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Register":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Create account")

    name = st.text_input("Full Name", key="reg_name", placeholder="Enter your full name")
    dob = st.date_input("Date of Birth", key="reg_dob")

    # EMAIL + inline OTP controls
    email = st.text_input("Email address", key="reg_email", placeholder="Enter your email here")

    col1, col2 = st.columns([2, 1], gap="small")
    with col1:
        if st.button("Send OTP", key="send_email_otp"):
            if "@" not in email or "." not in email:
                st.error("Enter a valid email first.")
            else:
                otp = verify.gen_otp()
                st.session_state.pending_otp = otp
                st.session_state.pending_otp_time = verify.now_ts()
                st.session_state.registered_email = email
                st.session_state.email_verified = False

                # Try to send real email
                sent = verify.send_email_otp(email, otp)
                if sent:
                    st.info("OTP sent to your email. Please check your inbox.")
                else:
                    # fallback simulation if email fails
                    st.warning("Email sending failed. (Showing OTP for testing only)")
                    st.success(f"Testing OTP (do not use in production): {otp}")

    with col2:
        otp_input = st.text_input("Enter OTP", key="reg_email_otp", placeholder="6-digit OTP")
        if st.button("Verify Email OTP", key="verify_email_otp"):
            if (st.session_state.pending_otp == "" or st.session_state.registered_email != email):
                st.error("No OTP pending for this email. Click Send OTP first.")
            else:
                if not verify.otp_is_valid(st.session_state.pending_otp_time):
                    st.error("OTP expired. Click Send OTP again.")
                elif otp_input.strip() == st.session_state.pending_otp:
                    st.session_state.email_verified = True
                    st.success("Email verified ✅")
                else:
                    st.error("Incorrect OTP.")

    # Passwords
    password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a strong password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password", placeholder="Re-enter your password")

    # Password rules
    rules = {
        "At least 8 characters": len(password) >= 8,
        "One uppercase letter": bool(re.search(r"[A-Z]", password)),
        "One lowercase letter": bool(re.search(r"[a-z]", password)),
        "One number": bool(re.search(r"[0-9]", password)),
        "One special character (e.g. !@#$%)": bool(re.search(r"[\W_]", password)),
    }

    for rule, passed in rules.items():
        icon = "✅" if passed else "❌"
        color = "green" if passed else "red"
        st.markdown(f"<div style='color:{color}; margin:2px 0;'>{icon} {rule}</div>", unsafe_allow_html=True)

    all_ok = all(rules.values())

    if st.button("Register", disabled=not st.session_state.email_verified):
        if not valid_name(name):
            st.error("Please enter a valid full name (first and last name).")
        elif "@" not in email or "." not in email:
            st.error("Enter a valid email address.")
        elif email in users:
            st.warning("Email already registered.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not all_ok:
            st.error("Password must meet all the requirements shown above.")
        else:
            users[email] = {
                "name": name,
                "dob": str(dob),
                "password": hash_password(password),
                "verified": True
            }
            save_users(users)
            st.success("Registration successful! You are now logged in.")
            st.session_state.temp_login_email = email
            st.session_state.page = "Main"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Forgot":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Reset Password")
    email = st.text_input("Enter your registered email")
    new_password = st.text_input("New Password", type="password")
    confirm_new_password = st.text_input("Confirm New Password", type="password")

    if st.button("Reset"):
        if email not in users:
            st.error("Email not registered")
        elif new_password != confirm_new_password:
            st.error("Passwords do not match")
        else:
            users[email]["password"] = hash_password(new_password)
            save_users(users)
            st.success("Password updated successfully! Please login again.")
            st.session_state.page = "Login"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Main":
    st.title("Welcome to EcoFinds 🛒")
    
    home.homepage()
    if st.button("profile"):
       dashboard.show_dashboard()

    if st.button("Logout"):
        st.session_state.page = "Login"
        st.rerun()


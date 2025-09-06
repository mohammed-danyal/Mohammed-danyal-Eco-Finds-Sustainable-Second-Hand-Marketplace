import streamlit as st
import json
import os
import hashlib
import re


USER_FILE = "users.json"


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
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

st.markdown("""
    <style>
    .stButton>button {
        background-color: #FFD814;
        color: black;
        border-radius: 8px;
        border: 1px solid #FCD200;
        font-weight: bold;
        width: 100%;
        height: 40px;
    }
    .stButton>button:hover {
        background-color: #F7CA00;
        border-color: #F2C200;
    }
    .main-card {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        background: white;
    }
    </style>
""", unsafe_allow_html=True)

users = load_users()

# Session state to handle navigation
if "page" not in st.session_state:
    st.session_state.page = "Login"

page = st.session_state.page

if page == "Login":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Sign in")
    email = st.text_input("Email address")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in users and users[email]["password"] == hash_password(password):
            st.success(f"Welcome back, {users[email]['name']}!")
            st.session_state.page = "Main"
            st.experimental_rerun()
        else:
            st.error("Invalid email or password")

    st.write("New to EcoFinds?")
    if st.button("Create your EcoFinds account"):
        st.session_state.page = "Register"
        st.experimental_rerun()

    if st.button("Forgot Password"):
        st.session_state.page = "Forgot"
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Register":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Create account")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email address")

    # Country codes dropdown (no external package)
    country_codes = {
        "India 🇮🇳 (+91)": "+91",
        "United States 🇺🇸 (+1)": "+1",
        "United Kingdom 🇬🇧 (+44)": "+44",
        "Canada 🇨🇦 (+1)": "+1",
        "Australia 🇦🇺 (+61)": "+61"
    }

    country = st.selectbox("Select your country", list(country_codes.keys()))
    phone = st.text_input("Phone number (without country code)")
    full_phone = f"{country_codes[country]} {phone}"

    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not valid_name(name):
            st.error("Please enter a valid full name (first and last name)")
        elif email in users:
            st.warning("Email already registered")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif "@" not in email or "." not in email:
            st.error("Enter a valid email address")
        elif not phone.isdigit():
            st.error("Enter a valid phone number")
        else:
            users[email] = {
                "name": name,
                "dob": str(dob),
                "phone": full_phone,
                "password": hash_password(password)
            }
            save_users(users)
            st.success("Registration successful! You can now login.")
            st.session_state.page = "Login"
            st.experimental_rerun()
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
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Main":
    st.title("Welcome to EcoFinds 🛒")
    st.write("This is your main content area (like Amazon home page). 🚀")
    if st.button("Logout"):
        st.session_state.page = "Login"
        st.experimental_rerun()
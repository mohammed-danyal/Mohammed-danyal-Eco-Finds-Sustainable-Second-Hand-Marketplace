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

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "registered_email" not in st.session_state:
    st.session_state.registered_email = ""

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
            st.rerun()
        else:
            st.error("Invalid email or password")

    st.write("New to EcoFinds?")
    if st.button("Create your EcoFinds account"):
        st.session_state.page = "Register"
        st.rerun()

    if st.button("Forgot Password"):
        st.session_state.page = "Forgot"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Register":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Create account")

   
    name = st.text_input("Full Name", key="reg_name")
    dob = st.date_input("Date of Birth", key="reg_dob")
    email = st.text_input("Email address", key="reg_email")


    # Passwords
    password = st.text_input("Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")

    # ---------------- Password validation (live) ----------------
    # Make sure you have `import re` at top of file
    rules = {
        "At least 8 characters": len(password) >= 8,
        "One uppercase letter": bool(re.search(r"[A-Z]", password)),
        "One lowercase letter": bool(re.search(r"[a-z]", password)),
        "One number": bool(re.search(r"[0-9]", password)),
        "One special character (e.g. !@#$%)": bool(re.search(r"[\W_]", password)),
    }

    # Show rules (red/green check)
    for rule, passed in rules.items():
        icon = "✅" if passed else "❌"
        color = "green" if passed else "red"
        st.markdown(f"<div style='color:{color}; margin:2px 0;'>{icon} {rule}</div>", unsafe_allow_html=True)

    all_ok = all(rules.values())  # all conditions satisfied

    # Register button (validation enforced)
    if st.button("Register"):
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
                "verified": False   # optional: mark unverified initially
            }
            save_users(users)
            st.success("Registration successful! Please verify your identity.")
            st.session_state.registered_email = email 
            st.session_state.page = "Verify"   # go to the DigiLocker verify page
            st.rerun()
elif st.session_state.page == "Verify":
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("Verify your identity")
    st.write(f"Hi {st.session_state.registered_email}, please verify your account using DigiLocker.")

    if st.button("Verify with DigiLocker"):
        st.markdown(
            """<a href='https://digilocker.gov.in/' target='_blank'>
            <button style='background-color:#FFD814;color:black;
            border-radius:8px;border:1px solid #FCD200;
            font-weight:bold;width:100%;height:40px;'>Go to DigiLocker</button></a>""",
            unsafe_allow_html=True
        )

    if st.button("Skip for now"):
        st.session_state.page = "Login"
        st.rerun()
        

    st.markdown("</div>", unsafe_allow_html=True)
# ---------- end block ----------


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
    st.write("This is your main content area (like Amazon home page). 🚀")
    if st.button("Logout"):
        st.session_state.page = "Login"
        st.rerun()
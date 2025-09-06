import sqlite3
import warnings
import hashlib
import streamlit as st

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Print SQLite version
$print("SQLite version:", sqlite3.version)

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the user table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to hash the password using SHA256
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Function to check if a user exists in the database
def check_user_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to add a new user to the database
def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

# Function to authenticate user during login
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user['password'] == hash_password(password):
        return True
    return False

# Main Streamlit app
def main():
    st.title('Streamlit Login and Signup System')

    create_table()  # Ensure the table exists

    # Tabs for login and signup
    tab = st.selectbox("Select Action", ["Login", "Sign Up"])

    if tab == "Login":
        st.subheader('Login')
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                if authenticate_user(username, password):
                    st.success("Login successful!")
                else:
                    st.error("Invalid username or password.")

    elif tab == "Sign Up":
        st.subheader('Sign Up')
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Sign Up"):
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                if check_user_exists(username):
                    st.error("User already exists. Please login.")
                else:
                    # Hash the password and add the new user to the database
                    hashed_password = hash_password(password)
                    add_user(username, hashed_password)
                    st.success("Sign up successful! You can now login.")

if __name__ == "__main__":
    main()

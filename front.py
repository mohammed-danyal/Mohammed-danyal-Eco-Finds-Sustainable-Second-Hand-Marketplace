import streamlit as st

st.title("My App")
name = st.text_input("Enter your name:")
if st.button("Click me"):
    st.write(f"Hello {name}!")

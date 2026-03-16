import streamlit as st
from database import register_user, validate_user

def register():
    st.subheader("Register New User")
    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Register"):
        if register_user(username, password):
            st.success("Registration successful. Please login.")
            st.rerun()
        else:
            st.error("Username already exists")


def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid credentials")

from db import users_collection, verify_password, hash_password
from functions import check_valid_email
import streamlit as st

import time


def login():
    del_login = st.empty()
    with del_login.form("Login Form"):
        username = st.text_input("Username", placeholder="Your unique username")
        password = st.text_input(
            "Password", placeholder="Your password", type="password"
        )
        login_submit_button = st.form_submit_button(label="Login")
        if login_submit_button:
            user = users_collection.find_one({"username": username})

            if user and verify_password(
                password,
                user["password"],
            ):
                st.session_state.username = username
                st.success("loggen in successfully")
                st.session_state["logged_in"] = True
                st.session_state["role"] = user["Role"]

            else:
                st.error("invalid username of password")


def signup():
    del_signup = st.empty()

    with del_signup.form("signup form"):

        email_sign_up = st.text_input("Email *", placeholder="Please enter your email")
        valid_email_check = check_valid_email(email_sign_up)

        username_sign_up = st.text_input(
            "Username *", placeholder="Enter a unique username"
        )

        password_sign_up = st.text_input(
            "Password *", placeholder="Create a strong password", type="password"
        )

        role_sign_up = st.selectbox(
            "Role *",
            ["User", "Admin", "municipal employee", "police Department employee"],
            index=0,
        )

        st.markdown("###")

        sign_up_submit_button = st.form_submit_button(label="signup")

        if sign_up_submit_button:

            if valid_email_check == False:
                st.error("Please enter a valid Email!")

            elif users_collection.find_one({"username": username_sign_up}):
                st.error("username already exists")

            else:
                users_collection.insert_one(
                    {
                        "username": username_sign_up,
                        "email": email_sign_up,
                        "password": hash_password(password_sign_up),
                        "Role": role_sign_up,
                    }
                )
                st.success("signup succesfully")
                st.session_state["logged_in"] = True
                st.session_state["role"] = role_sign_up
                time.sleep(1)
                st.experimental_rerun()

#import streamlit as st
import pymysql
import pandas as pd
import pickle
from twilio.rest import Client
from datetime import datetime
import streamlit as st


# Load ML models
urgency_model = pickle.load(open("urgency_model.pkl", "rb"))
fraud_model = pickle.load(open("fraud_model.pkl", "rb"))

# DB connection
def get_connection():
    return pymysql.connect(host="localhost", user="root", password="Saraswathi99*", database="organdonation")

# Send SMS (updated Twilio function)
def send_sms(to, msg):
    # Use your Twilio credentials here
    account_sid = 'AC4ef4be45d3ec939881c276efcc4afd4b'  # Replace with your Twilio Account SID
    auth_token = 'fbc58d5bcb8dab21e8a4de7340b56234'    # Replace with your Twilio Auth Token

    # Create a Twilio client
    client = Client(account_sid, auth_token)

    # Send the SMS
    client.messages.create(
        to=to,
        from_="6369033799",  # Replace with your Twilio phone number
        body=msg
    )

# Signup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login/Signup Page
st.title("Organ Donation Matching System")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    with st.form("register"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.radio("Role", ["donor", "recipient", "hospital"])
        contact = st.text_input("Contact Number")
        email = st.text_input("Email")
        address = st.text_area("Address")
        hospital = st.text_input("Hospital Name")
        submit = st.form_submit_button("Register")

        if submit:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password, role, contact, email, address, hospital_name) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (username, password, role, contact, email, address, hospital))
            conn.commit()
            st.success("Registered Successfully")
elif choice == "Login":
    with st.form("login"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s", (username_input,))
            data = cur.fetchone()

            if data:
                st.write("DEBUG - Data from DB:", data)
                st.write("DEBUG - Entered password:", password_input)
                st.write("DEBUG - Password from DB:", data[2])

            if data and data[2].strip() == password_input.strip():
                st.session_state.logged_in = True
                st.session_state.role = data[3]
                st.session_state.username = data[1]
                st.success(f"Welcome {data[1]}")
            else:
                st.error("Invalid credentials")

            cur.close()
            conn.close()

# After Login
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")

    option = st.sidebar.radio("Menu", ["Donate Organ", "Request Organ", "Match Organ"])

    if option == "Donate Organ":
        with st.form("donor_form"):
            name = st.text_input("Name")
            age = st.number_input("Age", 1, 100)
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            organ = st.text_input("Organ Donated")
            health = st.text_area("Health Condition")
            contact = st.text_input("Contact")
            aadhar = st.text_input("Aadhar")
            address = st.text_area("Address")
            submit = st.form_submit_button("Submit")

        if submit:
            # Feature engineering like training
            duplicate_id = 0  # Assuming no duplicate check here, use 0
            invalid_contact = 1 if len(contact) != 10 or not contact.isdigit() else 0
            implausible_age = 1 if age < 18 or age > 100 else 0
            age_condition_mismatch = 1 if age < 25 and health.lower() == "critical" else 0

            # Construct DataFrame for prediction
            df = pd.DataFrame([{
                "duplicate_id": duplicate_id,
                "invalid_contact": invalid_contact,
                "implausible_age": implausible_age,
                "age_condition_mismatch": age_condition_mismatch
            }])

            # Prediction
            if fraud_model.predict(df)[0] == -1:
                st.error("Fake donor detected. Submission blocked.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO donors (name, age, blood_group, organ_donated, health_condition, contact_no, aadhar_no, address, hospital, entry_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (name, age, blood, organ, health, contact, aadhar, address, st.session_state.username, datetime.today()))
                conn.commit()
                st.success("Donor registered.")

    elif option == "Request Organ":
        with st.form("recipient_form"):
            name = st.text_input("Name")
            age = st.number_input("Age", 1, 100)
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            organ = st.text_input("Organ Needed")
            condition = st.selectbox("Condition", ["Critical", "Stable"])
            contact = st.text_input("Contact")
            aadhar = st.text_input("Aadhar")
            address = st.text_area("Address")
            submit = st.form_submit_button("Submit")

            if submit:
                urgency = urgency_model.predict([[age, 1 if condition == "Critical" else 0]])[0]
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO recipients (name, age, blood_group, organ_needed, urgency_level, contact_no, aadhar_no, address, hospital, entry_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (name, age, blood, organ, urgency, contact, aadhar, address, st.session_state.username, datetime.today()))
                conn.commit()
                st.success(f"Recipient registered with urgency level: {urgency}")

    elif option == "Match Organ":
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM donors")
        donors = cur.fetchall()
        cur.execute("SELECT * FROM recipients")
        recipients = cur.fetchall()

        matches = []
        for d in donors:
            for r in recipients:
                print(f"Checking match: Donor: {d[1]} ({d[2]} - {d[3]}), Recipient: {r[1]} ({r[2]} - {r[3]})")

                if d[3] == r[3] and d[4] == r[4] and abs(d[2] - r[2]) <= 10:
                    print(f"Match found: Donor {d[1]} and Recipient {r[1]}")
                    matches.append((d[1], r[1], d[4], r[5]))  # Assuming r[5] is the recipient's urgency level
                    send_sms(r[6], f"Hello {r[1]}, a matching organ has been found from donor {d[1]}. Contact your hospital.")

        if matches:
            st.write("### Matches Found")
            st.table(matches)
        else:
            st.info("No matches found yet.")

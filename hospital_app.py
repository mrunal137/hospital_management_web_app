import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import numpy as np  # Import numpy here
import cv2  # type: ignore # Import OpenCV 
import pandas as pd  # Import pandas for DataFrame display

# Database setup
def create_connection():
    conn = sqlite3.connect('hospital_data.db')
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()[:8]

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        age INTEGER,
                        gender TEXT,
                        department TEXT,
                        hashed_password TEXT,
                        timestamp DATETIME)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        equipment_name TEXT,
                        status TEXT,
                        timestamp DATETIME)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS referrals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hospital_name TEXT,
                        beds_available INTEGER,
                        ventilators_available INTEGER,
                        timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_patient_data(data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO patients (name, age, gender, department, hashed_password, timestamp)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (data['Patient Name'], data['Age'], data['Gender'], data['Department'], data['Hashed Password'], data['Timestamp']))
    conn.commit()
    conn.close()

def save_equipment_data(data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO equipment (equipment_name, status, timestamp)
                      VALUES (?, ?, ?)''',
                   (data['Equipment'], data['Status'], data['Timestamp']))
    conn.commit()
    conn.close()

def save_referral_data(data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO referrals (hospital_name, beds_available, ventilators_available, timestamp)
                      VALUES (?, ?, ?, ?)''',
                   (data['Hospital'], data['Beds Available'], data['Ventilators Available'], data['Timestamp']))
    conn.commit()
    conn.close()

# Create database tables at start
create_tables()

# Streamlit App UI
st.title("🏥 Hospital Management Web App")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Patient Registration", "Equipment Status", "Referral Decision", "View Records", "Predicted Patients", "Alarm System", "Image Processing"])

if page == "Patient Registration":
    st.header("📝 Patient Registration")
    patient_name = st.text_input("Patient Name")
    age = st.number_input("Age", 0, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    department = st.selectbox("Department", ["Emergency", "ICU", "OPD"])
    password = st.text_input("Create Password", type="password")
    if st.button("Save Patient Record"):
        if patient_name and password:
            data = {'Timestamp': datetime.now(), 'Patient Name': patient_name, 'Age': age,
                    'Gender': gender, 'Department': department, 'Hashed Password': hash_password(password)}
            save_patient_data(data)
            st.success("✅ Patient record saved successfully!")
        else:
            st.error("Please fill all fields.")

elif page == "Equipment Status":
    st.header("🔧 Equipment Status Update")
    equipment = st.selectbox("Select Equipment", ["Ventilator", "Defibrillator", "Infusion Pump"])
    status = st.selectbox("Status", ["Working", "Needs Maintenance", "Offline"])
    if st.button("Save Equipment Status"):
        data = {'Timestamp': datetime.now(), 'Equipment': equipment, 'Status': status}
        save_equipment_data(data)
        st.success("✅ Equipment status saved successfully!")

elif page == "Referral Decision":
    st.header("🏥 Smart Referral Decision")
    hospital = st.selectbox("Select Hospital", ["CityCare", "Medipoint", "LifeLine"])
    beds = st.number_input("Beds Available", 0, 20)
    ventilators = st.number_input("Ventilators Available", 0, 10)
    if st.button("Save Referral Data"):
        data = {'Timestamp': datetime.now(), 'Hospital': hospital,
                'Beds Available': beds, 'Ventilators Available': ventilators}
        save_referral_data(data)
        st.success("✅ Referral data saved successfully!")

elif page == "Predicted Patients":
    st.header("🔮 Predicted Patients")
    st.write("Predicted number of patients for the day:")
    st.write("Emergency: 10 patients")
    st.write("ICU: 5 patients")
    st.write("OPD: 8 patients")

elif page == "Alarm System":
    st.header("🚨 Alarm System")
    st.write("Monitoring equipment status...")
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE status != 'Working'")
    alarms = cursor.fetchall()
    if alarms:
        st.warning("⚠️ Attention required: Equipment issues detected!")
        for alarm in alarms:
            st.write(f"Equipment: {alarm[1]}, Status: {alarm[2]}, Timestamp: {alarm[3]}")
    else:
        st.success("✅ All equipment is in working condition.")
    conn.close()

elif page == "View Records":
    st.header("📑 Stored Records")
    
    # Create database connection and fetch patient records
    conn = create_connection()
    cursor = conn.cursor()

    # Display patient records
    st.subheader("Patient Records")
    cursor.execute("SELECT * FROM patients")
    patient_records = cursor.fetchall()

    if patient_records:
        # Display the records as a dataframe for better visualization
        patient_df = pd.DataFrame(patient_records, columns=["ID", "Name", "Age", "Gender", "Department", "Password", "Timestamp"])
        st.dataframe(patient_df)
    else:
        st.warning("⚠️ No patient records available yet.")
    
    # Display equipment records
    st.subheader("Equipment Records")
    cursor.execute("SELECT * FROM equipment")
    equipment_records = cursor.fetchall()

    if equipment_records:
        equipment_df = pd.DataFrame(equipment_records, columns=["ID", "Equipment Name", "Status", "Timestamp"])
        st.dataframe(equipment_df)
    else:
        st.warning("⚠️ No equipment records available yet.")
    
    # Display referral records
    st.subheader("Referral Records")
    cursor.execute("SELECT * FROM referrals")
    referral_records = cursor.fetchall()

    if referral_records:
        referral_df = pd.DataFrame(referral_records, columns=["ID", "Hospital Name", "Beds Available", "Ventilators Available", "Timestamp"])
        st.dataframe(referral_df)
    else:
        st.warning("⚠️ No referral records available yet.")

    conn.close()

elif page == "Image Processing":
    st.header("🖼️ Medical Image Processing")

    uploaded_image = st.file_uploader("Upload Patient Image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        img_cv = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

        # Check if the image has 3 channels (color)
        if len(img_cv.shape) == 3 and img_cv.shape[2] == 3:
            # Image is already in BGR format (3 channels)
            st.image(img_cv, channels="BGR", caption="Original Image")
        else:
            # Convert grayscale to BGR (3 channels)
            img_bgr = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2BGR)
            st.image(img_bgr, channels="BGR", caption="Original Image (Converted)")

        # Grayscale image for processing
        gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY) if len(img_cv.shape) == 3 else img_cv

        st.image(gray_img, caption="Grayscale Image")

        # Edge detection
        edges = cv2.Canny(gray_img, 100, 200)
        st.image(edges, caption="Edge Detection (Canny)")

        st.success("✅ Image processing completed!")

    else:
        st.info("📥 Please upload an image file to proceed.")

        st.sidebar.subheader("Backup Database")
with open('hospital_data.db', 'rb') as f:
    st.sidebar.download_button('Download Backup', f, file_name='hospital_data_backup.db')


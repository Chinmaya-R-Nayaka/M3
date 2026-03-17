
# from bson import ObjectId
# import streamlit as st
# from datetime import datetime
# from db import get_database
# from services import (
#     calculate_age_in_months, calculate_growth_percentile, 
#     check_milestone_delay, check_immunization_delay, check_who_growth,
#     calculate_bmi, generate_recommendation
# )

# # Database Setup
# db = get_database()

# patients_col = db["patients"]
# growth_col = db["growth"]
# immunization_col = db["immunization"]
# milestone_col = db["milestones"]
# alert_col = db["alerts"]

# # UI Layout
# st.set_page_config(page_title="M3 Pediatric System", layout="wide")

# # --- Custom Alert Overrides ---
# def custom_success(msg, *args, **kwargs):
#     msg = str(msg).replace("✅", "").strip()
#     st.markdown(f"""
#         <div style="background-color: #173620; color: #57c776; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
#             <span style="font-size: 1rem;">✅ {msg}</span>
#         </div>
#     """, unsafe_allow_html=True)

# def custom_error(msg, *args, **kwargs):
#     msg = str(msg).replace("🚨", "").replace("⚠", "").strip()
#     st.markdown(f"""
#         <div style="background-color: #3b1515; color: #ff6b6b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
#             <span style="font-size: 1rem;">🚨 {msg}</span>
#         </div>
#     """, unsafe_allow_html=True)

# def custom_warning(msg, *args, **kwargs):
#     msg = str(msg).replace("⚠", "").strip()
#     st.markdown(f"""
#         <div style="background-color: #3b3010; color: #ffca28; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
#             <span style="font-size: 1rem;">⚠ {msg}</span>
#         </div>
#     """, unsafe_allow_html=True)

# st.success = custom_success
# st.error = custom_error
# st.warning = custom_warning
# # -------------------------------------

# st.markdown("""
# <style>
#     /* Red Primary Buttons */
#     div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
#         background-color: #ff4b4b !important;
#         color: white !important;
#         border: none !important;
#     }
#     div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {
#         background-color: #ff1f1f !important;
#         border: none !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.title("🏥 M3 - Pediatric Clinical Data System")
# st.markdown("---")

# menu_options = [
#     "Add Patient",
#     "Add Growth Record",
#     "Add Immunization",
#     "Add Milestone",
#     "View Patients",
#     "View Patient Details",
#     "View Alerts"
# ]

# # initialize session menu
# if "menu" not in st.session_state:
#     st.session_state.menu = "Add Patient"

# menu = st.sidebar.selectbox(
#     "Select Module",
#     menu_options,
#     index=menu_options.index(st.session_state.menu)
# )

# st.session_state.menu = menu


# # ADD PATIENT
# if menu == "Add Patient":

#     st.header("👶 Add New Pediatric Patient")

#     col1, col2 = st.columns(2)

#     with col1:
#         name = st.text_input("Child Name")
#         gender = st.selectbox("Gender", ["Male", "Female"])

#     with col2:
#         dob = st.date_input("Date of Birth")

#     if st.button("Save Patient", type="primary"):

#         if name.strip() == "":
#             st.error("Patient name cannot be empty")
#             st.stop()

#         age_months = calculate_age_in_months(dob)

#         patients_col.insert_one({
#             "name": name.strip(),
#             "dob": dob.strftime("%Y-%m-%d"),
#             "gender": gender,
#             "age_months": age_months,
#             "created_at": datetime.now()
#         })

#         st.success("Patient saved successfully")


# # ADD GROWTH
# elif menu == "Add Growth Record":

#     st.header("📈 Add Growth Measurement")

#     patient_list = list(patients_col.find())
#     if len(patient_list) == 0:
#         st.warning("No patients found")
#         st.stop()

#     patient_dict = {p["name"]: p["_id"] for p in patient_list}

#     selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
#     selected_patient = patient_dict[selected_name]

#     weight = st.number_input("Weight (kg)", min_value=0.0)
#     height = st.number_input("Height (cm)", min_value=0.0)

#     if st.button("Save Growth Record", type="primary"):

#         patient = patients_col.find_one({"_id": selected_patient})
#         age_months = patient["age_months"]
#         percentile = calculate_growth_percentile(weight, height)
#         weight_status, height_status = check_who_growth(age_months, weight, height)
#         bmi, bmi_status = calculate_bmi(weight, height)
#         recommendations = generate_recommendation(weight_status, height_status, bmi_status)

#         growth_col.insert_one({
#             "patient_id": selected_patient,
#             "patient_name": selected_name,
#             "weight": weight,
#             "height": height,
#             "bmi": bmi,
#             "bmi_status": bmi_status,
#             "weight_status": weight_status,
#             "height_status": height_status,
#             "percentile": percentile,
#             "recommendations": recommendations,
#             "recorded_at": datetime.now()
#         })

#         st.success("Growth record added successfully")

#         st.subheader("📊 Growth Analysis")

#         st.write("BMI:", bmi)
#         st.write("BMI Status:", bmi_status)
#         st.write("Weight Status:", weight_status)
#         st.write("Height Status:", height_status)

#         st.subheader("🩺 Doctor Recommendations")

#         for r in recommendations:
#             st.warning(r)


# # ADD IMMUNIZATION
# elif menu == "Add Immunization":

#     st.header("💉 Add Immunization Record")

#     # Fetch patients
#     patient_list = list(patients_col.find())

#     if len(patient_list) == 0:
#         st.warning("No patients found. Please add a patient first.")
#         st.stop()

#     # Create name → id mapping
#     patient_dict = {p["name"]: p["_id"] for p in patient_list}

#     selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
#     selected_patient = patient_dict[selected_name]

#     vaccine_name = st.text_input("Vaccine Name")
#     scheduled_date = st.date_input("Scheduled Date")

#     if st.button("Save Immunization", type="primary"):

#         if vaccine_name.strip() == "":
#             st.error("Please enter vaccine name")
#             st.stop()

#         delayed = check_immunization_delay(scheduled_date)

#         immunization_col.insert_one({
#             "patient_id": selected_patient,
#             "patient_name": selected_name,
#             "vaccine_name": vaccine_name,
#             "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
#             "delayed": delayed,
#             "created_at": datetime.now()
#         })

#         # Generate alert if delayed
#         if delayed:
#             alert_col.insert_one({
#                 "patient_id": selected_patient,
#                 "type": "Immunization Delay",
#                 "status": "Active",
#                 "created_at": datetime.now()
#             })

#         st.success("Immunization record added successfully")


# # ADD MILESTONE
# elif menu == "Add Milestone":

#     st.header("🏆 Add Developmental Milestone")

#     patient_list = list(patients_col.find())

#     if len(patient_list) == 0:
#         st.warning("No patients found. Please add a patient first.")
#         st.stop()

#     # name -> id mapping
#     patient_dict = {p["name"]: str(p["_id"]) for p in patient_list}

#     selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))

#     # geting ObjectId
#     selected_patient = ObjectId(patient_dict[selected_name])

#     milestone_name = st.text_input("Milestone Name")
#     expected_age = st.number_input("Expected Age (Months)", min_value=0)
#     achieved_age = st.number_input("Achieved Age (Months)", min_value=0)

#     if st.button("Save Milestone", type="primary"):

#         delayed = check_milestone_delay(expected_age, achieved_age)

#         milestone_col.insert_one({
#             "patient_id": selected_patient,
#             "patient_name": selected_name,
#             "milestone_name": milestone_name,
#             "expected_age": expected_age,
#             "achieved_age": achieved_age,
#             "delayed": delayed,
#             "created_at": datetime.now()
#         })

#         if delayed:
#             alert_col.insert_one({
#                 "patient_id": selected_patient,
#                 "type": "Milestone Delay",
#                 "status": "Active",
#                 "created_at": datetime.now()
#             })

#         st.success("Milestone saved successfully")


# # VIEW PATIENTS
# elif menu == "View Patients":

#     st.header("📋 Patient Records")

#     records = list(patients_col.find())

#     if len(records) == 0:
#         st.warning("No patients found")

#     else:
#         h1, h2, h3, h4, h5, h6 = st.columns([2,2,2,2,2,1])
#         h1.write("Name")
#         h2.write("DOB")
#         h3.write("Gender")
#         h4.write("Age (Months)")
#         h5.write("Created At")
#         h6.write("Delete")

#         st.markdown("---")

#         for patient in records:
#             c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,2,2,1])

#             # CLICKABLE NAME
#             if c1.button(patient["name"], key=f"name_{patient['_id']}"):
#                 st.session_state.selected_patient = patient["_id"]
#                 st.session_state.menu = "View Patient Details"
#                 st.rerun()

#             c2.write(patient["dob"])
#             c3.write(patient["gender"])
#             c4.write(patient["age_months"])
#             c5.write(patient["created_at"].strftime("%Y-%m-%d"))

#             if c6.button("Delete", key=f"del_{patient['_id']}", type="primary"):
#                 pid = patient["_id"]

#                 patients_col.delete_one({"_id": pid})
#                 growth_col.delete_many({"patient_id": pid})
#                 immunization_col.delete_many({"patient_id": pid})
#                 milestone_col.delete_many({"patient_id": pid})
#                 alert_col.delete_many({"patient_id": pid})

#                 st.success(f"{patient['name']} deleted successfully")
#                 st.rerun()


# # View Patient Details
# elif menu == "View Patient Details":

#     st.header("📝 Patient Complete Record")

#     patient_list = list(patients_col.find())
#     if len(patient_list) == 0:
#         st.warning("No patients found")
#     else:
#         patient_dict = {p["name"]: p["_id"] for p in patient_list}

#         if "selected_patient" in st.session_state:
#             selected_patient = st.session_state["selected_patient"]
#         else:
#             selected_name = st.selectbox("Select Patient", list(patient_dict.keys()))
#             selected_patient = patient_dict[selected_name]

#         st.markdown("---")

#         patient_info = patients_col.find_one({"_id": selected_patient})

#         st.subheader("👤 Patient Profile")

#         patient_info.pop("_id", None)

#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("👶 Name", patient_info["name"])
#         col2.metric("🧑 Gender", patient_info["gender"])
#         col3.metric("📅 Age (Months)", patient_info["age_months"])
#         col4.metric("🎂 DOB", patient_info["dob"])

#         st.markdown("---")

#         # HEALTH ALERT BANNER
#         immunization_delays = list(immunization_col.find({
#             "patient_id": selected_patient,
#             "delayed": True
#         }))

#         milestone_delays = list(milestone_col.find({
#             "patient_id": selected_patient,
#             "delayed": True
#         }))

#         total_alerts = len(immunization_delays) + len(milestone_delays)
#         if total_alerts > 0:
#             st.error(f"⚠ {total_alerts} Health Alerts Detected")
#         else:
#             st.success("✅ No Health Alerts")

#         # GROWTH RECORDS
#         st.subheader("📈 Growth Records")

#         growth_records = list(growth_col.find({"patient_id": selected_patient}))
#         if growth_records:
#             for g in growth_records:
#                 g.pop("_id", None)
#                 g.pop("patient_id", None)
#                 if g.get("weight_status") == "Underweight":
#                     st.warning(f"⚠ Underweight detected on {g['recorded_at']}")

#             st.dataframe(growth_records)

#         else:
#             st.info("No growth records found")

#         st.markdown("---")

#         # IMMUNIZATION RECORDS
#         st.subheader("💉 Immunization Records")

#         immunization_records = list(immunization_col.find({"patient_id": selected_patient}))
#         if immunization_records:
#             for i in immunization_records:
#                 i.pop("_id", None)
#                 i.pop("patient_id", None)

#             st.dataframe(immunization_records)

#         else:
#             st.info("No immunization records found")

#         st.markdown("---")

#         # MILESTONE RECORDS
#         st.subheader("🏆 Milestone Records")

#         milestone_records = list(milestone_col.find({"patient_id": selected_patient}))
#         if milestone_records:
#             for m in milestone_records:
#                 m.pop("_id", None)
#                 m.pop("patient_id", None)

#             st.dataframe(milestone_records)

#         else:
#             st.info("No milestone records found")

#         st.markdown("---")

#         # IMMUNIZATION DELAYS
#         st.subheader("⚠️ Immunization Delays")

#         if immunization_delays:
#             h1, h2, h3, h4 = st.columns([3,3,2,1])
#             h1.write("Vaccine Name")
#             h2.write("Scheduled Date")
#             h3.write("Status")
#             h4.write("Resolve")

#             st.markdown("---")

#             for record in immunization_delays:
#                 c1, c2, c3, c4 = st.columns([3,3,2,1])
#                 c1.write(record["vaccine_name"])
#                 c2.write(record["scheduled_date"])
#                 c3.markdown("🔴 **Active**")

#                 if c4.button("Resolve", key=f"imm_{record['_id']}", type="primary"):
#                     immunization_col.update_one(
#                         {"_id": record["_id"]},
#                         {"$set": {"delayed": False}}
#                     )

#                     st.success("Immunization delay resolved")
#                     st.rerun()

#         else:
#             st.success("No immunization delays")

#         st.markdown("---")

#         # MILESTONE DELAYS
#         st.subheader("⚠️ Milestone Delays")

#         if milestone_delays:
#             h1, h2, h3, h4 = st.columns([3,2,2,2])
#             h1.write("Milestone Name")
#             h2.write("Expected Age")
#             h3.write("Achieved Age")
#             h4.write("Status")

#             st.markdown("---")

#             for record in milestone_delays:
#                 c1, c2, c3, c4 = st.columns([3,2,2,2])
#                 c1.write(record["milestone_name"])
#                 c2.write(f"{record['expected_age']} months")
#                 c3.write(f"{record['achieved_age']} months")
#                 c4.markdown("🔴 **Delayed**")

#         else:
#             st.success("No milestone delays")

#     if st.button("⬅ Back to Patients", type="primary"):
#         st.session_state.menu = "View Patients"
#         st.rerun()


# # VIEW ALERTS PAGE (ONLY ACTIVE ALERTS)
# elif menu == "View Alerts":

#     st.header("🚨 Generated Alerts")
#     display_data = []

#     # IMMUNIZATION DELAYS
#     immunization_delays = list(immunization_col.find({"delayed": True}))

#     for record in immunization_delays:
#         patient = patients_col.find_one({"_id": record["patient_id"]})
#         if patient:
#             patient_name = patient["name"]
#         else:
#             patient_name = "Unknown"

#         display_data.append({
#             "Patient Name": patient_name,
#             "Alert Type": "Immunization Delay",
#             "Detail": record.get("vaccine_name", "Unknown"),
#             "Scheduled Date": record.get("scheduled_date", "Unknown")
#         })

#     # MILESTONE DELAYS
#     # milestone_delays = list(milestone_col.find({"delayed": True}))
#     # for record in milestone_delays:
#     #     patient = patients_col.find_one({"_id": record["patient_id"]})
#     #     if patient:
#     #         patient_name = patient["name"]
#     #     else:
#     #         patient_name = "Unknown"

#     #     display_data.append({
#     #         "Patient Name": patient_name,
#     #         "Alert Type": "Milestone Delay",
#     #         "Detail": record.get("milestone_name", "Unknown"),
#     #         "Scheduled Date": f"{record.get('expected_age','?')} months"
#     #     })


#     # DISPLAY TABLE
#     if display_data:
#         st.dataframe(display_data, use_container_width=True)
#     else:
#         st.success("✅ No Active Alerts")



"""
M3 – Pediatric Clinical Data System  |  Streamlit Frontend
Run with:  streamlit run app.py
All backend communication goes through api_client.py — no direct DB calls here.
"""

import streamlit as st
import requests
import api_client as api

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="M3 Pediatric System", layout="wide")

# --- Custom Alert Overrides ---
def custom_success(msg, *args, **kwargs):
    msg = str(msg).replace("✅", "").strip()
    st.markdown(f"""
        <div style="background-color: #173620; color: #57c776; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">✅ {msg}</span>
        </div>
    """, unsafe_allow_html=True)

def custom_error(msg, *args, **kwargs):
    msg = str(msg).replace("🚨", "").replace("⚠", "").strip()
    st.markdown(f"""
        <div style="background-color: #3b1515; color: #ff6b6b; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">🚨 {msg}</span>
        </div>
    """, unsafe_allow_html=True)

def custom_warning(msg, *args, **kwargs):
    msg = str(msg).replace("⚠", "").strip()
    st.markdown(f"""
        <div style="background-color: #3b3010; color: #ffca28; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size: 1rem;">⚠ {msg}</span>
        </div>
    """, unsafe_allow_html=True)

st.success = custom_success
st.error = custom_error
st.warning = custom_warning
# -------------------------------------

# --- Global CSS ---
st.markdown("""
<style>
    /* Red Primary Buttons */
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #ff1f1f !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 M3 - Pediatric Clinical Data System")
st.markdown("---")


# Navigation

MENU_OPTIONS = [
    "Add Patient",
    "Add Growth Record",
    "Add Immunization",
    "Add Milestone",
    "View Patients",
    "View Patient Details",
    "View Alerts",
]

if "menu" not in st.session_state:
    st.session_state.menu = "Add Patient"

menu = st.sidebar.selectbox(
    "Select Module",
    MENU_OPTIONS,
    index=MENU_OPTIONS.index(st.session_state.menu),
)
st.session_state.menu = menu

# ──────────────────────────────────────────────────────────────────────────────
# Helper: fetch patients and build name → id dict; show warning if empty
# ──────────────────────────────────────────────────────────────────────────────

def _load_patient_dict() -> dict[str, str]:
    """Returns {patient_name: patient_id} or stops the page if none exist."""
    try:
        patients = api.get_all_patients()
    except requests.RequestException as e:
        st.error(f"Could not reach API: {e}")
        st.stop()
        return {}

    if not patients:
        st.warning("No patients found. Please add a patient first.")
        st.stop()

    return {p["name"]: p["id"] for p in patients}

# ──────────────────────────────────────────────────────────────────────────────
# Error wrapper
# ──────────────────────────────────────────────────────────────────────────────

def _api_error(e: requests.HTTPError) -> None:
    """Display a user-friendly error from an HTTPError response."""
    try:
        detail = e.response.json().get("detail", str(e))
    except Exception:
        detail = str(e)
    st.error(f"API error: {detail}")


# ══════════════════════════════════════════════════════════════════════════════
# ADD PATIENT
# ══════════════════════════════════════════════════════════════════════════════

if menu == "Add Patient":
    st.header("👶 Add New Pediatric Patient")

    col1, col2 = st.columns(2)
    with col1:
        name   = st.text_input("Child Name")
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        dob = st.date_input("Date of Birth")

    if st.button("Save Patient", type="primary"):
        if not name.strip():
            st.error("Patient name cannot be empty.")
        else:
            try:
                patient = api.create_patient(name.strip(), dob, gender)
                st.success(
                    f"✅ Patient **{patient['name']}** created "
                    f"(age: {patient['age_months']} months)"
                )
            except requests.HTTPError as e:
                _api_error(e)
            except requests.RequestException as e:
                st.error(f"Could not reach API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ADD GROWTH RECORD
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "Add Growth Record":
    st.header("📈 Add Growth Measurement")

    patient_dict = _load_patient_dict()

    selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
    selected_patient = patient_dict[selected_name]

    weight = st.number_input("Weight (kg)", min_value=0.1, step=0.1, format="%.1f")
    height = st.number_input("Height (cm)", min_value=1.0,  step=0.5, format="%.1f")

    if st.button("Save Growth Record", type="primary"):
        try:
            record = api.create_growth_record(selected_patient, weight, height)

            st.success("Growth record added successfully.")

            st.subheader("📊 Growth Analysis")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Weight (kg)", record["weight"])
            c2.metric("Height (cm)", record["height"])
            c3.metric("BMI",         record["bmi"])
            c4.metric("Percentile",  f"{record['percentile']}th")

            st.markdown(f"**BMI Status:** {record['bmi_status']}")
            st.markdown(f"**Weight Status:** {record['weight_status']}")
            st.markdown(f"**Height Status:** {record['height_status']}")

            st.subheader("🩺 Doctor Recommendations")
            for rec in record["recommendations"]:
                st.warning(rec)

        except requests.HTTPError as e:
            _api_error(e)
        except requests.RequestException as e:
            st.error(f"Could not reach API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ADD IMMUNIZATION
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "Add Immunization":
    st.header("💉 Add Immunization Record")

    patient_dict = _load_patient_dict()

    selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
    selected_patient = patient_dict[selected_name]

    vaccine_name   = st.text_input("Vaccine Name")
    scheduled_date = st.date_input("Scheduled Date")

    if st.button("Save Immunization", type="primary"):
        if not vaccine_name.strip():
            st.error("Please enter the vaccine name.")
        else:
            try:
                record = api.create_immunization_record(
                    selected_patient, vaccine_name.strip(), scheduled_date
                )
                if record["delayed"]:
                    st.warning(
                        f"⚠ **{record['vaccine_name']}** is overdue "
                        f"(scheduled: {record['scheduled_date']}) — alert raised."
                    )
                else:
                    st.success("Immunization record added successfully.")

            except requests.HTTPError as e:
                _api_error(e)
            except requests.RequestException as e:
                st.error(f"Could not reach API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ADD MILESTONE
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "Add Milestone":
    st.header("🏆 Add Developmental Milestone")

    patient_dict = _load_patient_dict()

    selected_name    = st.selectbox("Select Patient", list(patient_dict.keys()))
    selected_patient = patient_dict[selected_name]

    milestone_name = st.text_input("Milestone Name")
    expected_age   = st.number_input("Expected Age (Months)", min_value=0, step=1)
    achieved_age   = st.number_input("Achieved Age (Months)", min_value=0, step=1)

    if st.button("Save Milestone", type="primary"):
        if not milestone_name.strip():
            st.error("Please enter the milestone name.")
        else:
            try:
                record = api.create_milestone_record(
                    selected_patient,
                    milestone_name.strip(),
                    int(expected_age),
                    int(achieved_age),
                )
                if record["delayed"]:
                    lag = record["achieved_age"] - record["expected_age"]
                    st.warning(
                        f"⚠ **{record['milestone_name']}** achieved "
                        f"{lag} month(s) late — alert raised."
                    )
                else:
                    st.success("Milestone saved successfully.")

            except requests.HTTPError as e:
                _api_error(e)
            except requests.RequestException as e:
                st.error(f"Could not reach API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW PATIENTS
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "View Patients":
    st.header("📋 Patient Records")

    try:
        patients = api.get_all_patients()
    except requests.RequestException as e:
        st.error(f"Could not reach API: {e}")
        st.stop()

    if not patients:
        st.warning("No patients found.")
    else:
        h1, h2, h3, h4, h5, h6 = st.columns([2, 2, 2, 2, 2, 1])
        h1.write("**Name**")
        h2.write("**DOB**")
        h3.write("**Gender**")
        h4.write("**Age (Months)**")
        h5.write("**Created At**")
        h6.write("**Delete**")
        st.markdown("---")

        for p in patients:
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 1])

            if c1.button(p["name"], key=f"name_{p['id']}"):
                st.session_state.selected_patient_id = p["id"]
                st.session_state.menu = "View Patient Details"
                st.rerun()

            c2.write(p["dob"])
            c3.write(p["gender"])
            c4.write(p["age_months"])
            c5.write(p["created_at"][:10])

            if c6.button("🗑", key=f"del_{p['id']}", type="primary"):
                try:
                    result = api.delete_patient(p["id"])
                    st.success(result["message"])
                    st.rerun()
                except requests.HTTPError as e:
                    _api_error(e)
                except requests.RequestException as e:
                    st.error(f"Could not reach API: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# VIEW PATIENT DETAILS
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "View Patient Details":
    st.header("📝 Patient Complete Record")

    # Resolve which patient to display
    if "selected_patient_id" in st.session_state:
        selected_patient_id = st.session_state["selected_patient_id"]
    else:
        patient_dict = _load_patient_dict()
        selected_name       = st.selectbox("Select Patient", list(patient_dict.keys()))
        selected_patient_id = patient_dict[selected_name]

    # ── Fetch patient profile ─────────────────────────────────────────────────
    try:
        patient = api.get_patient(selected_patient_id)
    except requests.HTTPError:
        st.error("Patient not found.")
        st.stop()
    except requests.RequestException as e:
        st.error(f"Could not reach API: {e}")
        st.stop()

    st.subheader("👤 Patient Profile")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👶 Name",         patient["name"])
    col2.metric("🧑 Gender",       patient["gender"])
    col3.metric("📅 Age (Months)", patient["age_months"])
    col4.metric("🎂 DOB",          patient["dob"])

    st.markdown("---")

    # ── Fetch all sub-records ─────────────────────────────────────────────────
    try:
        growth_records       = api.get_growth_records(selected_patient_id)
        immunization_records = api.get_immunization_records(selected_patient_id)
        milestone_records    = api.get_milestone_records(selected_patient_id)
    except requests.RequestException as e:
        st.error(f"Could not fetch records: {e}")
        st.stop()

    # ── Health alert banner ───────────────────────────────────────────────────
    imm_delays = [r for r in immunization_records if r["delayed"]]
    ms_delays  = [r for r in milestone_records    if r["delayed"]]
    total      = len(imm_delays) + len(ms_delays)

    if total:
        st.error(f"⚠ {total} Health Alert(s) Detected")
    else:
        st.success("✅ No Health Alerts")

    st.markdown("---")

    # ── Growth records ────────────────────────────────────────────────────────
    st.subheader("📈 Growth Records")
    if growth_records:
        for g in growth_records:
            if g["weight_status"] == "Underweight":
                st.warning(f"⚠ Underweight detected on {g['recorded_at'][:10]}")

        display = [{
            "Recorded At":     r["recorded_at"][:10],
            "Weight (kg)":     r["weight"],
            "Height (cm)":     r["height"],
            "BMI":             r["bmi"],
            "BMI Status":      r["bmi_status"],
            "Weight Status":   r["weight_status"],
            "Height Status":   r["height_status"],
            "Percentile":      r["percentile"],
            "Recommendations": ", ".join(r["recommendations"]),
        } for r in growth_records]
        st.dataframe(display, use_container_width=True)
    else:
        st.info("No growth records found.")

    st.markdown("---")

    # ── Immunization records ──────────────────────────────────────────────────
    st.subheader("💉 Immunization Records")
    if immunization_records:
        display = [{
            "Vaccine Name":   r["vaccine_name"],
            "Scheduled Date": r["scheduled_date"],
            "Delayed":        "Yes" if r["delayed"] else "No",
            "Created At":     r["created_at"][:10],
        } for r in immunization_records]
        st.dataframe(display, use_container_width=True)
    else:
        st.info("No immunization records found.")

    st.markdown("---")

    # ── Milestone records ─────────────────────────────────────────────────────
    st.subheader("🏆 Milestone Records")
    if milestone_records:
        display = [{
            "Milestone":     r["milestone_name"],
            "Expected (mo)": r["expected_age"],
            "Achieved (mo)": r["achieved_age"],
            "Delayed":       "Yes" if r["delayed"] else "No",
            "Created At":    r["created_at"][:10],
        } for r in milestone_records]
        st.dataframe(display, use_container_width=True)
    else:
        st.info("No milestone records found.")

    st.markdown("---")

    # ── Immunization delays with resolve ─────────────────────────────────────
    st.subheader("⚠️ Immunization Delays")
    if imm_delays:
        h1, h2, h3, h4 = st.columns([3, 3, 2, 1])
        h1.write("**Vaccine Name**")
        h2.write("**Scheduled Date**")
        h3.write("**Status**")
        h4.write("**Action**")
        st.markdown("---")

        for r in imm_delays:
            c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
            c1.write(r["vaccine_name"])
            c2.write(r["scheduled_date"])
            c3.markdown("🔴 **Active**")

            if c4.button("Resolve", key=f"imm_{r['id']}", type="primary"):
                try:
                    result = api.resolve_immunization(r["id"])
                    st.success(result["message"])
                    st.rerun()
                except requests.HTTPError as e:
                    _api_error(e)
    else:
        st.success("No immunization delays.")

    st.markdown("---")

    # ── Milestone delays with resolve ─────────────────────────────────────────
    st.subheader("⚠️ Milestone Delays")
    if ms_delays:
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
        h1.write("**Milestone Name**")
        h2.write("**Expected (mo)**")
        h3.write("**Achieved (mo)**")
        h4.write("**Status**")
        h5.write("**Action**")
        st.markdown("---")

        for r in ms_delays:
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            c1.write(r["milestone_name"])
            c2.write(f"{r['expected_age']} mo")
            c3.write(f"{r['achieved_age']} mo")
            c4.markdown("🔴 **Delayed**")

            if c5.button("Resolve", key=f"ms_{r['id']}", type="primary"):
                try:
                    result = api.resolve_milestone(r["id"])
                    st.success(result["message"])
                    st.rerun()
                except requests.HTTPError as e:
                    _api_error(e)
    else:
        st.success("No milestone delays.")

    if st.button("⬅ Back to Patients", type="primary"):
        st.session_state.pop("selected_patient_id", None)
        st.session_state.menu = "View Patients"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# VIEW ALERTS
# ══════════════════════════════════════════════════════════════════════════════

elif menu == "View Alerts":
    st.header("🚨 Generated Alerts")

    try:
        alerts = api.get_all_alerts()
    except requests.RequestException as e:
        st.error(f"Could not reach API: {e}")
        st.stop()

    if alerts:
        display = [{
            "Patient Name":   a["patient_name"],
            "Alert Type":     a["alert_type"],
            "Detail":         a["detail"],
            "Scheduled Date": a["scheduled_date"],
        } for a in alerts]
        st.dataframe(display, use_container_width=True)
    else:
        st.success("✅ No Active Alerts")
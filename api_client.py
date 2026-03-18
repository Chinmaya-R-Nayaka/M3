# """
# API Client for M3 Pediatric System.

# Every function in this module is a thin wrapper around one REST endpoint.
# The Streamlit app imports from here and never calls `requests` directly.
# """

# from datetime import date
# import requests
# import streamlit as st
# import os

# # ──────────────────────────────────────────────────────────────────────────────
# # Base URL – override via Streamlit secrets or fall back to localhost
# # ──────────────────────────────────────────────────────────────────────────────

# BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")


# # ──────────────────────────────────────────────────────────────────────────────
# # Internal helpers
# # ──────────────────────────────────────────────────────────────────────────────

# def _get(path: str) -> dict | list:
#     """GET request; raises on HTTP error."""
#     r = requests.get(f"{BASE_URL}{path}", timeout=10)
#     r.raise_for_status()
#     return r.json()


# def _post(path: str, payload: dict) -> dict:
#     """POST request; raises on HTTP error."""
#     r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
#     r.raise_for_status()
#     return r.json()


# def _patch(path: str) -> dict:
#     """PATCH request (no body); raises on HTTP error."""
#     r = requests.patch(f"{BASE_URL}{path}", timeout=10)
#     r.raise_for_status()
#     return r.json()


# def _delete(path: str) -> dict:
#     """DELETE request; raises on HTTP error."""
#     r = requests.delete(f"{BASE_URL}{path}", timeout=10)
#     r.raise_for_status()
#     return r.json()


# # ══════════════════════════════════════════════════════════════════════════════
# # PATIENT API CALLS
# # ══════════════════════════════════════════════════════════════════════════════

# def get_all_patients() -> list[dict]:
#     """GET /patients → list of patient dicts."""
#     return _get("/patients")


# def get_patient(patient_id: str) -> dict:
#     """GET /patients/{id} → single patient dict."""
#     return _get(f"/patients/{patient_id}")


# def create_patient(name: str, dob: date, gender: str) -> dict:
#     """POST /patients → newly created patient dict."""
#     return _post("/patients", {
#         "name":   name,
#         "dob":    dob.isoformat(),
#         "gender": gender,
#     })


# def delete_patient(patient_id: str) -> dict:
#     """DELETE /patients/{id} → message dict."""
#     return _delete(f"/patients/{patient_id}")


# # ══════════════════════════════════════════════════════════════════════════════
# # GROWTH API CALLS
# # ══════════════════════════════════════════════════════════════════════════════

# def get_growth_records(patient_id: str) -> list[dict]:
#     """GET /growth/{patient_id} → list of growth record dicts."""
#     return _get(f"/growth/{patient_id}")


# def create_growth_record(patient_id: str, weight: float, height: float) -> dict:
#     """POST /growth → newly created growth record dict (with analysis)."""
#     return _post("/growth", {
#         "patient_id": patient_id,
#         "weight":     weight,
#         "height":     height,
#     })


# # ══════════════════════════════════════════════════════════════════════════════
# # IMMUNIZATION API CALLS
# # ══════════════════════════════════════════════════════════════════════════════

# def get_immunization_records(patient_id: str) -> list[dict]:
#     """GET /immunization/{patient_id} → list of immunization dicts."""
#     return _get(f"/immunization/{patient_id}")


# def create_immunization_record(
#     patient_id: str,
#     vaccine_name: str,
#     scheduled_date: date,
# ) -> dict:
#     """POST /immunization → newly created immunization dict."""
#     return _post("/immunization", {
#         "patient_id":     patient_id,
#         "vaccine_name":   vaccine_name,
#         "scheduled_date": scheduled_date.isoformat(),
#     })


# def resolve_immunization(record_id: str) -> dict:
#     """PATCH /immunization/{id}/resolve → message dict."""
#     return _patch(f"/immunization/{record_id}/resolve")


# # ══════════════════════════════════════════════════════════════════════════════
# # MILESTONE API CALLS
# # ══════════════════════════════════════════════════════════════════════════════

# def get_milestone_records(patient_id: str) -> list[dict]:
#     """GET /milestones/{patient_id} → list of milestone dicts."""
#     return _get(f"/milestones/{patient_id}")


# def create_milestone_record(
#     patient_id: str,
#     milestone_name: str,
#     expected_age: int,
#     achieved_age: int,
# ) -> dict:
#     """POST /milestones → newly created milestone dict."""
#     return _post("/milestones", {
#         "patient_id":     patient_id,
#         "milestone_name": milestone_name,
#         "expected_age":   expected_age,
#         "achieved_age":   achieved_age,
#     })


# def resolve_milestone(record_id: str) -> dict:
#     """PATCH /milestones/{id}/resolve → message dict."""
#     return _patch(f"/milestones/{record_id}/resolve")


# # ══════════════════════════════════════════════════════════════════════════════
# # ALERTS API CALL
# # ══════════════════════════════════════════════════════════════════════════════

# def get_all_alerts() -> list[dict]:
#     """GET /alerts → list of alert dicts."""
#     data = _get("/alerts")
#     return data.get("alerts", [])



"""
M3 Pediatric System – FastAPI Backend
Run with:
uvicorn backend:app --host 0.0.0.0 --port 8000
"""

from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from db import get_database
from models import (
    PatientCreate, PatientResponse,
    GrowthCreate, GrowthResponse,
    ImmunizationCreate, ImmunizationResponse,
    MilestoneCreate, MilestoneResponse,
    AlertItem, AlertsResponse,
    MessageResponse,
)

from services import (
    calculate_age_in_months,
    calculate_growth_percentile,
    check_who_growth,
    calculate_bmi,
    generate_recommendation,
    check_immunization_delay,
    check_milestone_delay,
)

# ------------------------------------------------------------------
# APP
# ------------------------------------------------------------------

app = FastAPI(
    title="M3 Pediatric Clinical API",
    version="1.0.0"
)

# Important for Streamlit Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------

db = get_database()

patients_col = db["patients"]
growth_col = db["growth"]
immunization_col = db["immunization"]
milestone_col = db["milestones"]
alert_col = db["alerts"]


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def oid(id_str: str):
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")


# ------------------------------------------------------------------
# PATIENT ENDPOINTS
# ------------------------------------------------------------------

@app.get("/patients", response_model=list[PatientResponse])
def get_patients():
    docs = list(patients_col.find().sort("created_at", -1))

    results = []
    for d in docs:
        results.append({
            "id": str(d["_id"]),
            "name": d["name"],
            "dob": d["dob"],
            "gender": d["gender"],
            "age_months": d["age_months"],
            "created_at": d["created_at"]
        })

    return results


@app.post("/patients", response_model=PatientResponse, status_code=201)
def create_patient(body: PatientCreate):

    age_months = calculate_age_in_months(body.dob)

    doc = {
        "name": body.name,
        "dob": body.dob.strftime("%Y-%m-%d"),
        "gender": body.gender,
        "age_months": age_months,
        "created_at": datetime.now()
    }

    result = patients_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "dob": doc["dob"],
        "gender": doc["gender"],
        "age_months": doc["age_months"],
        "created_at": doc["created_at"]
    }


@app.delete("/patients/{patient_id}", response_model=MessageResponse)
def delete_patient(patient_id: str):

    patient = patients_col.find_one({"_id": oid(patient_id)})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patients_col.delete_one({"_id": oid(patient_id)})
    growth_col.delete_many({"patient_id": oid(patient_id)})
    immunization_col.delete_many({"patient_id": oid(patient_id)})
    milestone_col.delete_many({"patient_id": oid(patient_id)})
    alert_col.delete_many({"patient_id": oid(patient_id)})

    return {"message": "Patient deleted"}


# ------------------------------------------------------------------
# ALERTS
# ------------------------------------------------------------------

@app.get("/alerts", response_model=AlertsResponse)
def get_alerts():

    alerts = []

    for rec in immunization_col.find({"delayed": True}):
        patient = patients_col.find_one({"_id": rec["patient_id"]})

        alerts.append(AlertItem(
            patient_name=patient["name"] if patient else "Unknown",
            alert_type="Immunization Delay",
            detail=rec["vaccine_name"],
            scheduled_date=rec["scheduled_date"]
        ))

    return AlertsResponse(alerts=alerts)


# ------------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


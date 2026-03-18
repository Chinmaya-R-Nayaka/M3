"""
API Client for M3 Pediatric System.

Every function in this module is a thin wrapper around one REST endpoint.
The Streamlit app imports from here and never calls `requests` directly.
"""

from datetime import date
import requests
import streamlit as st
import os

# ──────────────────────────────────────────────────────────────────────────────
# Base URL – override via Streamlit secrets or fall back to localhost
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get(path: str) -> dict | list:
    """GET request; raises on HTTP error."""
    r = requests.get(f"{BASE_URL}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def _post(path: str, payload: dict) -> dict:
    """POST request; raises on HTTP error."""
    r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def _patch(path: str) -> dict:
    """PATCH request (no body); raises on HTTP error."""
    r = requests.patch(f"{BASE_URL}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def _delete(path: str) -> dict:
    """DELETE request; raises on HTTP error."""
    r = requests.delete(f"{BASE_URL}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════════════════════════════════════
# PATIENT API CALLS
# ══════════════════════════════════════════════════════════════════════════════

def get_all_patients() -> list[dict]:
    """GET /patients → list of patient dicts."""
    return _get("/patients")


def get_patient(patient_id: str) -> dict:
    """GET /patients/{id} → single patient dict."""
    return _get(f"/patients/{patient_id}")


def create_patient(name: str, dob: date, gender: str) -> dict:
    """POST /patients → newly created patient dict."""
    return _post("/patients", {
        "name":   name,
        "dob":    dob.isoformat(),
        "gender": gender,
    })


def delete_patient(patient_id: str) -> dict:
    """DELETE /patients/{id} → message dict."""
    return _delete(f"/patients/{patient_id}")


# ══════════════════════════════════════════════════════════════════════════════
# GROWTH API CALLS
# ══════════════════════════════════════════════════════════════════════════════

def get_growth_records(patient_id: str) -> list[dict]:
    """GET /growth/{patient_id} → list of growth record dicts."""
    return _get(f"/growth/{patient_id}")


def create_growth_record(patient_id: str, weight: float, height: float) -> dict:
    """POST /growth → newly created growth record dict (with analysis)."""
    return _post("/growth", {
        "patient_id": patient_id,
        "weight":     weight,
        "height":     height,
    })


# ══════════════════════════════════════════════════════════════════════════════
# IMMUNIZATION API CALLS
# ══════════════════════════════════════════════════════════════════════════════

def get_immunization_records(patient_id: str) -> list[dict]:
    """GET /immunization/{patient_id} → list of immunization dicts."""
    return _get(f"/immunization/{patient_id}")


def create_immunization_record(
    patient_id: str,
    vaccine_name: str,
    scheduled_date: date,
) -> dict:
    """POST /immunization → newly created immunization dict."""
    return _post("/immunization", {
        "patient_id":     patient_id,
        "vaccine_name":   vaccine_name,
        "scheduled_date": scheduled_date.isoformat(),
    })


def resolve_immunization(record_id: str) -> dict:
    """PATCH /immunization/{id}/resolve → message dict."""
    return _patch(f"/immunization/{record_id}/resolve")


# ══════════════════════════════════════════════════════════════════════════════
# MILESTONE API CALLS
# ══════════════════════════════════════════════════════════════════════════════

def get_milestone_records(patient_id: str) -> list[dict]:
    """GET /milestones/{patient_id} → list of milestone dicts."""
    return _get(f"/milestones/{patient_id}")


def create_milestone_record(
    patient_id: str,
    milestone_name: str,
    expected_age: int,
    achieved_age: int,
) -> dict:
    """POST /milestones → newly created milestone dict."""
    return _post("/milestones", {
        "patient_id":     patient_id,
        "milestone_name": milestone_name,
        "expected_age":   expected_age,
        "achieved_age":   achieved_age,
    })


def resolve_milestone(record_id: str) -> dict:
    """PATCH /milestones/{id}/resolve → message dict."""
    return _patch(f"/milestones/{record_id}/resolve")


# ══════════════════════════════════════════════════════════════════════════════
# ALERTS API CALL
# ══════════════════════════════════════════════════════════════════════════════

def get_all_alerts() -> list[dict]:
    """GET /alerts → list of alert dicts."""
    data = _get("/alerts")
    return data.get("alerts", [])
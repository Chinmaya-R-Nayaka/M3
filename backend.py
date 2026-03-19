# """
# M3 Pediatric System – FastAPI Backend
# Run with:  uvicorn main:app --reload --port 8000
# """

# from datetime import datetime
# from bson import ObjectId
# from fastapi import FastAPI, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware

# from db import get_database
# from models import (
#     PatientCreate, PatientResponse,
#     GrowthCreate, GrowthResponse,
#     ImmunizationCreate, ImmunizationResponse,
#     MilestoneCreate, MilestoneResponse,
#     AlertItem, AlertsResponse,
#     MessageResponse,
# )
# from services import (
#     calculate_age_in_months,
#     calculate_growth_percentile,
#     check_who_growth,
#     calculate_bmi,
#     generate_recommendation,
#     check_immunization_delay,
#     check_milestone_delay,
# )

# # ──────────────────────────────────────────────────────────────────────────────
# # App & middleware
# # ──────────────────────────────────────────────────────────────────────────────

# app = FastAPI(
#     title="M3 Pediatric Clinical API",
#     version="1.0.0",
#     description="REST API for the M3 Pediatric Clinical Data System",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # tighten in production
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ──────────────────────────────────────────────────────────────────────────────
# # Collections (resolved once at startup)
# # ──────────────────────────────────────────────────────────────────────────────

# db               = get_database()
# patients_col     = db["patients"]
# growth_col       = db["growth"]
# immunization_col = db["immunization"]
# milestone_col    = db["milestones"]
# alert_col        = db["alerts"]

# # ──────────────────────────────────────────────────────────────────────────────
# # Helpers
# # ──────────────────────────────────────────────────────────────────────────────

# def _oid(id_str: str) -> ObjectId:
#     """Convert a string to ObjectId, raising 400 on invalid format."""
#     try:
#         return ObjectId(id_str)
#     except Exception:
#         raise HTTPException(status_code=400, detail=f"Invalid id: {id_str}")


# def _serialize_patient(doc: dict) -> dict:
#     return {
#         "id":         str(doc["_id"]),
#         "name":       doc["name"],
#         "dob":        doc["dob"],
#         "gender":     doc["gender"],
#         "age_months": doc["age_months"],
#         "created_at": doc["created_at"],
#     }


# def _serialize_growth(doc: dict) -> dict:
#     return {
#         "id":              str(doc["_id"]),
#         "patient_id":      str(doc["patient_id"]),
#         "patient_name":    doc["patient_name"],
#         "weight":          doc["weight"],
#         "height":          doc["height"],
#         "bmi":             doc["bmi"],
#         "bmi_status":      doc["bmi_status"],
#         "weight_status":   doc["weight_status"],
#         "height_status":   doc["height_status"],
#         "percentile":      doc["percentile"],
#         "recommendations": doc["recommendations"],
#         "recorded_at":     doc["recorded_at"],
#     }


# def _serialize_immunization(doc: dict) -> dict:
#     return {
#         "id":             str(doc["_id"]),
#         "patient_id":     str(doc["patient_id"]),
#         "patient_name":   doc["patient_name"],
#         "vaccine_name":   doc["vaccine_name"],
#         "scheduled_date": doc["scheduled_date"],
#         "delayed":        doc["delayed"],
#         "created_at":     doc["created_at"],
#     }


# def _serialize_milestone(doc: dict) -> dict:
#     return {
#         "id":             str(doc["_id"]),
#         "patient_id":     str(doc["patient_id"]),
#         "patient_name":   doc["patient_name"],
#         "milestone_name": doc["milestone_name"],
#         "expected_age":   doc["expected_age"],
#         "achieved_age":   doc["achieved_age"],
#         "delayed":        doc["delayed"],
#         "created_at":     doc["created_at"],
#     }


# # ══════════════════════════════════════════════════════════════════════════════
# # PATIENT ENDPOINTS
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/patients", response_model=list[PatientResponse], tags=["Patients"])
# def list_patients():
#     """Return all patients, newest first."""
#     docs = list(patients_col.find().sort("created_at", -1))
#     return [_serialize_patient(d) for d in docs]


# @app.get("/patients/{patient_id}", response_model=PatientResponse, tags=["Patients"])
# def get_patient(patient_id: str):
#     """Return a single patient by ID."""
#     doc = patients_col.find_one({"_id": _oid(patient_id)})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     return _serialize_patient(doc)


# @app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, tags=["Patients"])
# def create_patient(body: PatientCreate):
#     """Create a new patient record."""
#     if not body.name.strip():
#         raise HTTPException(status_code=400, detail="Patient name cannot be empty")

#     age_months = calculate_age_in_months(body.dob)
#     now = datetime.now()

#     doc = {
#         "name":       body.name.strip(),
#         "dob":        body.dob.strftime("%Y-%m-%d"),
#         "gender":     body.gender,
#         "age_months": age_months,
#         "created_at": now,
#     }
#     result = patients_col.insert_one(doc)
#     doc["_id"] = result.inserted_id
#     return _serialize_patient(doc)


# @app.delete("/patients/{patient_id}", response_model=MessageResponse, tags=["Patients"])
# def delete_patient(patient_id: str):
#     """Delete a patient and all associated records."""
#     oid = _oid(patient_id)
#     patient = patients_col.find_one({"_id": oid})
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     patients_col.delete_one({"_id": oid})
#     growth_col.delete_many({"patient_id": oid})
#     immunization_col.delete_many({"patient_id": oid})
#     milestone_col.delete_many({"patient_id": oid})
#     alert_col.delete_many({"patient_id": oid})

#     return {"message": f"Patient '{patient['name']}' and all related records deleted"}


# # ══════════════════════════════════════════════════════════════════════════════
# # GROWTH ENDPOINTS
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/growth/{patient_id}", response_model=list[GrowthResponse], tags=["Growth"])
# def list_growth(patient_id: str):
#     """Return all growth records for a patient."""
#     oid  = _oid(patient_id)
#     docs = list(growth_col.find({"patient_id": oid}).sort("recorded_at", -1))
#     return [_serialize_growth(d) for d in docs]


# @app.post("/growth", response_model=GrowthResponse, status_code=status.HTTP_201_CREATED, tags=["Growth"])
# def create_growth(body: GrowthCreate):
#     """Add a growth record; runs WHO checks, BMI, and generates recommendations."""
#     patient_oid = _oid(body.patient_id)
#     patient     = patients_col.find_one({"_id": patient_oid})
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     age_months                   = patient["age_months"]
#     percentile                   = calculate_growth_percentile(body.weight, body.height)
#     weight_status, height_status = check_who_growth(age_months, body.weight, body.height)
#     bmi, bmi_status              = calculate_bmi(body.weight, body.height)
#     recommendations              = generate_recommendation(weight_status, height_status, bmi_status)

#     doc = {
#         "patient_id":      patient_oid,
#         "patient_name":    patient["name"],
#         "weight":          body.weight,
#         "height":          body.height,
#         "bmi":             bmi,
#         "bmi_status":      bmi_status,
#         "weight_status":   weight_status,
#         "height_status":   height_status,
#         "percentile":      percentile,
#         "recommendations": recommendations,
#         "recorded_at":     datetime.now(),
#     }
#     result  = growth_col.insert_one(doc)
#     doc["_id"] = result.inserted_id
#     return _serialize_growth(doc)


# # ══════════════════════════════════════════════════════════════════════════════
# # IMMUNIZATION ENDPOINTS
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/immunization/{patient_id}", response_model=list[ImmunizationResponse], tags=["Immunization"])
# def list_immunizations(patient_id: str):
#     """Return all immunization records for a patient."""
#     oid  = _oid(patient_id)
#     docs = list(immunization_col.find({"patient_id": oid}).sort("created_at", -1))
#     return [_serialize_immunization(d) for d in docs]


# @app.post("/immunization", response_model=ImmunizationResponse, status_code=status.HTTP_201_CREATED, tags=["Immunization"])
# def create_immunization(body: ImmunizationCreate):
#     """Add an immunization record; raises an alert if overdue."""
#     if not body.vaccine_name.strip():
#         raise HTTPException(status_code=400, detail="Vaccine name cannot be empty")

#     patient_oid = _oid(body.patient_id)
#     patient     = patients_col.find_one({"_id": patient_oid})
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     delayed = check_immunization_delay(body.scheduled_date)
#     now     = datetime.now()

#     doc = {
#         "patient_id":     patient_oid,
#         "patient_name":   patient["name"],
#         "vaccine_name":   body.vaccine_name.strip(),
#         "scheduled_date": body.scheduled_date.strftime("%Y-%m-%d"),
#         "delayed":        delayed,
#         "created_at":     now,
#     }
#     result = immunization_col.insert_one(doc)
#     doc["_id"] = result.inserted_id

#     if delayed:
#         alert_col.insert_one({
#             "patient_id": patient_oid,
#             "type":       "Immunization Delay",
#             "detail":     body.vaccine_name.strip(),
#             "status":     "Active",
#             "created_at": now,
#         })

#     return _serialize_immunization(doc)


# @app.patch("/immunization/{record_id}/resolve", response_model=MessageResponse, tags=["Immunization"])
# def resolve_immunization(record_id: str):
#     """Mark an immunization delay as resolved."""
#     oid = _oid(record_id)
#     doc = immunization_col.find_one({"_id": oid})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Immunization record not found")

#     immunization_col.update_one({"_id": oid}, {"$set": {"delayed": False}})

#     # Resolve corresponding alert
#     alert_col.update_one(
#         {"patient_id": doc["patient_id"], "type": "Immunization Delay", "status": "Active"},
#         {"$set": {"status": "Resolved"}},
#     )

#     return {"message": "Immunization delay resolved"}


# # ══════════════════════════════════════════════════════════════════════════════
# # MILESTONE ENDPOINTS
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/milestones/{patient_id}", response_model=list[MilestoneResponse], tags=["Milestones"])
# def list_milestones(patient_id: str):
#     """Return all milestone records for a patient."""
#     oid  = _oid(patient_id)
#     docs = list(milestone_col.find({"patient_id": oid}).sort("created_at", -1))
#     return [_serialize_milestone(d) for d in docs]


# @app.post("/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED, tags=["Milestones"])
# def create_milestone(body: MilestoneCreate):
#     """Add a developmental milestone; raises an alert if delayed."""
#     if not body.milestone_name.strip():
#         raise HTTPException(status_code=400, detail="Milestone name cannot be empty")

#     patient_oid = _oid(body.patient_id)
#     patient     = patients_col.find_one({"_id": patient_oid})
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")

#     delayed = check_milestone_delay(body.expected_age, body.achieved_age)
#     now     = datetime.now()

#     doc = {
#         "patient_id":     patient_oid,
#         "patient_name":   patient["name"],
#         "milestone_name": body.milestone_name.strip(),
#         "expected_age":   body.expected_age,
#         "achieved_age":   body.achieved_age,
#         "delayed":        delayed,
#         "created_at":     now,
#     }
#     result = milestone_col.insert_one(doc)
#     doc["_id"] = result.inserted_id

#     if delayed:
#         alert_col.insert_one({
#             "patient_id": patient_oid,
#             "type":       "Milestone Delay",
#             "detail":     body.milestone_name.strip(),
#             "status":     "Active",
#             "created_at": now,
#         })

#     return _serialize_milestone(doc)


# @app.patch("/milestones/{record_id}/resolve", response_model=MessageResponse, tags=["Milestones"])
# def resolve_milestone(record_id: str):
#     """Mark a milestone delay as resolved."""
#     oid = _oid(record_id)
#     doc = milestone_col.find_one({"_id": oid})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Milestone record not found")

#     milestone_col.update_one({"_id": oid}, {"$set": {"delayed": False}})

#     alert_col.update_one(
#         {"patient_id": doc["patient_id"], "type": "Milestone Delay", "status": "Active"},
#         {"$set": {"status": "Resolved"}},
#     )

#     return {"message": "Milestone delay resolved"}


# # ══════════════════════════════════════════════════════════════════════════════
# # ALERTS ENDPOINT
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/alerts", response_model=AlertsResponse, tags=["Alerts"])
# def list_alerts():
#     """
#     Return all active alerts across all patients:
#     immunization delays + milestone delays.
#     """
#     items: list[AlertItem] = []

#     # Immunization delays
#     for rec in immunization_col.find({"delayed": True}):
#         patient = patients_col.find_one({"_id": rec["patient_id"]})
#         items.append(AlertItem(
#             patient_name   = patient["name"] if patient else "Unknown",
#             alert_type     = "Immunization Delay",
#             detail         = rec.get("vaccine_name", "Unknown"),
#             scheduled_date = rec.get("scheduled_date", "Unknown"),
#         ))

#     # Milestone delays
#     for rec in milestone_col.find({"delayed": True}):
#         patient = patients_col.find_one({"_id": rec["patient_id"]})
#         items.append(AlertItem(
#             patient_name   = patient["name"] if patient else "Unknown",
#             alert_type     = "Milestone Delay",
#             detail         = rec.get("milestone_name", "Unknown"),
#             scheduled_date = f"{rec.get('expected_age', '?')} months (expected)",
#         ))

#     return AlertsResponse(alerts=items)


# # ──────────────────────────────────────────────────────────────────────────────




# new one

"""
M3 Pediatric System – FastAPI Backend
Run with:
uvicorn backend:app --host 0.0.0.0 --port 8000
"""

from datetime import datetime
from bson import ObjectId
from fastapi import FastAPI, HTTPException
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

# ─────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="M3 Pediatric Clinical API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────

db = get_database()

patients_col = db["patients"]
growth_col = db["growth"]
immunization_col = db["immunization"]
milestone_col = db["milestones"]
alert_col = db["alerts"]

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def oid(id_str: str):
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

# ─────────────────────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

# ─────────────────────────────────────────────────────────────
# PATIENTS
# ─────────────────────────────────────────────────────────────

@app.get("/patients", response_model=list[PatientResponse])
def get_patients():
    docs = list(patients_col.find().sort("created_at", -1))
    return [{
        "id": str(d["_id"]),
        "name": d["name"],
        "dob": d["dob"],
        "gender": d["gender"],
        "age_months": d["age_months"],
        "created_at": d["created_at"]
    } for d in docs]


@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str):
    d = patients_col.find_one({"_id": oid(patient_id)})
    if not d:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "id": str(d["_id"]),
        "name": d["name"],
        "dob": d["dob"],
        "gender": d["gender"],
        "age_months": d["age_months"],
        "created_at": d["created_at"]
    }


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
    if not patients_col.find_one({"_id": oid(patient_id)}):
        raise HTTPException(status_code=404, detail="Patient not found")

    patients_col.delete_one({"_id": oid(patient_id)})
    growth_col.delete_many({"patient_id": oid(patient_id)})
    immunization_col.delete_many({"patient_id": oid(patient_id)})
    milestone_col.delete_many({"patient_id": oid(patient_id)})

    return {"message": "Patient deleted"}

# ─────────────────────────────────────────────────────────────
# GROWTH
# ─────────────────────────────────────────────────────────────

@app.post("/growth", response_model=GrowthResponse)
def create_growth(body: GrowthCreate):

    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    bmi, bmi_status = calculate_bmi(body.weight, body.height)
    percentile = calculate_growth_percentile(body.weight, body.height)
    weight_status, height_status = check_who_growth(
        patient["age_months"], body.weight, body.height
    )

    recs = generate_recommendation(weight_status, height_status, bmi_status)

    doc = {
        "patient_id": oid(body.patient_id),
        "weight": body.weight,
        "height": body.height,
        "bmi": bmi,
        "bmi_status": bmi_status,
        "weight_status": weight_status,
        "height_status": height_status,
        "percentile": percentile,
        "recommendations": recs,
        "recorded_at": datetime.now()
    }

    result = growth_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "id": str(doc["_id"]),
        "patient_id": body.patient_id,
        "patient_name": patient["name"],
        **doc
    }


@app.get("/growth/{patient_id}")
def get_growth(patient_id: str):
    docs = list(growth_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["patient_id"] = str(d["patient_id"])
    return docs

# ─────────────────────────────────────────────────────────────
# IMMUNIZATION
# ─────────────────────────────────────────────────────────────

@app.post("/immunization", response_model=ImmunizationResponse)
def create_immunization(body: ImmunizationCreate):

    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delayed = check_immunization_delay(body.scheduled_date)

    doc = {
        "patient_id": oid(body.patient_id),
        "vaccine_name": body.vaccine_name,
        "scheduled_date": body.scheduled_date.isoformat(),
        "delayed": delayed,
        "created_at": datetime.now()
    }

    result = immunization_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "id": str(doc["_id"]),
        "patient_id": body.patient_id,
        "patient_name": patient["name"],
        **doc
    }


@app.get("/immunization/{patient_id}")
def get_immunization(patient_id: str):
    docs = list(immunization_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["patient_id"] = str(d["patient_id"])
    return docs

# ─────────────────────────────────────────────────────────────
# MILESTONE
# ─────────────────────────────────────────────────────────────

@app.post("/milestones", response_model=MilestoneResponse)
def create_milestone(body: MilestoneCreate):

    patient = patients_col.find_one({"_id": oid(body.patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    delayed = check_milestone_delay(body.expected_age, body.achieved_age)

    doc = {
        "patient_id": oid(body.patient_id),
        "milestone_name": body.milestone_name,
        "expected_age": body.expected_age,
        "achieved_age": body.achieved_age,
        "delayed": delayed,
        "created_at": datetime.now()
    }

    result = milestone_col.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "id": str(doc["_id"]),
        "patient_id": body.patient_id,
        "patient_name": patient["name"],
        **doc
    }


@app.get("/milestones/{patient_id}")
def get_milestones(patient_id: str):
    docs = list(milestone_col.find({"patient_id": oid(patient_id)}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["patient_id"] = str(d["patient_id"])
    return docs

# ─────────────────────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────────────────────

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



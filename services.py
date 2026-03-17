
# from datetime import datetime

# WHO_STANDARDS = {
#     6: {"weight": 7.9, "height": 67},
#     12: {"weight": 9.6, "height": 76},
#     24: {"weight": 12.2, "height": 87},
#     36: {"weight": 14.3, "height": 96},
#     48: {"weight": 16.3, "height": 103}
# }


# def calculate_age_in_months(dob):
#     days_difference = (datetime.now() - datetime.combine(dob, datetime.min.time())).days
#     return days_difference // 30


# def calculate_growth_percentile(weight, height):
#     if weight < 5:
#         return 10
#     elif weight > 20:
#         return 95
#     else:
#         return 50


# def check_milestone_delay(expected_age, achieved_age):
#     return achieved_age > expected_age


# def check_immunization_delay(scheduled_date):
#     return datetime.now().date() > scheduled_date


# def check_who_growth(age_months, weight, height):

#     closest_age = min(WHO_STANDARDS.keys(), key=lambda x: abs(x-age_months))
#     standard = WHO_STANDARDS[closest_age]

#     weight_status = "Normal"
#     height_status = "Normal"

#     if weight < standard["weight"] * 0.9:
#         weight_status = "Underweight"

#     if height < standard["height"] * 0.9:
#         height_status = "Stunted"

#     return weight_status, height_status


# def calculate_bmi(weight, height_cm):
#     height_m = height_cm / 100
#     bmi = weight / (height_m ** 2)

#     if bmi < 14:
#         status = "Severely Underweight"
#     elif bmi < 16:
#         status = "Underweight"
#     elif bmi < 18:
#         status = "Normal"
#     else:
#         status = "Overweight"

#     return round(bmi, 2), status


# def generate_recommendation(weight_status, height_status, bmi_status):

#     recommendations = []

#     if weight_status == "Underweight":
#         recommendations.append("Increase nutritional intake")

#     if height_status == "Stunted":
#         recommendations.append("Monitor height growth and nutrition")

#     if bmi_status == "Severely Underweight":
#         recommendations.append("Immediate pediatric consultation required")

#     if len(recommendations) == 0:
#         recommendations.append("Growth is normal")

#     return recommendations


# new one 

"""
Business-logic layer — pure functions with no I/O side effects.
"""

from datetime import datetime, date

WHO_STANDARDS: dict[int, dict[str, float]] = {
    6:  {"weight": 7.9,  "height": 67.0},
    12: {"weight": 9.6,  "height": 76.0},
    24: {"weight": 12.2, "height": 87.0},
    36: {"weight": 14.3, "height": 96.0},
    48: {"weight": 16.3, "height": 103.0},
}


def calculate_age_in_months(dob: date) -> int:
    """Returns whole months elapsed since *dob*."""
    delta_days = (datetime.now().date() - dob).days
    return delta_days // 30


def calculate_growth_percentile(weight: float, height: float) -> int:
    """Simplified percentile estimate based on weight."""
    if weight < 5:
        return 10
    if weight > 20:
        return 95
    return 50


def check_milestone_delay(expected_age: int, achieved_age: int) -> bool:
    """True when a milestone was reached later than expected."""
    return achieved_age > expected_age


def check_immunization_delay(scheduled_date: date) -> bool:
    """True when today is past the scheduled vaccination date."""
    return datetime.now().date() > scheduled_date


def check_who_growth(age_months: int, weight: float, height: float) -> tuple[str, str]:
    """
    Compares measurements against the nearest WHO age standard.

    Returns:
        (weight_status, height_status) — each "Normal", "Underweight", or "Stunted".
    """
    closest_age = min(WHO_STANDARDS.keys(), key=lambda x: abs(x - age_months))
    std = WHO_STANDARDS[closest_age]

    weight_status = "Underweight" if weight < std["weight"] * 0.9 else "Normal"
    height_status = "Stunted"     if height < std["height"] * 0.9 else "Normal"
    return weight_status, height_status


def calculate_bmi(weight: float, height_cm: float) -> tuple[float, str]:
    """
    Returns (bmi_value, bmi_status) using pediatric thresholds.
    """
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)

    if bmi < 14:
        status = "Severely Underweight"
    elif bmi < 16:
        status = "Underweight"
    elif bmi < 18:
        status = "Normal"
    else:
        status = "Overweight"

    return round(bmi, 2), status


def generate_recommendation(
    weight_status: str,
    height_status: str,
    bmi_status: str,
) -> list[str]:
    """Produces a list of clinical recommendations from growth statuses."""
    recs: list[str] = []

    if weight_status == "Underweight":
        recs.append("Increase nutritional intake")
    if height_status == "Stunted":
        recs.append("Monitor height growth and nutrition")
    if bmi_status == "Severely Underweight":
        recs.append("Immediate pediatric consultation required")
    if bmi_status == "Overweight":
        recs.append("Review diet and physical activity levels")
    if not recs:
        recs.append("Growth is within normal parameters")

    return recs
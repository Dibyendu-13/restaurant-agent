from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta

app = FastAPI()

# Allow Vapi and other origins to call your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with Vapi domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- In-memory storage ----
reservations: List[dict] = []

# ---- Request model ----
class ReservationRequest(BaseModel):
    name: str
    date: str  # format: YYYY-MM-DD
    time: str  # format: HH:MM AM/PM UTC
    guests: str  # store as string for Vapi

# ---- Helper: UTC to IST conversion ----
def utc_to_ist(utc_time_str: str) -> str:
    try:
        # Parse time assuming "HH:MM AM/PM" format in UTC
        utc_time = datetime.strptime(utc_time_str.strip(), "%I:%M %p")
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        return ist_time.strftime("%I:%M %p")
    except Exception:
        # fallback if format unexpected
        return utc_time_str

# ---- Helper function: check availability ----
def is_time_available(date: str, time: str) -> bool:
    count = sum(
        1 for r in reservations if r["date"] == date and r["time"].lower() == time.lower()
    )
    return count < 2  # max 2 bookings per slot

# ---- API: Check availability ----
@app.get("/availability/{date}/{time}")
def check_availability(date: str, time: str):
    ist_time = utc_to_ist(time)
    available = is_time_available(date, ist_time)
    if not available:
        return {
            "available": False,
            "message": f"Sorry, {ist_time} on {date} is fully booked."
        }
    return {
        "available": True,
        "message": f"{ist_time} on {date} is available."
    }

# ---- API: Create reservation ----
@app.post("/reserve")
def create_reservation(request: ReservationRequest):
    ist_time = utc_to_ist(request.time)
    if not is_time_available(request.date, ist_time):
        return {
            "status": "failed",
            "message": f"{ist_time} on {request.date} is not available. Please choose another time."
        }

    reservation = {
        "name": request.name.strip(),
        "date": request.date.strip(),
        "time": ist_time,  # store as IST
        "guests": request.guests.strip()
    }
    reservations.append(reservation)

    return {
        "status": "confirmed",
        "message": f"Table booked for {reservation['guests']} people at {ist_time} on {reservation['date']} under {reservation['name']}",
        "reservation": reservation
    }

# ---- API: View all reservations ----
@app.get("/reservations")
def get_reservations():
    return {
        "total": len(reservations),
        "data": reservations
    }

# ---- Root ----
@app.get("/")
def root():
    return {"message": "Restaurant Reservation API is running"}
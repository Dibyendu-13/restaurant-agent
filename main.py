from fastapi import FastAPI
from pydantic import BaseModel, validator
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

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
    date: str  # Expecting ISO format: YYYY-MM-DD
    time: str
    guests: int

    @validator("guests", pre=True)
    def parse_guests(cls, v):
        # Convert guests from string to int if needed
        if isinstance(v, str):
            v = v.replace('"', '')  # remove any quotes
        return int(v)

    @validator("date")
    def parse_date(cls, v):
        # Ensure date is valid and in YYYY-MM-DD format
        try:
            dt = datetime.strptime(v, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

# ---- Helper function ----
def is_time_available(date: str, time: str) -> bool:
    """
    Returns True if less than 2 bookings exist for a given date+time slot.
    """
    count = sum(
        1 for r in reservations if r["date"] == date and r["time"].lower() == time.lower()
    )
    return count < 2

# ---- API: Check availability ----
@app.get("/availability/{date}/{time}")
def check_availability(date: str, time: str):
    available = is_time_available(date, time)
    if not available:
        return {
            "available": False,
            "message": f"Sorry, {time} on {date} is fully booked."
        }
    return {
        "available": True,
        "message": f"{time} on {date} is available."
    }

# ---- API: Create reservation ----
@app.post("/reserve")
def create_reservation(request: ReservationRequest):
    if not is_time_available(request.date, request.time):
        return {
            "status": "failed",
            "message": f"{request.time} on {request.date} is not available. Please choose another time."
        }

    reservation = {
        "name": request.name,
        "date": request.date,
        "time": request.time,
        "guests": request.guests
    }
    reservations.append(reservation)

    return {
        "status": "confirmed",
        "message": f"Table booked for {request.guests} people at {request.time} on {request.date} under {request.name}",
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
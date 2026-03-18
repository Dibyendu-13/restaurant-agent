from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory storage
reservations = []

# Request model
class ReservationRequest(BaseModel):
    name: str
    time: str
    guests: int

# ---- Helper function ----
def is_time_available(time: str) -> bool:
    count = sum(1 for r in reservations if r["time"].lower() == time.lower())
    return count < 2  # max 2 bookings per slot

# ---- API: Check availability ----
@app.get("/availability/{time}")
def check_availability(time: str):
    available = is_time_available(time)

    if not available:
        return {
            "available": False,
            "message": f"Sorry, {time} is fully booked."
        }

    return {
        "available": True,
        "message": f"{time} is available."
    }

# ---- API: Create reservation ----
@app.post("/reserve")
def create_reservation(request: ReservationRequest):
    if not is_time_available(request.time):
        return {
            "status": "failed",
            "message": f"{request.time} is not available. Please choose another time."
        }

    reservation = {
        "name": request.name,
        "time": request.time,
        "guests": request.guests
    }

    reservations.append(reservation)

    return {
        "status": "confirmed",
        "message": f"Table booked for {request.guests} people at {request.time} under {request.name}",
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
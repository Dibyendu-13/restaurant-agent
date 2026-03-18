from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# In-memory storage
reservations = []

# Request model
class ReservationRequest(BaseModel):
    name: str
    date: str      # Format: YYYY-MM-DD
    time: str      # Format: HH:MM AM/PM
    guests: int

# ---- Helper function ----
def is_time_available(date: str, time: str) -> bool:
    # Max 2 bookings per date+time slot
    count = sum(1 for r in reservations if r["date"] == date and r["time"].lower() == time.lower())
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
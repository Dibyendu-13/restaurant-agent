from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
import dateparser  # pip install dateparser

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
    date: str  # can be natural language (e.g., "next Tuesday")
    time: str  # format: HH:MM AM/PM UTC
    guests: str  # store as string for Vapi

# ---- Helper: UTC to IST conversion ----
def utc_to_ist(utc_time_str: str) -> str:
    print(f"[UTC to IST] Input UTC time: '{utc_time_str}'")
    try:
        utc_time = datetime.strptime(utc_time_str.strip(), "%I:%M %p")
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        ist_str = ist_time.strftime("%I:%M %p")
        print(f"[UTC to IST] Converted IST time: '{ist_str}'")
        return ist_str
    except Exception as e:
        print(f"[UTC to IST] Failed to parse time: {e}")
        return utc_time_str

# ---- Helper: Parse natural language date ----
def parse_natural_date(date_str: str) -> str:
    print(f"[Date Parsing] Input date string: '{date_str}'")
    parsed_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'})
    if parsed_date:
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        print(f"[Date Parsing] Parsed date: '{formatted_date}'")
        return formatted_date
    print("[Date Parsing] Failed to parse date, returning input as-is")
    return date_str

# ---- Helper: check availability ----
def is_time_available(date: str, time: str) -> bool:
    print(f"[Availability] Checking availability for {date} at {time}")
    count = sum(
        1 for r in reservations if r["date"] == date and r["time"].lower() == time.lower()
    )
    print(f"[Availability] Current bookings for this slot: {count}")
    return count < 2  # max 2 bookings per slot

# ---- API: Check availability ----
@app.get("/availability/{date}/{time}")
def check_availability(date: str, time: str):
    print(f"[API] /availability called with date={date}, time={time}")
    parsed_date = parse_natural_date(date)
    ist_time = utc_to_ist(time)
    available = is_time_available(parsed_date, ist_time)
    if not available:
        print(f"[API] Time not available: {ist_time} on {parsed_date}")
        return {
            "available": False,
            "message": f"Sorry, {ist_time} on {parsed_date} is fully booked."
        }
    print(f"[API] Time available: {ist_time} on {parsed_date}")
    return {
        "available": True,
        "message": f"{ist_time} on {parsed_date} is available."
    }

# ---- API: Create reservation ----
@app.post("/reserve")
def create_reservation(request: ReservationRequest):
    print(f"[API] /reserve called with request: {request}")
    parsed_date = parse_natural_date(request.date)
    ist_time = utc_to_ist(request.time)
    if not is_time_available(parsed_date, ist_time):
        print(f"[API] Cannot book: {ist_time} on {parsed_date} is full")
        return {
            "status": "failed",
            "message": f"{ist_time} on {parsed_date} is not available. Please choose another time."
        }

    reservation = {
        "name": request.name.strip(),
        "date": parsed_date,
        "time": ist_time,  # store as IST
        "guests": request.guests.strip()
    }
    reservations.append(reservation)
    print(f"[API] Reservation added: {reservation}")
    print(f"[API] Total reservations now: {len(reservations)}")

    return {
        "status": "confirmed",
        "message": f"Table booked for {reservation['guests']} people at {ist_time} on {parsed_date} under {reservation['name']}",
        "reservation": reservation
    }

# ---- API: View all reservations ----
@app.get("/reservations")
def get_reservations():
    print("[API] /reservations called")
    return {
        "total": len(reservations),
        "data": reservations
    }

# ---- Root ----
@app.get("/")
def root():
    print("[API] / root endpoint called")
    return {"message": "Restaurant Reservation API is running"}
# 🍽️ AI Voice Restaurant Reservation Agent

## 📌 Overview

This project is a voice-based AI agent that automates restaurant reservations. It interacts with users through natural conversation, collects booking details, checks availability, and confirms reservations in real time.

The system is designed to simulate a real-world business use case where restaurants handle high volumes of booking calls.

---

## 🎯 Problem

Restaurants often:

* Miss calls during peak hours
* Handle repetitive booking queries
* Struggle with manual reservation management

This leads to lost customers and poor experience.

---

## 💡 Solution

An AI-powered voice agent that:

* Handles reservation requests end-to-end
* Collects user details (name, time, guests)
* Checks slot availability
* Confirms or suggests alternatives

---

## 🏗️ Architecture

```
User (Voice)
   ↓
Vapi (Speech-to-Text + LLM + Text-to-Speech)
   ↓
Agent Logic (Intent + Slot Filling)
   ↓
FastAPI Backend (Tools)
   ↓
Reservation Logic (In-memory storage)
   ↓
Response → Voice
```

---

## 🧠 Agent Design

### Context

* Role: Restaurant reservation assistant
* Domain: Customer support / operations

### Workflow

1. Detect user intent (booking request)
2. Collect required information:

   * Number of guests
   * Time
   * Name
3. Check availability
4. Create reservation
5. Confirm booking or suggest alternative

### Key Behavior

* Multi-step conversation handling
* Slot-filling approach
* Error handling (fully booked slots)

---

## 🧰 Backend (FastAPI)

### Endpoints

#### 1. Check Availability

`GET /availability/{time}`

Response:

```
{
  "available": true,
  "message": "7 PM is available."
}
```

#### 2. Create Reservation

`POST /reserve`

Request:

```
{
  "name": "Dibyendu",
  "time": "7 PM",
  "guests": 3
}
```

Response:

```
{
  "status": "confirmed",
  "message": "Table booked for 3 people at 7 PM under Dibyendu"
}
```

---

## ⚙️ Tech Stack

* Voice AI: Vapi
* Backend: FastAPI (Python)
* API Testing: Postman
* Deployment: Render

---

## 🚀 Deployment

### Backend

Hosted on Render:

```
https://your-app.onrender.com
```

### API Docs

```
https://your-app.onrender.com/docs
```

---

## 🔗 Vapi Integration

### Tool: Create Reservation

* Method: POST
* Endpoint: `/reserve`

### Tool: Check Availability

* Method: GET
* Endpoint: `/availability/{time}`

The agent uses these tools to perform real-time actions instead of only generating text responses.

---

## 🎙️ Demo Scenarios

### ✅ Successful Booking

User: "Book a table for 2 at 7 PM"
→ Reservation confirmed

### ❌ Fully Booked Slot

User: "Book a table for 2 at 7 PM" (after limit reached)
→ Agent suggests alternative time

---

## ⭐ Key Features

* Voice-based interaction
* Tool-based execution (real API calls)
* Dynamic availability handling
* Multi-step conversational flow
* Real-world business application

---

## 🔮 Future Improvements

* Database integration (PostgreSQL / SQLite)
* User history & memory
* SMS / WhatsApp confirmations
* Admin dashboard for restaurants
* Multi-language support

---

## 📂 Setup Instructions

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🏁 Conclusion

This project demonstrates how to build a practical AI agent that goes beyond chat by integrating with backend systems to perform real-world tasks. It highlights agent design, tool usage, and conversational workflows in a production-like sc

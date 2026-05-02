# Secure Memory Isolation System Dashboard

This project simulates how an Operating System enforces strict memory isolation between processes to prevent unauthorized access and data leakage. It features a complete FastAPI Python backend for the OS kernel simulation and a modern React + Tailwind + Framer Motion dashboard.

## Folder Structure
- `backend/`: Python FastAPI app containing the OS Simulation Engine (Memory Manager, Process Manager, Access Matrix).
- `frontend/`: React + Vite + Tailwind project containing the cyberpunk dashboard.

## Installation Steps

### Prerequisites
- **Python 3.9+**
- **Node.js 18+**

### 1. Backend Setup
1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install fastapi uvicorn websockets pydantic
   ```

### 2. Frontend Setup
1. Open a terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```

## Run Instructions

### 1. Start the Backend Kernel Simulation
In the `backend` folder (with the virtual environment activated), run:
```bash
uvicorn main:app --reload --port 8000
```
*The simulation engine will start on `ws://localhost:8000/ws`.*

### 2. Start the Frontend Dashboard
In the `frontend` folder, run:
```bash
npm run dev
```
*Open the provided local URL (usually `http://localhost:5173`) in your browser.*

## Features & Simulation Details
- **Memory Visualization:** Watch RAM frames get allocated in real-time.
- **Process Manager:** Spawn and terminate simulated processes.
- **Access Control:** View the Matrix dictating which process can access which memory frame.
- **Threat Simulation:** Test Buffer Overflows and Unauthorized Cross-Process reads, watching the system raise SIGSEGV and terminate offending processes!

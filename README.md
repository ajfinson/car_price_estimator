# 🚗 Car Lifetime TCO Calculator

A full-stack application that provides **honest, LLM-powered estimates** of vehicle Total Cost of Ownership (TCO) with realistic uncertainty ranges and self-auditing.


https://github.com/user-attachments/assets/2a9245ba-4719-4d4f-8c87-b3cb6ce2628e


## Overview

This application calculates vehicle lifetime costs with:
- **Expert LLM Analysis**: Uses GPT-4o-mini as an automotive expert (no fake web browsing)
- **Honest Uncertainty**: Cost ranges (low/mid/high) and confidence levels
- **Self-Auditing**: Two-pass validation ensures data consistency
- **Comprehensive Timeline**: Scheduled maintenance, wear items, failure-driven repairs, and fees
- **Smart Categorization**: Different confidence levels for predictable vs. uncertain costs

**Important**: All results are AI-generated estimates. Actual costs vary based on usage, location, and vehicle condition.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **AI**: OpenAI API (gpt-4o-mini)
- **Deployment**: Docker + Docker Compose

## Project Structure

```
car_price_estimator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── routes.py        # API endpoints
│   │   ├── models.py        # Pydantic models
│   │   └── service.py       # TCO estimation logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── App.css          # Styles
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types
│   │   └── main.tsx         # Entry point
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

**Option 1: Using Docker (Recommended)**
- Docker and Docker Compose installed
- OpenAI API key

**Option 2: Local Development**
- Python 3.9+ installed
- Node.js 18+ and npm installed
- OpenAI API key

### Setup

#### Option 1: Docker Setup

1. **Configure environment variables**

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-actual-key-here
```

2. **Start the application**

```bash
docker-compose up --build
```

This will:
- Build both backend and frontend containers
- Start the backend API on http://localhost:8000
- Start the frontend on http://localhost:5173

#### Option 2: Local Development Setup

1. **Install root dependencies (for concurrently)**

```bash
npm install
```

2. **Install backend and frontend dependencies**

```bash
npm run install:all
```

Or install them separately:
```bash
# Backend
npm run install:backend

# Frontend
npm run install:frontend
```

3. **Configure environment variables**

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
```

4. **Start both servers**

```bash
npm run dev
```

Or start them manually in separate terminals:

Terminal 1 (Backend):
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

5. **Open your browser**

Navigate to http://localhost:5173

## Available Scripts

- `npm run install:all` - Install all dependencies (backend + frontend)
- `npm run install:backend` - Install only backend dependencies
- `npm run install:frontend` - Install only frontend dependencies
- `npm run dev` - Run both backend and frontend concurrently
- `npm start` - Alias for `npm run dev`

## API Usage

### Endpoint

**POST** `/api/tco/estimate`

### Request Example

```bash
curl -X POST http://localhost:8000/api/tco/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Honda",
    "model": "Civic",
    "year": 2016
  }'
```

### Response Example

```json
{
  "vehicle": {
    "make": "Honda",
    "model": "Civic",
    "year": 2016
  },
  "lifetime": {
    "totalCost": 45000,
    "costPerMonth": 375,
    "months": 120,
    "endReason": "maxYears"
  },
  "breakdown": {
    "depreciation": 8000,
    "fuel": 18000,
    "maintenance": 12000,
    "fees": 7000
  },
  "assumptionsUsed": {
    "kmPerYear": 15000,
    "fuelPricePerLiter": 7.0,
    "maxYears": 20,
    "maxKm": 250000
  },
  "sourcesUsed": [
    {
      "title": "2016 Honda Civic Fuel Economy",
      "url": "https://www.fueleconomy.gov/",
      "snippet": "Average fuel consumption varies between 7-10 L/100km..."
    }
  ],
  "confidence": "medium",
  "notes": [
    "Estimate based on typical usage patterns",
    "Actual costs may vary by region and driving habits"
  ]
}
```

## Configuration

Default assumptions (can be modified in `.env`):

- `DEFAULT_KM_PER_YEAR=15000` - Average kilometers driven per year
- `DEFAULT_FUEL_PRICE_PER_LITER=7.0` - Fuel price in dollars per liter
- `MAX_YEARS=20` - Maximum vehicle age for calculation
- `MAX_KM=250000` - Maximum kilometers for calculation

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

✅ Simple 3-field input (make, model, year)  
✅ AI-powered cost estimation with OpenAI  
✅ Automatic lifetime calculation (20 years OR 250k km)  
✅ Detailed cost breakdown (depreciation, fuel, maintenance, fees)  
✅ Source citations from web research  
✅ Confidence levels and explanatory notes  
✅ Clean, responsive UI  
✅ Docker containerization for easy deployment  

## Limitations

- No authentication or user accounts
- No data persistence (no database)
- Simplified web search (placeholder in demo)
- AI estimates may not reflect real-world costs accurately
- Costs are in USD only
- Single currency and locale

## License

This is a demo project for educational purposes.

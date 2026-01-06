# 🚗 Car Lifetime TCO Calculator

A simple demo application that estimates the Total Cost of Ownership (TCO) for a vehicle over its lifetime using AI-powered analysis.

## Overview

This monorepo contains a full-stack application that calculates vehicle lifetime costs based on:
- **Vehicle Information**: Make, model, and year (user input only)
- **Lifetime Rules**: Ends at minimum of 20 years total age OR 250,000 km
- **AI Analysis**: Uses OpenAI to generate cost estimates with reasoning
- **Web Research**: Includes sources from web searches for transparency

**Important**: All results are AI-generated estimates based on publicly available information. Actual costs may vary significantly based on individual usage patterns, location, vehicle condition, and market conditions.

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

- Docker and Docker Compose installed
- OpenAI API key

### Setup

1. **Clone or create the project directory**

2. **Configure environment variables**

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-actual-key-here
```

3. **Start the application**

```bash
docker-compose up --build
```

This will:
- Build both backend and frontend containers
- Start the backend API on http://localhost:8000
- Start the frontend on http://localhost:5173

4. **Open your browser**

Navigate to http://localhost:5173

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

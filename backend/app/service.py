import os
import json
from datetime import date
from typing import List
from openai import OpenAI
from .models import VehicleInput, TcoResult, Source, VehicleInfo, Lifetime, Breakdown, Assumptions


class TcoService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.km_per_year = int(os.getenv("DEFAULT_KM_PER_YEAR", "15000"))
        self.fuel_price = float(os.getenv("DEFAULT_FUEL_PRICE_PER_LITER", "7.0"))
        self.max_years = int(os.getenv("MAX_YEARS", "20"))
        self.max_km = int(os.getenv("MAX_KM", "250000"))

    def get_web_search_snippets(self, vehicle: VehicleInput) -> List[Source]:
        """
        Placeholder web search function.
        In production, use a real search API (Google Custom Search, Bing, SerpAPI, etc.)
        """
        return [
            Source(
                title=f"{vehicle.year} {vehicle.make} {vehicle.model} Fuel Economy",
                url="https://www.fueleconomy.gov/",
                snippet=f"Average fuel consumption for {vehicle.year} {vehicle.make} {vehicle.model} varies between 7-10 L/100km depending on engine and driving conditions."
            ),
            Source(
                title=f"{vehicle.make} {vehicle.model} Maintenance Costs",
                url="https://www.edmunds.com/",
                snippet=f"Annual maintenance costs for {vehicle.make} {vehicle.model} typically range from $500-$1200, with major services required every 30,000-60,000 km."
            ),
            Source(
                title=f"{vehicle.year} {vehicle.make} {vehicle.model} Depreciation",
                url="https://www.kbb.com/",
                snippet=f"Vehicles like the {vehicle.year} {vehicle.make} {vehicle.model} typically depreciate 15-20% per year for the first 5 years, then 5-10% annually thereafter."
            )
        ]

    async def estimate_tco(self, vehicle: VehicleInput) -> TcoResult:
        # Get search snippets
        sources = self.get_web_search_snippets(vehicle)
        
        # Calculate vehicle age and determine lifetime (use current year dynamically)
        current_year = date.today().year
        vehicle_age = current_year - vehicle.year
        years_remaining = max(0, self.max_years - vehicle_age)
        months = years_remaining * 12
        total_km = years_remaining * self.km_per_year
        
        # Determine end reason
        end_reason = "maxYears" if total_km >= self.max_km else "maxKm"
        if total_km > self.max_km:
            # Adjust months based on km limit
            months = int((self.max_km / self.km_per_year) * 12)
            years_remaining = months / 12
        
        # Build OpenAI prompt
        sources_text = "\n".join([
            f"- {s.title}: {s.snippet} (Source: {s.url})"
            for s in sources
        ])
        
        prompt = f"""You are a car cost estimation expert. Calculate the total cost of ownership (TCO) for the following vehicle.

Vehicle Information:
- Make: {vehicle.make}
- Model: {vehicle.model}
- Year: {vehicle.year}
- Current Year: {current_year}
- Vehicle Age: {vehicle_age} years

Lifetime Calculation Rules:
- The lifetime ends at whichever comes first: {self.max_years} years total age OR {self.max_km} km total
- Years remaining until max age: {years_remaining:.1f} years
- Estimated km over remaining lifetime: {years_remaining * self.km_per_year:.0f} km
- Duration to estimate: {months} months

Server Assumptions (MUST USE THESE):
- Average km driven per year: {self.km_per_year} km
- Fuel price per liter: ₪{self.fuel_price}
- Maximum vehicle age: {self.max_years} years
- Maximum km: {self.max_km} km

Research Sources:
{sources_text}

Calculate the total cost of ownership including:
1. Depreciation (current value - estimated value at end of lifetime)
2. Fuel costs (based on typical fuel consumption for this vehicle and the assumptions above)
3. Maintenance and repairs (routine and expected repairs over the lifetime)
4. Fees (registration, taxes - estimated averages)

YOU MUST RESPOND WITH VALID JSON ONLY. NO MARKDOWN. NO EXPLANATIONS OUTSIDE THE JSON.
Use this exact structure:

{{
  "totalCost": <number>,
  "costPerMonth": <number>,
  "breakdown": {{
    "depreciation": <number>,
    "fuel": <number>,
    "maintenance": <number>,
    "fees": <number>
  }},
  "confidence": "low" | "medium" | "high",
  "notes": [<array of 2-4 brief explanation strings>]
}}

All costs in NIS. Make reasonable estimates based on the vehicle info and research sources.
Ensure totalCost equals the sum of all breakdown items.
Calculate costPerMonth as totalCost / {months}.
"""

        # Call OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise cost estimation assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            data = json.loads(ai_response)
            
            # Clamp negative values to 0
            total_cost = max(0, data.get("totalCost", 0))
            cost_per_month = max(0, data.get("costPerMonth", 0))
            breakdown_data = data.get("breakdown", {})
            breakdown = Breakdown(
                depreciation=max(0, breakdown_data.get("depreciation", 0)),
                fuel=max(0, breakdown_data.get("fuel", 0)),
                maintenance=max(0, breakdown_data.get("maintenance", 0)),
                fees=max(0, breakdown_data.get("fees", 0))
            )
            
            # Build result
            result = TcoResult(
                vehicle=VehicleInfo(
                    make=vehicle.make,
                    model=vehicle.model,
                    year=vehicle.year
                ),
                lifetime=Lifetime(
                    totalCost=total_cost,
                    costPerMonth=cost_per_month,
                    months=months,
                    endReason=end_reason
                ),
                breakdown=breakdown,
                assumptionsUsed=Assumptions(
                    kmPerYear=self.km_per_year,
                    fuelPricePerLiter=self.fuel_price,
                    maxYears=self.max_years,
                    maxKm=self.max_km
                ),
                sourcesUsed=sources,
                confidence=data.get("confidence", "medium"),
                notes=data.get("notes", ["Estimate based on typical usage patterns"])
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to generate TCO estimate: {str(e)}")

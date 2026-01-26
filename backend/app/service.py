import os
import json
import logging
from datetime import date
from typing import Any, Dict
from openai import OpenAI
from .models import VehicleInput, TcoResult

logger = logging.getLogger(__name__)


class TcoService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. Service will fail at runtime.")
        self.openai_client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.km_per_year = int(os.getenv("DEFAULT_KM_PER_YEAR", "15000"))
        self.fuel_price = float(os.getenv("DEFAULT_FUEL_PRICE_PER_LITER", "7.0"))
        self.max_years = int(os.getenv("MAX_YEARS", "20"))
        self.max_km = int(os.getenv("MAX_KM", "250000"))
        self.audit_pass_enabled = os.getenv("LLM_AUDIT_PASS", "true").lower() == "true"

    def clamp_nonnegative_numbers(self, obj: Any) -> Any:
        """Recursively clamp all numeric values to be non-negative."""
        if isinstance(obj, dict):
            return {k: self.clamp_nonnegative_numbers(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.clamp_nonnegative_numbers(item) for item in obj]
        elif isinstance(obj, (int, float)):
            return max(0, obj)
        return obj

    def is_timeline_sorted(self, timeline: list) -> bool:
        """Check if timeline is sorted by km (if present) or ageYears."""
        for i in range(len(timeline) - 1):
            curr_trigger = timeline[i].get("trigger", {})
            next_trigger = timeline[i + 1].get("trigger", {})
            
            curr_km = curr_trigger.get("km")
            next_km = next_trigger.get("km")
            
            if curr_km is not None and next_km is not None:
                if curr_km > next_km:
                    return False
            else:
                curr_age = curr_trigger.get("ageYears")
                next_age = next_trigger.get("ageYears")
                if curr_age is not None and next_age is not None:
                    if curr_age > next_age:
                        return False
        return True

    async def estimate_tco(self, vehicle: VehicleInput) -> TcoResult:
        # Calculate vehicle age and determine lifetime
        current_year = date.today().year
        vehicle_age = current_year - vehicle.year
        years_remaining = max(0, self.max_years - vehicle_age)
        months = years_remaining * 12
        total_km_remaining = years_remaining * self.km_per_year
        current_km = vehicle_age * self.km_per_year
        
        # Determine end reason
        end_km = current_km + total_km_remaining
        if end_km > self.max_km:
            # Adjust based on km limit
            km_remaining = self.max_km - current_km
            years_remaining = km_remaining / self.km_per_year
            months = int(years_remaining * 12)
            end_km = self.max_km
            end_reason = "maxKm"
        else:
            end_reason = "maxYears"
        
        # Build system prompt
        system_prompt = """You are an expert automotive cost analyst and mechanic with decades of experience.

Your role is to provide honest, realistic estimates of vehicle ownership costs over a specified lifetime.

CRITICAL RULES:
- You do NOT browse the web. You do NOT have access to external sources.
- Use your expert knowledge of automotive maintenance, repair patterns, and depreciation.
- Be honest about uncertainty: use cost ranges and confidence levels.
- Return ONLY valid JSON matching the exact schema provided. NO markdown, NO explanations outside JSON.
- All costs in Israeli Shekels (NIS).
- Never return negative costs."""

        # Build user prompt
        user_prompt = f"""Calculate the total cost of ownership for this vehicle:

Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}
Current year: {current_year}
Vehicle age: {vehicle_age} years
Current estimated km: {current_km:,} km

Lifetime parameters:
- Duration: {months} months ({years_remaining:.1f} years remaining)
- End km: {end_km:,} km
- End reason: {end_reason}
- Annual km: {self.km_per_year} km
- Fuel price: ₪{self.fuel_price}/liter

Max constraints:
- Max age: {self.max_years} years
- Max km: {self.max_km:,} km

Return JSON with this EXACT schema:

{{
  "lifetime": {{
    "months": {months},
    "endReason": "{end_reason}",
    "totalCost": <number>,
    "costPerMonth": <number>
  }},
  "breakdown": {{
    "depreciation": <number>,
    "fuel": <number>,
    "maintenance": <number>,
    "fees": <number>
  }},
  "timeline": [
    {{
      "item": "<name>",
      "category": "scheduled" | "wear" | "failure-driven" | "fees",
      "trigger": {{"ageYears": <number|null>, "km": <number|null>}},
      "window": {{"kmMin": <number|null>, "kmMax": <number|null>, "ageMin": <number|null>, "ageMax": <number|null>}},
      "description": "<details>",
      "cost": {{"low": <number>, "mid": <number>, "high": <number>}},
      "confidence": "low" | "medium" | "high",
      "notes": ["<note>"]
    }}
  ],
  "audit": {{
    "timelineSorted": true,
    "totalsConsistent": true,
    "maintenanceMatchesTimelineMid": true,
    "flags": []
  }},
  "overallConfidence": "low" | "medium" | "high"
}}

REQUIREMENTS:
1. Timeline: 10-25 items sorted by km/age. Include:
   - Scheduled maintenance (oil, filters, fluids)
   - Wear items (brakes, tires, battery, suspension)
   - Failure-driven items (alternator, starter, water pump with symptoms)
   - Annual fees (registration, inspection)
   - You may bundle recurring items (e.g., "Oil changes over lifetime") with total mid cost

2. Categories:
   - scheduled: predictable service intervals, high confidence
   - wear: depends on usage, moderate confidence
   - failure-driven: age/mileage-related failures, wider windows, symptoms in notes
   - fees: annual costs

3. Depreciation: Realistic for {vehicle_age}-year-old vehicle (5-10%/year for used, 2-5% if 10+ years old)

4. Fuel: Based on typical consumption for this make/model × km × fuel price

5. MATH CONSTRAINTS (CRITICAL):
   - breakdown.maintenance = SUM of timeline cost.mid for categories scheduled/wear/failure-driven (exclude fees)
   - breakdown.fees = SUM of timeline cost.mid for category fees
   - lifetime.totalCost = depreciation + fuel + maintenance + fees
   - lifetime.costPerMonth = totalCost / {months}

6. Audit fields must be set correctly based on your calculations

7. No negative values. Clamp to 0 if needed."""

        try:
            # Check if client is initialized
            if not self.openai_client:
                raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            
            # Call 1: Generate initial estimate
            logger.info(f"Generating TCO estimate for {vehicle.year} {vehicle.make} {vehicle.model}")
            response1 = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            # Log token usage
            if response1.usage:
                logger.info(f"Call 1 tokens: {response1.usage.total_tokens} "
                           f"(prompt: {response1.usage.prompt_tokens}, "
                           f"completion: {response1.usage.completion_tokens})")
            
            ai_response = response1.choices[0].message.content
            data = json.loads(ai_response)
            
            # Call 2: Auditor pass (if enabled)
            if self.audit_pass_enabled:
                audit_prompt = f"""You are an auditor for TCO estimates. Review and fix this JSON:

{json.dumps(data, indent=2)}

Your job:
1. Verify timeline is sorted by km (if present) else ageYears - fix if not
2. Verify totals consistency:
   - breakdown.maintenance must equal SUM of timeline cost.mid for scheduled/wear/failure-driven
   - breakdown.fees must equal SUM of timeline cost.mid for fees category
   - lifetime.totalCost must equal depreciation + fuel + maintenance + fees
   - lifetime.costPerMonth must equal totalCost / lifetime.months
3. Fix any negative values (clamp to 0)
4. Update audit block with correct boolean flags and list any issues in flags array
5. Ensure all trigger.km and window values don't exceed {self.max_km} km
6. Ensure all trigger.ageYears values don't exceed {self.max_years} years

Return corrected JSON with same schema. NO explanations, ONLY JSON."""

                logger.info("Running auditor pass")
                response2 = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise JSON auditor. Return only valid JSON."},
                        {"role": "user", "content": audit_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                if response2.usage:
                    logger.info(f"Call 2 tokens: {response2.usage.total_tokens}")
                
                data = json.loads(response2.choices[0].message.content)
            
            # Clamp negative values
            data = self.clamp_nonnegative_numbers(data)
            
            # Validate with Pydantic
            result = TcoResult(**data)
            
            logger.info(f"Successfully generated TCO estimate. Total cost: ₪{result.lifetime.totalCost:,.0f}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"TCO estimation error: {e}")
            raise Exception(f"Failed to generate TCO estimate: {str(e)}")

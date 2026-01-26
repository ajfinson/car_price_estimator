from fastapi import APIRouter, HTTPException, status
from openai import OpenAIError, RateLimitError
from .models import VehicleInput, TcoResult
from .service import TcoService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
tco_service = TcoService()


@router.post("/api/tco/estimate", response_model=TcoResult)
async def estimate_tco(vehicle: VehicleInput):
    """
    Estimate the lifetime total cost of ownership for a vehicle.
    
    Returns a detailed breakdown with timeline of maintenance events,
    cost ranges, and confidence levels.
    """
    try:
        result = await tco_service.estimate_tco(vehicle)
        return result
    except RateLimitError as e:
        logger.error(f"OpenAI rate limit error: {e}")
        # Check if it's quota exhaustion
        if "insufficient_quota" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="OpenAI API quota exhausted. Please check your billing."
            )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Upstream AI service error. Please try again."
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid response from AI service: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )

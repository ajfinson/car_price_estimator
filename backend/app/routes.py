from fastapi import APIRouter, HTTPException
from .models import VehicleInput, TcoResult
from .service import TcoService

router = APIRouter()
tco_service = TcoService()


@router.post("/api/tco/estimate", response_model=TcoResult)
async def estimate_tco(vehicle: VehicleInput):
    """
    Estimate the lifetime total cost of ownership for a vehicle.
    """
    try:
        result = await tco_service.estimate_tco(vehicle)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

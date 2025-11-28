from fastapi import APIRouter

from app.modules.absence.api.routes import router as absence_router
from app.modules.compensation.api.endpoints import router as compensation_router
from app.modules.contract.api.endpoints import router as contract_router
from app.modules.employee.api.endpoints import router as employee_router

api_router = APIRouter()
api_router.include_router(employee_router, prefix="/employees", tags=["employees"])
api_router.include_router(contract_router, prefix="/contracts", tags=["contracts"])
api_router.include_router(compensation_router, prefix="/compensation", tags=["compensation"])
api_router.include_router(absence_router, prefix="/absence", tags=["absence"])

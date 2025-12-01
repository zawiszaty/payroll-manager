from fastapi import APIRouter

from app.modules.absence.presentation.routes import router as absence_router
from app.modules.compensation.presentation.endpoints import router as compensation_router
from app.modules.contract.presentation.endpoints import router as contract_router
from app.modules.employee.presentation.endpoints import router as employee_router
from app.modules.payroll.presentation.endpoints import router as payroll_router
from app.modules.reporting.presentation.routes import router as reporting_router
from app.modules.timesheet.presentation.endpoints import router as timesheet_router

api_router = APIRouter()
api_router.include_router(employee_router, prefix="/employees", tags=["employees"])
api_router.include_router(contract_router, prefix="/contracts", tags=["contracts"])
api_router.include_router(compensation_router, prefix="/compensation", tags=["compensation"])
api_router.include_router(absence_router, prefix="/absence", tags=["absence"])
api_router.include_router(timesheet_router, prefix="/timesheet", tags=["timesheet"])
api_router.include_router(payroll_router, prefix="/payroll", tags=["payroll"])
api_router.include_router(reporting_router, prefix="/reporting", tags=["reporting"])

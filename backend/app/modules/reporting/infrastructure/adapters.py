"""
Reporting Module Adapters
Anti-Corruption Layer for accessing other modules' data
"""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.api.facade import AbsenceModuleFacade
from app.modules.compensation.api.facade import CompensationModuleFacade
from app.modules.contract.api.facade import ContractModuleFacade
from app.modules.employee.api.facade import EmployeeModuleFacade
from app.modules.payroll.infrastructure.read_model import PayrollReadModel
from app.modules.reporting.domain.value_objects import ReportParameters


class ReportingDataAdapter:
    """
    Adapter for gathering data from other modules for report generation
    Implements the Anti-Corruption Layer pattern
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_facade = EmployeeModuleFacade(session)
        self.absence_facade = AbsenceModuleFacade(session)
        self.compensation_facade = CompensationModuleFacade(session)
        self.contract_facade = ContractModuleFacade(session)
        self.payroll_read_model = PayrollReadModel(session)

    async def fetch_payroll_summary_data(self, parameters: ReportParameters) -> dict[str, Any]:
        """
        Fetch payroll summary data from Payroll module
        Returns data in format ready for report generation
        """
        # Build query parameters
        filters = {}

        if parameters.employee_id:
            filters["employee_id"] = UUID(parameters.employee_id)

        # Fetch payrolls from read model
        from sqlalchemy import select

        from app.modules.payroll.infrastructure.models import PayrollORM

        query = select(PayrollORM)

        if parameters.employee_id:
            query = query.where(PayrollORM.employee_id == UUID(parameters.employee_id))

        if parameters.start_date and parameters.end_date:
            start = date.fromisoformat(parameters.start_date)
            end = date.fromisoformat(parameters.end_date)
            query = query.where(
                PayrollORM.period_start_date >= start, PayrollORM.period_end_date <= end
            )

        result = await self.session.execute(query)
        payrolls = result.scalars().all()

        # Format data for report
        rows = []
        for payroll in payrolls:
            # Get employee name
            employee = await self.employee_facade.get_employee_by_id(payroll.employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            # Extract payroll summary data
            gross_pay = f"${payroll.gross_pay_amount:,.2f}" if payroll.gross_pay_amount else "$0.00"
            deductions = (
                f"${payroll.total_deductions_amount:,.2f}"
                if payroll.total_deductions_amount
                else "$0.00"
            )
            net_pay = f"${payroll.net_pay_amount:,.2f}" if payroll.net_pay_amount else "$0.00"
            period = f"{payroll.period_start_date} to {payroll.period_end_date}"

            rows.append([employee_name, gross_pay, deductions, net_pay, period])

        return {
            "headers": ["Employee", "Gross Pay", "Deductions", "Net Pay", "Period"],
            "rows": rows,
        }

    async def fetch_employee_compensation_data(
        self, parameters: ReportParameters
    ) -> dict[str, Any]:
        """
        Fetch employee compensation data from Contract and Compensation modules
        """
        # Get all employees or specific employee
        from sqlalchemy import select

        from app.modules.employee.infrastructure.models import EmployeeORM

        query = select(EmployeeORM)

        if parameters.employee_id:
            query = query.where(EmployeeORM.id == UUID(parameters.employee_id))

        if parameters.department:
            query = query.where(EmployeeORM.department == parameters.department)

        result = await self.session.execute(query)
        employees = result.scalars().all()

        # Build rows
        rows = []
        for employee in employees:
            employee_name = f"{employee.first_name} {employee.last_name}"

            # Get current contract for base salary
            check_date = date.today()
            if parameters.start_date:
                check_date = date.fromisoformat(parameters.start_date)

            contract = await self.contract_facade.get_active_contract_for_employee(
                employee.id, check_date
            )

            base_salary = Decimal("0")
            if contract:
                base_salary = contract.terms.rate_amount

            # Get bonuses for the period (or year)
            start = (
                date.fromisoformat(parameters.start_date)
                if parameters.start_date
                else date(check_date.year, 1, 1)
            )
            end = (
                date.fromisoformat(parameters.end_date)
                if parameters.end_date
                else date(check_date.year, 12, 31)
            )

            bonuses = await self.compensation_facade.get_bonuses_for_period(employee.id, start, end)

            total_bonuses = sum(bonus.amount_value for bonus in bonuses)
            total_comp = base_salary + total_bonuses

            year = start.year

            rows.append(
                [
                    employee_name,
                    f"${base_salary:,.2f}",
                    f"${total_bonuses:,.2f}",
                    f"${total_comp:,.2f}",
                    str(year),
                ]
            )

        return {"headers": ["Employee", "Base Salary", "Bonuses", "Total", "Year"], "rows": rows}

    async def fetch_absence_summary_data(self, parameters: ReportParameters) -> dict[str, Any]:
        """
        Fetch absence summary data from Absence module
        """
        # Get absences
        start = date.fromisoformat(parameters.start_date) if parameters.start_date else None
        end = date.fromisoformat(parameters.end_date) if parameters.end_date else None

        # Get absences from facade
        if parameters.employee_id and start and end:
            absences = await self.absence_facade.get_approved_absences_in_period(
                UUID(parameters.employee_id), start, end
            )
        elif parameters.employee_id:
            absences = await self.absence_facade.get_absences_for_employee(
                UUID(parameters.employee_id)
            )
        else:
            # Get all absences for the period
            from sqlalchemy import select

            from app.modules.absence.infrastructure.models import AbsenceORM

            query = select(AbsenceORM)

            if start and end:
                query = query.where(AbsenceORM.start_date >= start, AbsenceORM.end_date <= end)

            result = await self.session.execute(query)
            absence_orms = result.scalars().all()

            # Convert to response format
            from app.modules.absence.presentation.schemas import AbsenceResponse

            absences = [
                AbsenceResponse(
                    id=a.id,
                    employee_id=a.employee_id,
                    absence_type=a.absence_type,
                    start_date=a.start_date,
                    end_date=a.end_date,
                    status=a.status,
                    reason=a.reason,
                    created_at=a.created_at,
                    updated_at=a.updated_at,
                )
                for a in absence_orms
            ]

        # Build rows
        rows = []
        for absence in absences:
            # Get employee name
            employee = await self.employee_facade.get_employee_by_id(absence.employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            # Calculate days
            days = (absence.end_date - absence.start_date).days + 1

            rows.append(
                [
                    employee_name,
                    absence.absence_type.value
                    if hasattr(absence.absence_type, "value")
                    else str(absence.absence_type),
                    str(days),
                    str(absence.start_date),
                    str(absence.end_date),
                ]
            )

        return {
            "headers": ["Employee", "Absence Type", "Days", "Start Date", "End Date"],
            "rows": rows,
        }

    async def fetch_timesheet_summary_data(self, parameters: ReportParameters) -> dict[str, Any]:
        """
        Fetch timesheet summary data
        Note: Timesheet module not yet implemented, returning placeholder
        """
        return {
            "headers": [
                "Employee",
                "Regular Hours",
                "Overtime Hours",
                "Total Hours",
                "Week",
            ],
            "rows": [
                ["No timesheet data", "0", "0", "0", "N/A"],
            ],
        }

    async def fetch_tax_report_data(self, parameters: ReportParameters) -> dict[str, Any]:
        """
        Fetch tax report data from payroll records
        """
        # Build query for payrolls
        from sqlalchemy import select

        from app.modules.payroll.infrastructure.models import PayrollORM

        query = select(PayrollORM)

        if parameters.employee_id:
            query = query.where(PayrollORM.employee_id == UUID(parameters.employee_id))

        if parameters.start_date and parameters.end_date:
            start = date.fromisoformat(parameters.start_date)
            end = date.fromisoformat(parameters.end_date)
            query = query.where(
                PayrollORM.period_start_date >= start, PayrollORM.period_end_date <= end
            )

        result = await self.session.execute(query)
        payrolls = result.scalars().all()

        # Aggregate tax data by employee
        employee_taxes: dict[UUID, dict[str, Decimal]] = {}

        for payroll in payrolls:
            if payroll.employee_id not in employee_taxes:
                employee_taxes[payroll.employee_id] = {"gross": Decimal("0"), "taxes": Decimal("0")}

            employee_taxes[payroll.employee_id]["gross"] += payroll.gross_pay_amount or Decimal("0")
            employee_taxes[payroll.employee_id]["taxes"] += payroll.total_taxes_amount or Decimal(
                "0"
            )

        # Build rows
        rows = []
        for employee_id, tax_data in employee_taxes.items():
            employee = await self.employee_facade.get_employee_by_id(employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            gross = tax_data["gross"]
            total_tax = tax_data["taxes"]

            # Split tax into federal (70%) and state (30%) as example
            federal_tax = total_tax * Decimal("0.7")
            state_tax = total_tax * Decimal("0.3")

            rows.append(
                [
                    employee_name,
                    f"${gross:,.2f}",
                    f"${federal_tax:,.2f}",
                    f"${state_tax:,.2f}",
                    f"${total_tax:,.2f}",
                ]
            )

        return {
            "headers": [
                "Employee",
                "Gross Income",
                "Federal Tax",
                "State Tax",
                "Total Tax",
            ],
            "rows": rows,
        }

    async def fetch_custom_report_data(self, parameters: ReportParameters) -> dict[str, Any]:
        """
        Fetch custom report data based on additional_filters
        """
        return {
            "headers": ["Field 1", "Field 2", "Field 3"],
            "rows": [
                ["Custom report", "not yet", "implemented"],
            ],
        }

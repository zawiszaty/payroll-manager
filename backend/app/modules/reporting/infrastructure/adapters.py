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
        # Fetch payrolls from read model
        from sqlalchemy import select

        from app.modules.payroll.infrastructure.models import PayrollORM

        query = select(PayrollORM)

        if parameters.employee_id:
            query = query.where(PayrollORM.employee_id == UUID(parameters.employee_id))

        if parameters.start_date and parameters.end_date:
            query = query.where(
                PayrollORM.period_start_date >= parameters.start_date,
                PayrollORM.period_end_date <= parameters.end_date,
            )

        result = await self.session.execute(query)
        payrolls = result.scalars().all()

        # Bulk fetch all employees to avoid N+1 query
        employee_ids = list(set(payroll.employee_id for payroll in payrolls))
        employees_map = await self.employee_facade.get_employees_by_ids(employee_ids)

        # Format data for report
        rows = []
        for payroll in payrolls:
            # Get employee name from map
            employee = employees_map.get(payroll.employee_id)
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
            check_date = parameters.start_date if parameters.start_date else date.today()

            contract = await self.contract_facade.get_active_contract_for_employee(
                employee.id, check_date
            )

            base_salary = Decimal("0")
            if contract:
                base_salary = contract.terms.rate_amount

            # Get bonuses for the period (or year)
            start = parameters.start_date if parameters.start_date else date(check_date.year, 1, 1)
            end = parameters.end_date if parameters.end_date else date(check_date.year, 12, 31)

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
        # Get absences - parameters already have date objects
        start = parameters.start_date
        end = parameters.end_date

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

        # Bulk fetch all employees to avoid N+1 query
        employee_ids = list(set(absence.employee_id for absence in absences))
        employees_map = await self.employee_facade.get_employees_by_ids(employee_ids)

        # Build rows
        rows = []
        for absence in absences:
            # Get employee name from map
            employee = employees_map.get(absence.employee_id)
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
        Attempts to extract federal/state tax breakdown from payroll lines
        """
        # Build query for payrolls with lines eager-loaded
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.modules.payroll.domain.value_objects import PayrollLineType
        from app.modules.payroll.infrastructure.models import PayrollORM

        query = select(PayrollORM).options(selectinload(PayrollORM.lines))

        if parameters.employee_id:
            query = query.where(PayrollORM.employee_id == UUID(parameters.employee_id))

        if parameters.start_date and parameters.end_date:
            query = query.where(
                PayrollORM.period_start_date >= parameters.start_date,
                PayrollORM.period_end_date <= parameters.end_date,
            )

        result = await self.session.execute(query)
        payrolls = result.scalars().all()

        # Aggregate tax data by employee
        employee_taxes: dict[UUID, dict[str, Decimal]] = {}
        has_explicit_breakdown = False

        for payroll in payrolls:
            if payroll.employee_id not in employee_taxes:
                employee_taxes[payroll.employee_id] = {
                    "gross": Decimal("0"),
                    "federal_tax": Decimal("0"),
                    "state_tax": Decimal("0"),
                    "total_tax": Decimal("0"),
                }

            employee_taxes[payroll.employee_id]["gross"] += payroll.gross_pay_amount or Decimal("0")
            employee_taxes[payroll.employee_id]["total_tax"] += (
                payroll.total_taxes_amount or Decimal("0")
            )

            # Try to extract federal/state tax breakdown from payroll lines
            for line in payroll.lines:
                if line.line_type == PayrollLineType.TAX:
                    description_lower = line.description.lower()
                    amount = abs(line.amount) if line.amount else Decimal("0")

                    if "federal" in description_lower:
                        employee_taxes[payroll.employee_id]["federal_tax"] += amount
                        has_explicit_breakdown = True
                    elif "state" in description_lower:
                        employee_taxes[payroll.employee_id]["state_tax"] += amount
                        has_explicit_breakdown = True

        # Bulk fetch all employees to avoid N+1 query
        employee_ids = list(employee_taxes.keys())
        employees_map = await self.employee_facade.get_employees_by_ids(employee_ids)

        # Determine headers based on whether we have explicit breakdown
        if has_explicit_breakdown:
            headers = [
                "Employee",
                "Gross Income",
                "Federal Tax",
                "State Tax",
                "Total Tax",
            ]
        else:
            # No explicit breakdown available, show only total
            headers = [
                "Employee",
                "Gross Income",
                "Total Tax",
            ]

        # Build rows
        rows = []
        for employee_id, tax_data in employee_taxes.items():
            employee = employees_map.get(employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            gross = tax_data["gross"]
            total_tax = tax_data["total_tax"]

            if has_explicit_breakdown:
                federal_tax = tax_data["federal_tax"]
                state_tax = tax_data["state_tax"]

                rows.append(
                    [
                        employee_name,
                        f"${gross:,.2f}",
                        f"${federal_tax:,.2f}",
                        f"${state_tax:,.2f}",
                        f"${total_tax:,.2f}",
                    ]
                )
            else:
                # Only show gross and total tax when no breakdown available
                rows.append(
                    [
                        employee_name,
                        f"${gross:,.2f}",
                        f"${total_tax:,.2f}",
                    ]
                )

        return {
            "headers": headers,
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

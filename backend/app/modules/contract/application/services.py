"""
Application services for contract module
These services orchestrate business logic
"""

import logging
from datetime import date
from typing import List

from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.repository import ContractRepository

logger = logging.getLogger(__name__)


class ExpireContractsService:
    """
    Service to find and expire all contracts that have passed their end date.

    This can be called by:
    - A scheduled job (cron, systemd timer, Kubernetes CronJob)
    - An API endpoint (future)
    - Manual script
    """

    def __init__(self, repository: ContractRepository):
        self.repository = repository

    async def expire_due_contracts(self, check_date: date | None = None) -> List[Contract]:
        """
        Find all ACTIVE contracts with valid_to <= check_date and expire them.

        Args:
            check_date: Date to check against. Defaults to today.

        Returns:
            List of expired contracts
        """
        if check_date is None:
            check_date = date.today()

        logger.info(f"Checking for contracts to expire as of {check_date}")

        # Get expired contracts from repository (filtered at DB level for scalability)
        contracts_to_expire = await self.repository.get_expired_contracts(check_date)

        expired_contracts = []
        for contract in contracts_to_expire:
            logger.info(f"Expiring contract {contract.id} for employee {contract.employee_id}")
            try:
                contract.expire()
                updated_contract = await self.repository.update(contract)
                expired_contracts.append(updated_contract)
            except Exception as e:
                logger.error(f"Failed to expire contract {contract.id}: {e}")

        logger.info(f"Expired {len(expired_contracts)} contracts")
        return expired_contracts

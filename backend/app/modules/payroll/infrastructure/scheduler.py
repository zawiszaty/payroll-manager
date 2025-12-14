"""
Payroll Month-End Scheduler
This module handles scheduled tasks for end-of-month payroll processing
"""

import asyncio
import logging
from calendar import monthrange
from datetime import date, datetime, time, timedelta

from app.modules.payroll.domain.events import MonthEndEvent
from app.shared.domain.events import get_event_dispatcher

logger = logging.getLogger(__name__)


class PayrollScheduler:
    """
    Scheduler for payroll events, particularly month-end processing
    """

    def __init__(self):
        self.is_running = False
        self._task = None

    async def start(self) -> None:
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info("Payroll scheduler started")

    async def stop(self) -> None:
        """Stop the scheduler"""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Payroll scheduler stopped")

    async def _run_scheduler(self) -> None:
        """Main scheduler loop - checks daily at midnight"""
        while self.is_running:
            try:
                await self._check_and_trigger_month_end()

                # Sleep until next midnight
                now = datetime.now()
                tomorrow = now + timedelta(days=1)
                next_midnight = datetime.combine(tomorrow.date(), time.min)
                sleep_seconds = (next_midnight - now).total_seconds()

                logger.debug(f"Sleeping for {sleep_seconds / 3600:.2f} hours until next check")
                await asyncio.sleep(sleep_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # Sleep for an hour before retrying
                await asyncio.sleep(3600)

    async def _check_and_trigger_month_end(self) -> None:
        """Check if today is the last day of the month and trigger event if so"""
        today = date.today()
        last_day_of_month = monthrange(today.year, today.month)[1]

        if today.day == last_day_of_month:
            logger.info(f"Last day of month detected: {today}")
            await self._trigger_month_end_event(today.year, today.month)

    async def _trigger_month_end_event(self, year: int, month: int) -> None:
        """Trigger the month-end event for payroll processing"""
        try:
            # Calculate period dates
            first_day = date(year, month, 1)
            last_day = date(year, month, monthrange(year, month)[1])

            # Create and dispatch month-end event
            event = MonthEndEvent(
                year=year,
                month=month,
                period_start=first_day,
                period_end=last_day,
            )

            await get_event_dispatcher().dispatch(event)

            logger.info(f"Month-end event triggered for {year}-{month:02d}")

        except Exception as e:
            logger.error(f"Error triggering month-end event: {e}", exc_info=True)


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> PayrollScheduler:
    """Get the global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = PayrollScheduler()
    return _scheduler_instance


async def start_scheduler() -> None:
    """Start the payroll scheduler"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler() -> None:
    """Stop the payroll scheduler"""
    scheduler = get_scheduler()
    await scheduler.stop()


async def trigger_month_end_manually(year: int, month: int) -> None:
    """
    Manually trigger month-end processing for a specific year/month
    Useful for testing or processing past months
    """
    scheduler = get_scheduler()
    await scheduler._trigger_month_end_event(year, month)
    logger.info(f"Manually triggered month-end for {year}-{month:02d}")

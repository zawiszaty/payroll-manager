#!/usr/bin/env python3
"""
Script to simulate an external system publishing an event to create a pending absence request.
This demonstrates event-driven architecture where absence requests can come from external systems.
"""
import asyncio
import json
import sys
from datetime import date, timedelta
from uuid import uuid4

import aio_pika
from aio_pika import ExchangeType, Message


async def publish_absence_request_event(
    employee_id: str,
    absence_type: str = "vacation",
    start_date: str | None = None,
    end_date: str | None = None,
    reason: str | None = None,
    rabbitmq_url: str = "amqp://payroll:payroll@rabbitmq:5672/",
):
    """
    Publish an AbsenceRequestedEvent to RabbitMQ.

    Args:
        employee_id: UUID of the employee
        absence_type: Type of absence (vacation, sick_leave, parental_leave, etc.)
        start_date: Start date in YYYY-MM-DD format (defaults to tomorrow)
        end_date: End date in YYYY-MM-DD format (defaults to 3 days from start)
        reason: Optional reason for absence
        rabbitmq_url: RabbitMQ connection URL
    """
    # Default dates if not provided
    if start_date is None:
        start = date.today() + timedelta(days=1)
        start_date = start.isoformat()
    else:
        start = date.fromisoformat(start_date)

    if end_date is None:
        end = start + timedelta(days=2)  # 3 days total
        end_date = end.isoformat()

    # Create event data
    event_id = str(uuid4())
    event_data = {
        "event_id": event_id,
        "event_type": "AbsenceRequestedEvent",
        "timestamp": date.today().isoformat(),
        "version": "1.0",
        "source": "external-hr-system",
        "data": {
            "absence_id": str(uuid4()),
            "employee_id": employee_id,
            "absence_type": absence_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason or f"Absence request from external system",
            "notes": "Auto-generated from external HR system",
            "status": "pending",
        },
    }

    print(f"\n{'='*80}")
    print("Publishing Absence Request Event")
    print(f"{'='*80}")
    print(f"Event ID: {event_id}")
    print(f"Employee ID: {employee_id}")
    print(f"Absence Type: {absence_type}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Reason: {event_data['data']['reason']}")
    print(f"{'='*80}\n")

    try:
        # Connect to RabbitMQ
        print(f"Connecting to RabbitMQ at {rabbitmq_url}...")
        connection = await aio_pika.connect_robust(rabbitmq_url)
        channel = await connection.channel()

        # Declare the domain_events exchange
        exchange = await channel.declare_exchange(
            "domain_events", ExchangeType.TOPIC, durable=True
        )

        # Create message
        message_body = json.dumps(event_data, indent=2)
        message = Message(
            body=message_body.encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        # Routing key format: event.payroll-manager.absence.absence-requested-event
        routing_key = "event.payroll-manager.absence.absence-requested-event"

        # Publish event
        await exchange.publish(message, routing_key=routing_key)

        print(f"✅ Event published successfully!")
        print(f"   Routing Key: {routing_key}")
        print(f"   Exchange: domain_events")
        print(f"\n   Event Data:")
        print(f"   {message_body}\n")

        # Close connection
        await connection.close()

        print("✅ Connection closed")
        print(f"\n{'='*80}")
        print("NEXT STEPS:")
        print(f"{'='*80}")
        print("1. Check the backend logs to see if the event was consumed")
        print("2. Query the database to verify the absence was created:")
        print(f"   docker exec payroll_backend python -c \"")
        print(f"   import asyncio")
        print(f"   from app.database import AsyncSessionLocal")
        print(f"   from sqlalchemy import text")
        print(f"   async def check():")
        print(f"       async with AsyncSessionLocal() as session:")
        print(f"           result = await session.execute(")
        print(f"               text('SELECT id, employee_id, absence_type, start_date, end_date, status FROM absences WHERE employee_id = \\'{employee_id}\\' ORDER BY created_at DESC LIMIT 1')")
        print(f"           )")
        print(f"           row = result.first()")
        print(f"           if row:")
        print(f"               print(f'Absence created: {{row}}') ")
        print(f"           else:")
        print(f"               print('No absence found')")
        print(f"   asyncio.run(check())")
        print(f"   \"")
        print("3. Check the frontend at http://localhost:5173/absences")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Error publishing event: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Publish an absence request event to simulate external HR system"
    )
    parser.add_argument(
        "employee_id",
        help="Employee UUID (e.g., 6943b9a0-5c0e-4379-9c09-e73c6ba6d881)",
    )
    parser.add_argument(
        "--absence-type",
        default="vacation",
        choices=[
            "vacation",
            "sick_leave",
            "parental_leave",
            "unpaid_leave",
            "bereavement",
            "study_leave",
            "compassionate",
        ],
        help="Type of absence (default: vacation)",
    )
    parser.add_argument(
        "--start-date",
        help="Start date in YYYY-MM-DD format (default: tomorrow)",
    )
    parser.add_argument(
        "--end-date",
        help="End date in YYYY-MM-DD format (default: 3 days from start)",
    )
    parser.add_argument(
        "--reason",
        help="Reason for absence",
    )
    parser.add_argument(
        "--rabbitmq-url",
        default="amqp://payroll:payroll@rabbitmq:5672/",
        help="RabbitMQ connection URL",
    )

    args = parser.parse_args()

    success = await publish_absence_request_event(
        employee_id=args.employee_id,
        absence_type=args.absence_type,
        start_date=args.start_date,
        end_date=args.end_date,
        reason=args.reason,
        rabbitmq_url=args.rabbitmq_url,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

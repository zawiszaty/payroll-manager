import asyncio
import sys
from getpass import getpass

from app.database import AsyncSessionLocal
from app.modules.auth.application.services import AuthenticationService
from app.modules.auth.domain.value_objects import UserRole
from app.modules.auth.infrastructure.repository import SqlAlchemyUserRepository


async def create_user_command(
    email: str, password: str, role: str = "admin", full_name: str | None = None
):
    """Create a new user via CLI."""
    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)
        auth_service = AuthenticationService(repository)

        try:
            # Validate role
            user_role = UserRole(role.lower())

            user = await auth_service.create_user(
                email=email, password=password, role=user_role, full_name=full_name
            )
            await session.commit()

            print("✓ User created successfully!")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role.value}")
            print(f"  Full Name: {user.full_name or 'N/A'}")

        except ValueError as e:
            await session.rollback()
            print(f"✗ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            await session.rollback()
            print(f"✗ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


async def list_users_command():
    """List all users."""
    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)

        users = await repository.list_all()

        if not users:
            print("No users found.")
            return

        print(f"\nFound {len(users)} user(s):\n")
        print(f"{'ID':<38} {'Email':<30} {'Role':<10} {'Status':<10} {'Full Name':<20}")
        print("-" * 110)

        for user in users:
            print(
                f"{str(user.id):<38} {user.email:<30} {user.role.value:<10} "
                f"{user.status.value:<10} {user.full_name or 'N/A':<20}"
            )


async def deactivate_user_command(email: str):
    """Deactivate a user by email."""
    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)

        user = await repository.get_by_email(email)
        if not user:
            print(f"✗ User with email {email} not found.", file=sys.stderr)
            sys.exit(1)

        user.deactivate()
        await repository.update(user)
        await session.commit()

        print(f"✓ User {email} deactivated successfully.")


async def activate_user_command(email: str):
    """Activate a user by email."""
    async with AsyncSessionLocal() as session:
        repository = SqlAlchemyUserRepository(session)

        user = await repository.get_by_email(email)
        if not user:
            print(f"✗ User with email {email} not found.", file=sys.stderr)
            sys.exit(1)

        user.activate()
        await repository.update(user)
        await session.commit()

        print(f"✓ User {email} activated successfully.")


def main():
    """CLI entry point for user management."""
    import argparse

    parser = argparse.ArgumentParser(description="User management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create user command
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("email", help="User email address")
    create_parser.add_argument("--password", help="User password (will prompt if not provided)")
    create_parser.add_argument(
        "--role",
        choices=["admin", "user", "viewer"],
        default="admin",
        help="User role (default: admin)",
    )
    create_parser.add_argument("--full-name", help="User full name")

    # List users command
    subparsers.add_parser("list", help="List all users")

    # Deactivate user command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate a user")
    deactivate_parser.add_argument("email", help="User email address")

    # Activate user command
    activate_parser = subparsers.add_parser("activate", help="Activate a user")
    activate_parser.add_argument("email", help="User email address")

    args = parser.parse_args()

    if args.command == "create":
        password = args.password
        if not password:
            password = getpass("Enter password: ")
            password_confirm = getpass("Confirm password: ")
            if password != password_confirm:
                print("✗ Passwords do not match.", file=sys.stderr)
                sys.exit(1)

        asyncio.run(
            create_user_command(
                email=args.email,
                password=password,
                role=args.role,
                full_name=args.full_name,
            )
        )

    elif args.command == "list":
        asyncio.run(list_users_command())

    elif args.command == "deactivate":
        asyncio.run(deactivate_user_command(email=args.email))

    elif args.command == "activate":
        asyncio.run(activate_user_command(email=args.email))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

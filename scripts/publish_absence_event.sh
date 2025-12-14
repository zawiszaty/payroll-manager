#!/bin/bash
# Wrapper script to publish absence request events
# This simulates an external HR system creating absence requests

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <employee-id> [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --absence-type TYPE    Type of absence (default: vacation)"
    echo "                         Options: vacation, sick_leave, parental_leave,"
    echo "                                  unpaid_leave, bereavement, study_leave, compassionate"
    echo "  --start-date DATE      Start date in YYYY-MM-DD format (default: tomorrow)"
    echo "  --end-date DATE        End date in YYYY-MM-DD format (default: 3 days from start)"
    echo "  --reason TEXT          Reason for absence"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 6943b9a0-5c0e-4379-9c09-e73c6ba6d881"
    echo "  $0 6943b9a0-5c0e-4379-9c09-e73c6ba6d881 --absence-type sick_leave --reason \"Doctor appointment\""
    echo "  $0 6943b9a0-5c0e-4379-9c09-e73c6ba6d881 --start-date 2025-12-20 --end-date 2025-12-25"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if backend container is running
if ! docker ps | grep -q payroll_backend; then
    echo -e "${RED}Error: payroll_backend container is not running${NC}"
    echo "Please start the services first: docker compose up -d"
    exit 1
fi

echo -e "${GREEN}Publishing absence request event...${NC}"
echo ""

# Execute the Python script inside the container
docker exec payroll_backend python /app/scripts/publish_absence_request_event.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Event published successfully!${NC}"
    echo -e "${YELLOW}Check the frontend at: http://localhost:5173/absences${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed to publish event${NC}"
    exit $exit_code
fi

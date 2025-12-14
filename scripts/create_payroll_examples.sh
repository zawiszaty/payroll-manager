#!/bin/bash

# Login and get token
echo "=== Logging in as admin ==="
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: ${TOKEN:0:50}..."

# Get first employee
echo -e "\n=== Getting employees ==="
EMPLOYEES=$(curl -s -X GET "http://localhost:8000/api/v1/employees/?page=1&limit=5" \
  -H "Authorization: Bearer $TOKEN")

echo "Employees response:"
echo $EMPLOYEES | jq '.'

EMPLOYEE_ID=$(echo $EMPLOYEES | jq -r '.items[0].id')
echo "Using employee ID: $EMPLOYEE_ID"

if [ "$EMPLOYEE_ID" = "null" ] || [ -z "$EMPLOYEE_ID" ]; then
    echo "No employees found. Creating one first..."

    # Create an employee
    NEW_EMP=$(curl -s -X POST "http://localhost:8000/api/v1/employees/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "hire_date": "2024-01-01"
      }')

    EMPLOYEE_ID=$(echo $NEW_EMP | jq -r '.id')
    echo "Created employee with ID: $EMPLOYEE_ID"
fi

# Create payroll example 1 - Monthly payroll (DRAFT)
echo -e "\n=== Creating Payroll 1: Monthly DRAFT ==="
PAYROLL1=$(curl -s -X POST "http://localhost:8000/api/v1/payrolls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"employee_id\": \"$EMPLOYEE_ID\",
    \"period_type\": \"MONTHLY\",
    \"period_start_date\": \"2025-12-01\",
    \"period_end_date\": \"2025-12-31\",
    \"notes\": \"December 2025 monthly payroll\"
  }")

PAYROLL1_ID=$(echo $PAYROLL1 | jq -r '.id')
echo "Created payroll 1: $PAYROLL1_ID"
echo $PAYROLL1 | jq '.'

# Create payroll example 2 - Weekly payroll
echo -e "\n=== Creating Payroll 2: Weekly ==="
PAYROLL2=$(curl -s -X POST "http://localhost:8000/api/v1/payrolls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"employee_id\": \"$EMPLOYEE_ID\",
    \"period_type\": \"WEEKLY\",
    \"period_start_date\": \"2025-12-09\",
    \"period_end_date\": \"2025-12-15\",
    \"notes\": \"Week 50 - 2025\"
  }")

PAYROLL2_ID=$(echo $PAYROLL2 | jq -r '.id')
echo "Created payroll 2: $PAYROLL2_ID"
echo $PAYROLL2 | jq '.'

# Create payroll example 3 - Bi-weekly payroll
echo -e "\n=== Creating Payroll 3: Bi-weekly ==="
PAYROLL3=$(curl -s -X POST "http://localhost:8000/api/v1/payrolls/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"employee_id\": \"$EMPLOYEE_ID\",
    \"period_type\": \"BIWEEKLY\",
    \"period_start_date\": \"2025-12-01\",
    \"period_end_date\": \"2025-12-14\",
    \"notes\": \"Bi-weekly period Dec 1-14\"
  }")

PAYROLL3_ID=$(echo $PAYROLL3 | jq -r '.id')
echo "Created payroll 3: $PAYROLL3_ID"
echo $PAYROLL3 | jq '.'

# Calculate the first payroll
if [ "$PAYROLL1_ID" != "null" ] && [ -n "$PAYROLL1_ID" ]; then
    echo -e "\n=== Calculating Payroll 1 ==="
    CALC_RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/payrolls/$PAYROLL1_ID/calculate" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "working_days": 22
      }')

    echo "Calculated payroll:"
    echo $CALC_RESULT | jq '.'
fi

# List all payrolls
echo -e "\n=== Listing all payrolls ==="
ALL_PAYROLLS=$(curl -s -X GET "http://localhost:8000/api/v1/payrolls/?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN")

echo $ALL_PAYROLLS | jq '.'

echo -e "\n=== Done! ==="
echo "Created 3 example payrolls"
echo "Payroll 1: $PAYROLL1_ID (Monthly)"
echo "Payroll 2: $PAYROLL2_ID (Weekly)"
echo "Payroll 3: $PAYROLL3_ID (Bi-weekly)"

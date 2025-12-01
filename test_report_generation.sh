#!/bin/bash

set -e  # Exit on error

echo "=== Testing Report Generation Feature ==="
echo ""

# Step 1: Create a report
echo "1. Creating a payroll report..."
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/reporting/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Payroll Report",
    "report_type": "payroll_summary",
    "format": "pdf",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }')

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

# Validate HTTP status code
if [ "$HTTP_CODE" != "201" ]; then
  echo "ERROR: Failed to create report. HTTP status: $HTTP_CODE"
  echo "Response: $RESPONSE"
  exit 1
fi

# Extract and validate REPORT_ID
REPORT_ID=$(echo "$RESPONSE" | jq -r '.id')
if [ -z "$REPORT_ID" ] || [ "$REPORT_ID" = "null" ]; then
  echo "ERROR: Failed to extract REPORT_ID from response"
  echo "Response: $RESPONSE"
  exit 1
fi

echo "Report created with ID: $REPORT_ID"
echo "Status: $(echo "$RESPONSE" | jq -r '.status')"
echo ""

# Step 2: Generate the report file
echo "2. Generating the report file..."
sleep 1
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/reporting/$REPORT_ID/generate)

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
GENERATE_RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

# Validate HTTP status code
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: Failed to generate report. HTTP status: $HTTP_CODE"
  echo "Response: $GENERATE_RESPONSE"
  exit 1
fi

# Extract and validate status and file_path
REPORT_STATUS=$(echo "$GENERATE_RESPONSE" | jq -r '.status')
FILE_PATH=$(echo "$GENERATE_RESPONSE" | jq -r '.file_path')

if [ -z "$REPORT_STATUS" ] || [ "$REPORT_STATUS" = "null" ]; then
  echo "ERROR: Failed to extract status from response"
  echo "Response: $GENERATE_RESPONSE"
  exit 1
fi

if [ -z "$FILE_PATH" ] || [ "$FILE_PATH" = "null" ]; then
  echo "ERROR: Failed to extract file_path from response"
  echo "Response: $GENERATE_RESPONSE"
  exit 1
fi

echo "Status after generation: $REPORT_STATUS"
echo "File path: $FILE_PATH"
echo ""

# Step 3: Download the report
echo "3. Downloading the report..."
sleep 1
HTTP_CODE=$(curl -s -w "%{http_code}" -X GET http://localhost:8000/api/v1/reporting/$REPORT_ID/download -o /tmp/downloaded_report.pdf)

# Validate HTTP status code
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: Failed to download report. HTTP status: $HTTP_CODE"
  exit 1
fi

# Validate downloaded file
if [ ! -f /tmp/downloaded_report.pdf ]; then
  echo "ERROR: Downloaded file not found at /tmp/downloaded_report.pdf"
  exit 1
fi

if [ ! -s /tmp/downloaded_report.pdf ]; then
  echo "ERROR: Downloaded file is empty"
  exit 1
fi

FILE_SIZE=$(ls -lh /tmp/downloaded_report.pdf | awk '{print $5}')
echo "Report downloaded successfully! Size: $FILE_SIZE"
echo "File saved to: /tmp/downloaded_report.pdf"
echo ""

# Step 4: Get report details
echo "4. Getting final report details..."
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:8000/api/v1/reporting/$REPORT_ID)

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
FINAL_RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

# Validate HTTP status code
if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: Failed to get report details. HTTP status: $HTTP_CODE"
  echo "Response: $FINAL_RESPONSE"
  exit 1
fi

# Extract and validate required fields
REPORT_NAME=$(echo "$FINAL_RESPONSE" | jq -r '.name')
REPORT_TYPE=$(echo "$FINAL_RESPONSE" | jq -r '.report_type')
REPORT_FORMAT=$(echo "$FINAL_RESPONSE" | jq -r '.format')
FINAL_STATUS=$(echo "$FINAL_RESPONSE" | jq -r '.status')

if [ -z "$REPORT_NAME" ] || [ "$REPORT_NAME" = "null" ]; then
  echo "ERROR: Failed to extract name from response"
  echo "Response: $FINAL_RESPONSE"
  exit 1
fi

echo "Name: $REPORT_NAME"
echo "Type: $REPORT_TYPE"
echo "Format: $REPORT_FORMAT"
echo "Status: $FINAL_STATUS"
echo ""

echo "=== Test Complete! ==="
echo ""
echo "Try different formats:"
echo "- PDF:  \"format\": \"pdf\""
echo "- CSV:  \"format\": \"csv\""
echo "- XLSX: \"format\": \"xlsx\""
echo "- JSON: \"format\": \"json\""
echo ""
echo "Try different report types:"
echo "- payroll_summary"
echo "- employee_compensation"
echo "- absence_summary"
echo "- timesheet_summary"
echo "- tax_report"
echo "- custom"

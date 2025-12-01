#!/bin/bash

echo "=== Testing Report Generation Feature ==="
echo ""

# Step 1: Create a report
echo "1. Creating a payroll report..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/reporting/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Payroll Report",
    "report_type": "payroll_summary",
    "format": "pdf",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }')

REPORT_ID=$(echo $RESPONSE | jq -r '.id')
echo "Report created with ID: $REPORT_ID"
echo "Status: $(echo $RESPONSE | jq -r '.status')"
echo ""

# Step 2: Generate the report file
echo "2. Generating the report file..."
sleep 1
GENERATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/reporting/$REPORT_ID/generate)
echo "Status after generation: $(echo $GENERATE_RESPONSE | jq -r '.status')"
echo "File path: $(echo $GENERATE_RESPONSE | jq -r '.file_path')"
echo ""

# Step 3: Download the report
echo "3. Downloading the report..."
sleep 1
curl -s -X GET http://localhost:8000/api/v1/reporting/$REPORT_ID/download -o /tmp/downloaded_report.pdf
if [ -f /tmp/downloaded_report.pdf ]; then
  FILE_SIZE=$(ls -lh /tmp/downloaded_report.pdf | awk '{print $5}')
  echo "Report downloaded successfully! Size: $FILE_SIZE"
  echo "File saved to: /tmp/downloaded_report.pdf"
else
  echo "Download failed!"
fi
echo ""

# Step 4: Get report details
echo "4. Getting final report details..."
FINAL_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/reporting/$REPORT_ID)
echo "Name: $(echo $FINAL_RESPONSE | jq -r '.name')"
echo "Type: $(echo $FINAL_RESPONSE | jq -r '.report_type')"
echo "Format: $(echo $FINAL_RESPONSE | jq -r '.format')"
echo "Status: $(echo $FINAL_RESPONSE | jq -r '.status')"
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

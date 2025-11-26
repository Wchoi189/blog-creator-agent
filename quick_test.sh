#!/bin/bash
# Quick Test Commands Reference
# Save this and run: source quick_test.sh

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Blog Creator - Quick Test Commands${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    echo -e "${BLUE}Testing: $1${NC}"
    curl -s "$2" "${@:3}" | jq . 2>/dev/null || echo "Request failed"
    echo ""
}

# 1. Check services
echo -e "${GREEN}=== Checking Services ===${NC}"
echo -n "Redis: "
redis-cli ping 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo "✗"

echo -n "Backend Health: "
curl -s http://localhost:8002/health | jq .status 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo "✗"

echo -n "Frontend: "
curl -s http://localhost:3002 > /dev/null && echo -e "${GREEN}✓${NC}" || echo "✗"

echo ""
echo -e "${GREEN}=== Test User Credentials ===${NC}"
echo "Email: browser_test@example.com"
echo "Password: TestPass123"
echo ""

echo -e "${GREEN}=== Quick API Tests ===${NC}"

# 2. Get existing token (if user exists)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjN2M5NWYyNi0xMzZkLTQ3ZjQtODFjYS01N2JlYjJkOGIwZWIiLCJleHAiOjE3NjQwODgxMjIsInR5cGUiOiJhY2Nlc3MifQ.q_uPMXQleVZb7AIvzi5QO2zuF2Rm9TQgP5sopQ6eXuk"

# 3. List documents
echo -e "${BLUE}Listing Documents:${NC}"
curl -s http://localhost:8002/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" | jq '.documents | length' 2>/dev/null && echo "documents found" || echo "Error listing documents"

echo ""

# 4. List drafts  
echo -e "${BLUE}Listing Blog Drafts:${NC}"
curl -s http://localhost:8002/api/v1/blog \
  -H "Authorization: Bearer $TOKEN" | jq '. | length' 2>/dev/null && echo "drafts found" || echo "Error listing drafts"

echo ""
echo -e "${GREEN}=== Browser URLs ===${NC}"
echo "Frontend: http://localhost:3002"
echo "Login: http://localhost:3002/login"
echo "Dashboard: http://localhost:3002/dashboard"
echo "Upload: http://localhost:3002/dashboard/upload"
echo "Documents: http://localhost:3002/dashboard/documents"
echo "Drafts: http://localhost:3002/dashboard/drafts"
echo ""

echo -e "${GREEN}=== Full API Examples ===${NC}"
cat << 'EOF'
# Register new user
curl -X POST http://localhost:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"Password123","full_name":"New User"}'

# Login
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"Password123"}'

# Save token and use in other requests:
TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"Password123"}' | jq -r '.access_token')

echo $TOKEN

# Upload PDF file
curl -X POST http://localhost:8002/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/file.pdf"

# Get documents
curl http://localhost:8002/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

# Create session
curl -X POST http://localhost:8002/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Session"}'

# Generate blog draft
curl -X POST "http://localhost:8002/api/v1/blog/generate?session_id=SESSION_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_ids":["DOC_ID"],"title":"My Blog"}'

# List drafts
curl http://localhost:8002/api/v1/blog \
  -H "Authorization: Bearer $TOKEN"

# Update draft
curl -X PUT http://localhost:8002/api/v1/blog/DRAFT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"New content","title":"Updated Title"}'
EOF

echo ""
echo -e "${GREEN}=== Documentation ===${NC}"
echo "See TESTING_GUIDE.md for detailed API testing"
echo "See SESSION_SUMMARY_2025-11-26.md for test results"
echo "See HANDOVER.md for project status"

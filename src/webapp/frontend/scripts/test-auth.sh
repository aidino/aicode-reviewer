#!/bin/bash

# Test runner script for authentication components and hooks
# Usage: ./scripts/test-auth.sh

set -e

echo "🧪 Running Authentication Tests for AI Code Reviewer Frontend"
echo "============================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run tests with reporting
run_test_suite() {
    local suite_name="$1"
    local test_pattern="$2"
    
    echo -e "\n${BLUE}📋 Running $suite_name...${NC}"
    echo "Pattern: $test_pattern"
    echo "----------------------------------------"
    
    if npm test -- --run "$test_pattern" --reporter=verbose; then
        echo -e "${GREEN}✅ $suite_name passed!${NC}"
    else
        echo -e "${RED}❌ $suite_name failed!${NC}"
        exit 1
    fi
}

# Change to frontend directory if not already there
if [[ ! -f "package.json" ]]; then
    echo "Changing to frontend directory..."
    cd "$(dirname "$0")/.."
fi

# Verify we're in the correct directory
if [[ ! -f "package.json" ]] || ! grep -q "aicode-reviewer-frontend" package.json; then
    echo -e "${RED}❌ Error: Not in frontend directory or package.json not found${NC}"
    exit 1
fi

echo "📂 Current directory: $(pwd)"
echo "📦 Package: $(grep '"name"' package.json | cut -d'"' -f4)"

# Install dependencies if node_modules doesn't exist
if [[ ! -d "node_modules" ]]; then
    echo -e "\n${BLUE}📦 Installing dependencies...${NC}"
    npm install
fi

# Run authentication test suites
echo -e "\n${BLUE}🔐 Starting Authentication Test Suites${NC}"

# Test authentication hooks
run_test_suite "Authentication Hooks" "src/hooks/__tests__/useAuth.test.ts"

# Test authentication components
run_test_suite "LoginForm Component" "src/components/auth/__tests__/LoginForm.test.tsx"
run_test_suite "RegisterForm Component" "src/components/auth/__tests__/RegisterForm.test.tsx"
run_test_suite "ProtectedRoute Component" "src/components/auth/__tests__/ProtectedRoute.test.tsx"

# Run all auth tests together for coverage
echo -e "\n${BLUE}📊 Running all authentication tests with coverage...${NC}"
echo "Pattern: src/**/*auth*/**/*.test.{ts,tsx}"
echo "----------------------------------------"

if npm run test:coverage -- --run "src/**/*auth*/**/*.test.{ts,tsx}"; then
    echo -e "${GREEN}✅ All authentication tests passed with coverage!${NC}"
else
    echo -e "${RED}❌ Some authentication tests failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 All Authentication Tests Completed Successfully!${NC}"
echo "============================================================="
echo "Summary:"
echo "✅ Authentication Hooks Tests"
echo "✅ LoginForm Component Tests"
echo "✅ RegisterForm Component Tests"
echo "✅ ProtectedRoute Component Tests"
echo "✅ Test Coverage Report Generated"
echo ""
echo "📋 Next steps:"
echo "1. Review test coverage report in coverage/ directory"
echo "2. Add API endpoint tests for backend authentication"
echo "3. Add security testing for token validation"
echo "4. Update API documentation"
echo "5. Create user guide for authentication features" 
#!/bin/bash

BASE_URL="http://localhost:8080"  # copy and paste this line of code if my app runs on a different port

# Function to run a test and check the result
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="$3"

    echo "Running test: $test_name"
    response=$(eval "$command")
    status=$?

    if [ $status -eq $expected_status ]; then
        echo "Test passed: $test_name"
    else
        echo "Test failed: $test_name"
        echo "Response: $response"
    fi
    echo
}

# User Registration Test
run_test "User Registration" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST $BASE_URL/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"email\":\"testuser@example.com\",\"password\":\"testpassword\"}'" \
    0

# User Login Test
run_test "User Login" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST $BASE_URL/login -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"password\":\"testpassword\"}'" \
    0

# User Logout Test
run_test "User Logout" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST $BASE_URL/logout" \
    0

echo "Integration tests completed."

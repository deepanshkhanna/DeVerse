#!/bin/bash

################################################################################
# DevVerse Test Execution Script with Automated Logging
# 
# Purpose: Execute Python tests and main application while capturing output
#          to both terminal (for real-time monitoring) and log file (for judges)
#
# Usage: ./run_tests.sh
################################################################################

set -e  # Exit on error

# Color codes for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DevVerse Test Execution Suite${NC}"
echo -e "${BLUE}  Feature: Zero-Trust TEE Integration${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Create logs directory if it doesn't exist
echo -e "${YELLOW}[1/4] Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory ready${NC}\n"

# Initialize log file with header
LOG_FILE="logs/execution.log"
echo "========================================" > "$LOG_FILE"
echo "DevVerse Test Execution Log" >> "$LOG_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> "$LOG_FILE"
echo "Branch: feature/zero-trust-tee" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run stress tests
echo -e "${YELLOW}[2/4] Running stress tests (src/stress_test.py)...${NC}"
echo "--- STRESS TEST OUTPUT ---" | tee -a "$LOG_FILE"
python tests/stress_test.py 2>&1 | tee -a "$LOG_FILE"
STRESS_EXIT_CODE=${PIPESTATUS[0]}

if [ $STRESS_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Stress tests completed successfully${NC}\n" | tee -a "$LOG_FILE"
else
    echo -e "${RED}✗ Stress tests failed with exit code $STRESS_EXIT_CODE${NC}\n" | tee -a "$LOG_FILE"
fi

# Run main application
echo -e "${YELLOW}[3/4] Running main application (src/main.py)...${NC}"
echo "" | tee -a "$LOG_FILE"
echo "--- MAIN APPLICATION OUTPUT ---" | tee -a "$LOG_FILE"
python src/main.py 2>&1 | tee -a "$LOG_FILE"
MAIN_EXIT_CODE=${PIPESTATUS[0]}

if [ $MAIN_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Main application executed successfully${NC}\n" | tee -a "$LOG_FILE"
else
    echo -e "${RED}✗ Main application failed with exit code $MAIN_EXIT_CODE${NC}\n" | tee -a "$LOG_FILE"
fi

# Summary
echo -e "${YELLOW}[4/4] Generating execution summary...${NC}"
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "EXECUTION SUMMARY" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Stress Test Exit Code: $STRESS_EXIT_CODE" | tee -a "$LOG_FILE"
echo "Main Application Exit Code: $MAIN_EXIT_CODE" | tee -a "$LOG_FILE"
echo "Log File: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Final status
if [ $STRESS_EXIT_CODE -eq 0 ] && [ $MAIN_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed! Log saved to $LOG_FILE${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Check $LOG_FILE for details${NC}"
    exit 1
fi

# Made with Bob

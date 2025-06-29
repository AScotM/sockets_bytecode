#!/bin/bash

# Configuration
LOG_LEVEL="INFO"  # Can be INFO, ERROR
JSON_OUTPUT=false
SHOW_BYTECODE=false

# Logging function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    if [[ "$level" == "ERROR" ]] || [[ "$LOG_LEVEL" == "INFO" && "$level" == "INFO" ]]; then
        echo "${timestamp} - ${level} - ${message}"
    fi
}

# Check if ss command exists
check_ss_command() {
    if ! command -v ss &> /dev/null; then
        log "ERROR" "Error: 'ss' command not found. Please install iproute."
        exit 1
    fi
}

# Get socket summary
get_socket_summary() {
    local start_time=$(date +%s.%N)
    log "INFO" "Executing 'ss' command to fetch socket summary..."
    
    if ! output=$(ss -s 2>&1); then
        log "ERROR" "Command error: $output"
        return 1
    fi
    
    local end_time=$(date +%s.%N)
    local elapsed_time=$(echo "$end_time - $start_time" | bc -l | awk '{printf "%.4f", $0}')
    log "INFO" "Success! Retrieved socket summary in ${elapsed_time}s."
    
    if $JSON_OUTPUT; then
        parse_socket_summary "$output"
    else
        echo "$output"
    fi
}

# Parse socket summary to JSON
parse_socket_summary() {
    local output="$1"
    declare -A parsed_data
    
    while IFS= read -r line; do
        if [[ $line == *":"* ]]; then
            key=$(echo "$line" | cut -d':' -f1 | xargs)
            value=$(echo "$line" | cut -d':' -f2- | xargs)
            parsed_data["$key"]="$value"
        fi
    done <<< "$output"
    
    # Convert associative array to JSON
    echo "{"
    local first=true
    for key in "${!parsed_data[@]}"; do
        if $first; then
            first=false
        else
            echo ","
        fi
        printf '    "%s": "%s"' "$key" "${parsed_data[$key]}"
    done
    echo -e "\n}"
}

# Main function
print_socket_summary() {
    log "INFO" "Welcome to the Socket Summary Analyzer"
    
    local summary=$(get_socket_summary)
    if [[ $? -ne 0 ]]; then
        exit 1
    fi
    
    log "INFO" "Socket Summary:"
    echo "$summary"
    
    if $SHOW_BYTECODE; then
        log "INFO" "Bytecode Analysis:"
        log "ERROR" "Bytecode analysis not available in Bash"
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --bytecode)
            SHOW_BYTECODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main execution
check_ss_command
print_socket_summary

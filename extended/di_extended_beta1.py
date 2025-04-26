import subprocess
import dis
import io
import contextlib
import logging
import shutil
import json
import time
import argparse
import re
from typing import Union, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_socket_summary(json_output: bool = False, socket_type: str = None) -> Union[str, Dict]:
    """
    Executes the 'ss' command to fetch socket summary and returns the result.
    If json_output is True, returns structured JSON.
    Optionally filters by socket type (e.g., 't' for TCP, 'u' for UDP, 'x' for UNIX).

    Args:
        json_output: If True, returns JSON; otherwise, returns raw output.
        socket_type: Socket type to filter (e.g., 't', 'u', 'x').

    Returns:
        Union[str, Dict]: Socket summary as a string or JSON string.
    """
    if shutil.which("ss") is None:
        error_message = "Error: 'ss' command not found. Please install iproute."
        logging.error(error_message)
        return error_message

    cmd = ["ss", "-s"]
    if socket_type:
        if socket_type in ["t", "u", "x"]:
            cmd.append(f"-{socket_type}")
        else:
            error_message = f"Invalid socket type: {socket_type}. Use 't' (TCP), 'u' (UDP), or 'x' (UNIX)."
            logging.error(error_message)
            return error_message

    logging.info(f"Executing 'ss' command: {' '.join(cmd)}")
    start_time = time.time()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        elapsed_time = round(time.time() - start_time, 4)
        logging.info(f"Success! Retrieved socket summary in {elapsed_time}s.")

        if json_output:
            return parse_socket_summary(result.stdout)
        return result.stdout.strip()

    except FileNotFoundError:
        error_message = "Error: 'ss' command not found."
        logging.error(error_message)
        return error_message
    except subprocess.CalledProcessError as e:
        error_message = f"Command error: {e}"
        logging.error(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logging.error(error_message)
        return error_message

def parse_socket_summary(output: str) -> str:
    """
    Parses the 'ss -s' output into a structured JSON format, converting numeric values to integers.

    Args:
        output: Raw output from the 'ss' command.

    Returns:
        str: JSON string of parsed data.
    """
    parsed_data = {}
    for line in output.splitlines():
        # Use regex to match key-value pairs (e.g., "Total: 123" or "TCP: 45 (estab 30, closed 10)")
        match = re.match(r"(\w+)\s*:\s*(.+)", line)
        if match:
            key, value = match.groups()
            # Try to convert value to int if it's purely numeric
            try:
                parsed_data[key] = int(value)
            except ValueError:
                # Otherwise, keep as string (e.g., for complex values like "45 (estab 30, closed 10)")
                parsed_data[key] = value.strip()
    return json.dumps(parsed_data, indent=4)

def get_bytecode(func) -> str:
    """
    Disassembles the given function and returns its bytecode as a string.

    Args:
        func: Function to disassemble.

    Returns:
        str: Bytecode as a string.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return buf.getvalue()

def print_socket_summary(show_bytecode: bool = False, json_output: bool = False, socket_type: str = None) -> None:
    """
    Prints the socket summary and (optional) bytecode analysis.

    Args:
        show_bytecode: If True, prints bytecode of get_socket_summary.
        json_output: If True, outputs socket summary as JSON.
        socket_type: Socket type to filter (e.g., 't', 'u', 'x').
    """
    logging.info("Welcome to the Socket Summary Analyzer")

    socket_summary = get_socket_summary(json_output=json_output, socket_type=socket_type)
    
    logging.info("Socket Summary:")
    print(socket_summary)

    if show_bytecode:
        logging.info("Bytecode Analysis:")
        print(get_bytecode(get_socket_summary))

def main() -> None:
    """
    Main function to parse command-line arguments and run the socket summary analyzer.
    """
    parser = argparse.ArgumentParser(description="Socket Summary Analyzer for Linux")
    parser.add_argument("--json", action="store_true", help="Output socket summary in JSON format")
    parser.add_argument("--bytecode", action="store_true", help="Show bytecode analysis of get_socket_summary")
    parser.add_argument("--type", choices=["t", "u", "x"], help="Filter by socket type (t: TCP, u: UDP, x: UNIX)")
    args = parser.parse_args()

    print_socket_summary(
        show_bytecode=args.bytecode,
        json_output=args.json,
        socket_type=args.type
    )

if __name__ == "__main__":
    main()

import subprocess
import dis
import io
import contextlib
import logging
import shutil
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_socket_summary(json_output=False):
    """
    Executes the 'ss' command to fetch socket summary and returns the result.
    If json_output is True, returns structured JSON.
    """
    if shutil.which("ss") is None:
        error_message = "Error: 'ss' command not found. Please install iproute."
        logging.error(error_message)
        return error_message

    logging.info("Executing 'ss' command to fetch socket summary...")
    start_time = time.time()  # Track execution time

    try:
        result = subprocess.run(["ss", "-s"], capture_output=True, text=True, check=True)
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

def parse_socket_summary(output):
    """
    Parses the 'ss -s' output into a structured JSON format.
    """
    parsed_data = {}
    lines = output.splitlines()

    for line in lines:
        parts = line.split(":")
        if len(parts) == 2:
            key, value = parts[0].strip(), parts[1].strip()
            parsed_data[key] = value

    return json.dumps(parsed_data, indent=4)

def get_bytecode(func):
    """
    Disassembles the given function and returns its bytecode as a string.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return buf.getvalue()

def print_socket_summary(show_bytecode=False, json_output=False):
    """
    Prints the socket summary and (optional) bytecode analysis.
    """
    logging.info("Welcome to the Socket Summary Analyzer")

    socket_summary = get_socket_summary(json_output=json_output)
    
    logging.info("Socket Summary:")
    print(socket_summary)

    if show_bytecode:
        logging.info("Bytecode Analysis:")
        print(get_bytecode(get_socket_summary))

if __name__ == "__main__":
    print_socket_summary(show_bytecode=True, json_output=False)

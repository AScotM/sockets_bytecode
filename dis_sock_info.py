import subprocess
import dis
import io
import contextlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_socket_summary():
    """
    Executes the 'ss' command to fetch socket summary and returns the result.
    """
    logging.info("Executing 'ss' command to fetch socket summary...")
    try:
        result = subprocess.run(['ss', '-s'], capture_output=True, text=True, check=True)
        logging.info("Success! Retrieved socket summary.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_message = f"Command error: {e}"
        logging.error(error_message)
        return error_message
    except FileNotFoundError:
        error_message = "Error: 'ss' command not found. Please install iproute."
        logging.error(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        logging.error(error_message)
        return error_message

def get_bytecode(func):
    """
    Disassembles the given function and returns its bytecode as a string.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return buf.getvalue()

def print_socket_summary():
    """
    Prints the socket summary and bytecode analysis of the get_socket_summary function.
    """
    logging.info("Welcome to the Socket Summary Analyzer")
    
    socket_summary = get_socket_summary()
    logging.info("Socket Summary:")
    print(socket_summary)
    
    logging.info("Bytecode Analysis:")
    print(get_bytecode(get_socket_summary))

if __name__ == "__main__":
    print_socket_summary()

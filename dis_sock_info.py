import subprocess
import dis
import io
import contextlib

def get_socket_summary():
    print("Executing 'ss' command to fetch socket summary...")
    try:
        result = subprocess.run(['ss', '-s'], capture_output=True, text=True)
        print("Success! Retrieved socket summary.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_message = f"Command error: {e}"
        print(error_message)
        return error_message
    except FileNotFoundError:
        error_message = "Error: 'ss' command not found. Please install iproute."
        print(error_message)
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        return error_message

def get_bytecode(func):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dis.dis(func)
    return buf.getvalue()

def print_socket_summary():
    print("Welcome to the Socket Summary Analyzer")
    
    socket_summary = get_socket_summary()
    print("Socket Summary:")
    print(socket_summary)
    
    print("Bytecode Analysis:")
    print(get_bytecode(get_socket_summary))

if __name__ == "__main__":
    print_socket_summary()

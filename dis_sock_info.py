import subprocess
import dis

def get_socket_summary():
    try:
        # Get socket summary using ss -s command where subprocess comes in action
        socket_summary = subprocess.check_output(['ss', '-s']).decode()
        return socket_summary
    except Exception as e:
        return f"Error: {e}"

def print_socket_summary():
    # Get socket summary and print it as normally python prints things
    socket_summary = get_socket_summary()
    print("Socket Summary:")
    print(socket_summary)

    # Here comes bytecode
    print("\nBytecode of get_socket_summary function:")
    dis.dis(get_socket_summary)

if __name__ == "__main__":
    print_socket_summary()


import subprocess
import dis

def get_socket_summary():
    try:
       
        socket_summary = subprocess.check_output(['ss', '-s'], encoding='utf-8')
        return socket_summary
    except subprocess.CalledProcessError as e:
        return f"Command error: {e}"
    except FileNotFoundError:
        return "Error: 'ss' command not found. Please install it."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def print_socket_summary():
    
    socket_summary = get_socket_summary()
    print("Socket Summary:")
    print(socket_summary)

    
    print("\nBytecode of get_socket_summary function:")
    dis.dis(get_socket_summary) 

if __name__ == "__main__":
    print_socket_summary()

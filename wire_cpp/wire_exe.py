import subprocess

# This is python code to execute C++ code (temperature files) using subprocess module
# TODO: Add error handling for subprocess calls and file reading operations
#TODO: Replace hardcoded file paths with environment variables or command line arguments
#TODO: Add command line arguments for specifying input and output file paths
#TODO: This is not implemented
def cpp_read_1wire_sensors():
    result = subprocess.run(['./wire_reader'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    return [float(line.split(': ')[1].rstrip('°C')) for line in lines]

if __name__ == "__main__":
    temperatures = cpp_read_1wire_sensors()
    print(f"Temperatures: {temperatures}")
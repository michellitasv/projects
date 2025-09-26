#!/usr/bin/env python3
import os
import subprocess
import hashlib
import psutil
import shutil
from datetime import datetime

# --- Configuration ---------------------------------------------------
# TODO: You MUST change these two values for the file check to work.

# 1. The full path to the file you want to check for corruption.
#    Example: "/etc/hosts" or "C:\\Windows\\System32\\drivers\\etc\\hosts"
FILE_TO_CHECK = "/etc/" 

# 2. The known-good SHA256 hash of that file. 
#    See "Part 3: How to Use" for instructions on how to generate this.
EXPECTED_SHA256_HASH = "SHA256"

# --- Health Thresholds (percentage) ---
CPU_WARN_THRESHOLD = 85.0
MEM_WARN_THRESHOLD = 85.0
DISK_WARN_THRESHOLD = 90.0

# --- Color Formatting for Terminal Output ---
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(title):
    """Prints a bold, formatted header."""
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}--- {title} ---{bcolors.ENDC}")

def print_ok(key, value=""):
    """Prints a success message."""
    print(f"✅ {bcolors.OKGREEN}{key:<25}{bcolors.ENDC}{value}")

def print_warn(key, value=""):
    """Prints a warning message."""
    print(f"⚠️ {bcolors.WARNING}{key:<25}{bcolors.ENDC}{value}")

def print_fail(key, value=""):
    """Prints a failure message."""
    print(f"❌ {bcolors.FAIL}{key:<25}{bcolors.ENDC}{value}")
    
def print_info(key, value=""):
    """Prints an informational message."""
    print(f"ℹ️ {bcolors.OKCYAN}{key:<25}{bcolors.ENDC}{value}")

def check_command_exists(command):
    """Checks if a command-line tool is available in the system's PATH."""
    return shutil.which(command) is not None

def check_cpu_health():
    """Checks CPU usage, load, and core count."""
    print_header("CPU Health")
    print_info("Physical Cores", psutil.cpu_count(logical=False))
    print_info("Logical Cores", psutil.cpu_count(logical=True))
    
    # Get CPU usage over a 1-second interval for a more accurate reading
    cpu_usage = psutil.cpu_percent(interval=1)
    if cpu_usage > CPU_WARN_THRESHOLD:
        print_warn("Current Usage", f"{cpu_usage}%")
    else:
        print_ok("Current Usage", f"{cpu_usage}%")

def check_memory_health():
    """Checks RAM and Swap memory usage."""
    print_header("Memory Health")
    mem = psutil.virtual_memory()
    mem_total_gb = mem.total / (1024**3)
    mem_used_gb = mem.used / (1024**3)
    
    if mem.percent > MEM_WARN_THRESHOLD:
        print_warn("RAM Usage", f"{mem.percent}% ({mem_used_gb:.2f}/{mem_total_gb:.2f} GB)")
    else:
        print_ok("RAM Usage", f"{mem.percent}% ({mem_used_gb:.2f}/{mem_total_gb:.2f} GB)")
        
def check_disk_health():
    """Checks disk usage for the root partition."""
    print_header("Disk Health")
    disk = psutil.disk_usage('/')
    disk_total_gb = disk.total / (1024**3)
    disk_used_gb = disk.used / (1024**3)

    if disk.percent > DISK_WARN_THRESHOLD:
        print_warn("Root ('/') Usage", f"{disk.percent}% ({disk_used_gb:.2f}/{disk_total_gb:.2f} GB)")
    else:
        print_ok("Root ('/') Usage", f"{disk.percent}% ({disk_used_gb:.2f}/{disk_total_gb:.2f} GB)")

def check_file_integrity(filepath, expected_hash):
    """Calculates the SHA256 hash of a file and compares it to a trusted value."""
    print_header("File Integrity Check")
    print_info("File Path", filepath)
    
    if not os.path.exists(filepath):
        print_fail("Status", "File does not exist.")
        return

    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        
        calculated_hash = hasher.hexdigest()
        
        print_info("Expected Hash", expected_hash)
        print_info("Calculated Hash", calculated_hash)

        if calculated_hash.lower() == expected_hash.lower():
            print_ok("Status", "File integrity verified.")
        else:
            print_fail("Status", "CORRUPT or MODIFIED! Hashes do not match.")

    except Exception as e:
        print_fail("Error checking file", str(e))

def check_gpu_health():
    """Runs nvidia-smi to check GPU status."""
    print_header("NVIDIA GPU Health")
    if not check_command_exists("nvidia-smi"):
        print_fail("nvidia-smi", "Command not found. Please ensure NVIDIA drivers are installed.")
        return
        
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            check=True
        )
        # Print the detailed output from the command
        print(f"{bcolors.OKBLUE}{result.stdout}{bcolors.ENDC}")
        print_ok("GPU Status", "Successfully queried.")
            
    except subprocess.CalledProcessError as e:
        print_fail("nvidia-smi failed", e.stderr)
    except FileNotFoundError:
        print_fail("nvidia-smi", "Command not found. Is it in your system's PATH?")
    except Exception as e:
        print_fail("An unknown error occurred", str(e))

def main():
    """Main function to run all health checks."""
    print(f"{bcolors.BOLD}System Health Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{bcolors.ENDC}")
    
    check_cpu_health()
    check_memory_health()
    check_disk_health()
    check_file_integrity(FILE_TO_CHECK, EXPECTED_SHA256_HASH)
    check_gpu_health()
    
    print("\n--- Report Complete ---\n")

if __name__ == "__main__":
    main()

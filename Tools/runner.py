import threading
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print(f"[STDOUT] {stdout.decode().strip()}")
    if stderr:
        print(f"[STDERR] {stderr.decode().strip()}")
    print(f"Finished executing: {command}")

def main():
    commands = [
        "python3 AI_Runner.py 8 8 3 l Sample_AIs/Poor_AI/main.py ../src/checkers-python/main.py",
        "python3 AI_Runner.py 8 8 3 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py"
    ]
    threads = [threading.Thread(target=run_command, args=(cmd,)) for cmd in commands for _ in range(10)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
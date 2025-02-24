import subprocess
import threading


def run_game(result_list, index, ai_path_1, ai_path_2):
    # Run each game using subprocess
    command = [
        "python3", "AI_Runner.py", "8", "8", "3", "l", ai_path_1, ai_path_2
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout

        # Extract result based on your AI game output format
        if "player 2 wins" in output:
            result_list[index] = "win"
        elif "Tie" in output:
            result_list[index] = "tie"
        else:
            result_list[index] = "loss"  # If any other result is assumed to be a loss for Player 2
    except Exception as e:
        print(f"Error in thread {index}: {e}")
        result_list[index] = "error"


def run_simulations(num_simulations=50, ai_path_1="Sample_AIs/Random_AI/main.py",
                    ai_path_2="../src/checkers-python/main.py"):
    result_list = [None] * num_simulations
    threads = []

    # Create and start threads
    for i in range(num_simulations):
        thread = threading.Thread(target=run_game, args=(result_list, i, ai_path_1, ai_path_2))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Calculate results
    wins = result_list.count("win")
    ties = result_list.count("tie")
    total = num_simulations

    print(f"Player 2 Wins: {wins / total * 100:.2f}%")
    print(f"Ties: {ties / total * 100:.2f}%")
    print(f"Errors: {result_list.count('error')}/{total}")


if __name__ == "__main__":
    # Running simulations
    ai_path_1 = "Sample_AIs/Random_AI/main.py"  # Path for AI 1
    ai_path_2 = "../src/checkers-python/main.py"  # Path for AI 2

    run_simulations(50, ai_path_1, ai_path_2)

#!/bin/bash

echo "Running tests in parallel..."

run_test() {
  python3 AI_Runner.py 7 7 2 l "$1" "$2"
}

export -f run_test

# Run 10 tests for each case in parallel (total of 20 tests)
echo "Going First"
seq 10 | xargs -n1 -P10 bash -c 'run_test "../src/checkers-python/main.py" "Sample_AIs/Average_AI/main.py"'

echo "Going Second"
seq 10 | xargs -n1 -P10 bash -c 'run_test "Sample_AIs/Average_AI/main.py" "../src/checkers-python/main.py"'

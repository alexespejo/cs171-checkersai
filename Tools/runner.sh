#!/bin/bash
echo "Going First"
for i in {1..2}
do
  python3 AI_Runner.py 8 8 3 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py 
done

echo "Going Second"
for i in {1..2}
do
  python3 AI_Runner.py 8 8 3 l Sample_AIs/Poor_AI/main.py ../src/checkers-python/main.py
done

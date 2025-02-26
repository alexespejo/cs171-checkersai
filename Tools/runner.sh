#!/bin/bash

for i in {1..5}
do
  python3 AI_Runner.py 8 8 3 l Sample_AIs/Random_AI/main.py ../src/checkers-python/main.py
done

for i in {1..5}
do
  python3 AI_Runner.py 8 8 3 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py 
done

import json
with open('tasks.json') as f:
    tasks = json.load(f)
print("Actual keys in first task:", tasks[0].keys())  # Should show 'reward'
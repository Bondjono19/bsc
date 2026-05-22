import random
random.seed(42)
v = [round(random.uniform(-1, 1), 4) for _ in range(512)]
print(v)
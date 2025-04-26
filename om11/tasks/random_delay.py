import time
import random

def random_delay(min_sec=1, max_sec=5):
    duration = random.uniform(min_sec, max_sec)
    time.sleep(duration)
    return f"Случайная пауза: {round(duration, 2)} сек."
import time

def wait_email(timeout=30):
    time.sleep(timeout)
    return f"Ожидание письма: {timeout} сек."
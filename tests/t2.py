import requests

BROWSERSTACK_USER = "sereernest@gmail.com"
BROWSERSTACK_KEY = "PoF4jrAZXDDUsX2WysDC"

response = requests.get(
    "https://api.browserstack.com/automate/plan.json",
    auth=(BROWSERSTACK_USER, BROWSERSTACK_KEY),
)
print(response.json())  # 'cdp' to be checked

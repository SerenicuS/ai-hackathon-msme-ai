import requests

# 1. Define the URL for the "Update Scores" button
url = "http://localhost:8000/update-scores"

print("🔘 Pushing the 'Update Scores' button...")

# 2. Send the POST request (Simulating the Web App)
try:
    response = requests.post(url)

    # 3. Print the reply from main.py
    print("✅ Response from Server:", response.json())

except Exception as e:
    print("❌ Failed to connect:", e)
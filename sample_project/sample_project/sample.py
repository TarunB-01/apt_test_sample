import requests
import time

# Define the target URL to scan
target_url = "https://chat.openai.com"

# Set up the ZAP API URL and API key
zap_api_url = "http://localhost:8080"
api_key = "adij1hlj96560r3cv31i1ejpd7"  # Replace "your_api_key" with your actual API key

# Start ZAP in daemon mode
requests.get(f"{zap_api_url}/JSON/core/action/newSession/?apikey={api_key}")

# Set up the scan policy (optional)
requests.get(f"{zap_api_url}/JSON/spider/action/setOptionDefaultPolicy/?zapapiformat=JSON&policy=Default+Policy&apikey={api_key}")

# Set the scope of the scan (optional)
requests.get(f"{zap_api_url}/JSON/context/action/includeInContext/?zapapiformat=JSON&contextName=default&regex=http://example.com/.*&apikey={api_key}")

# Initiating the spider scan
resp = requests.get(f"{zap_api_url}/JSON/spider/action/scan/?zapapiformat=JSON&url={target_url}&apikey={api_key}")
scan_id = resp.json()["scan"]

# Polling the status until the spider scan is complete
while True:
    resp = requests.get(f"{zap_api_url}/JSON/spider/view/status/?zapapiformat=JSON&scanId={scan_id}&apikey={api_key}")
    status = resp.json()["status"]
    if status == "100":
        print("Spider scan completed.")
        break
    print(f"Spider scan status: {status}")
    time.sleep(5)

# Initiating the active scan
resp = requests.get(f"{zap_api_url}/JSON/ascan/action/scan/?zapapiformat=JSON&url={target_url}&apikey={api_key}")
scan_id = resp.json()["scan"]

# Polling the status until the active scan is complete
while True:
    resp = requests.get(f"{zap_api_url}/JSON/ascan/view/status/?zapapiformat=JSON&scanId={scan_id}&apikey={api_key}")
    status = resp.json()["status"]
    if status == "100":
        print("Active scan completed.")
        break
    print(f"Active scan status: {status}")
    time.sleep(5)

# Retrieve the scan results
resp = requests.get(f"{zap_api_url}/OTHER/core/other/htmlreport/?apikey={api_key}")
with open("zap_report.html", "wb") as f:
    f.write(resp.content)

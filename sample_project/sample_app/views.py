from django.shortcuts import redirect, render
from django.http import JsonResponse
import requests
import os
import shutil
import requests
import time
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
import subprocess

# Create your views here.
def home(request):
    return render(request,'home.html')
def signup(request):
    return render(request,'signup.html')

def signin(request):
    return render(request,'signin.html')

def url(request):
    return render(request,'url.html')

def validate_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        try:
            response = requests.head(url)
            valid = response.status_code == 200  # Check if response status is OK (200)
            message = 'URL exists' if valid else 'URL does not exist'
        except Exception as e:
            valid = False
            message = str(e)

        return JsonResponse({'valid': valid, 'message': message})



def scan_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')

        if url:
            # Set up the ZAP API URL and API key
            zap_api_url = "http://localhost:8080"
            api_key = "adij1hlj96560r3cv31i1ejpd7"  # Replace "your_api_key" with your actual API key

            # Start ZAP in daemon mode (optional if ZAP is already running)
            requests.get(f"{zap_api_url}/JSON/core/action/newSession/?apikey={api_key}")

            # Initiating the spider scan
            resp = requests.get(f"{zap_api_url}/JSON/spider/action/scan/?zapapiformat=JSON&url={url}&apikey={api_key}")
            scan_id = resp.json()["scan"]

            # Polling the status until the spider scan is complete
            while True:
                resp = requests.get(f"{zap_api_url}/JSON/spider/view/status/?zapapiformat=JSON&scanId={scan_id}&apikey={api_key}")
                status = resp.json()["status"]
                if status == "100":
                    break
                time.sleep(5)

            # Initiating the active scan
            resp = requests.get(f"{zap_api_url}/JSON/ascan/action/scan/?zapapiformat=JSON&url={url}&apikey={api_key}")
            scan_id = resp.json()["scan"]

            # Polling the status until the active scan is complete
            while True:
                resp = requests.get(f"{zap_api_url}/JSON/ascan/view/status/?zapapiformat=JSON&scanId={scan_id}&apikey={api_key}")
                status = resp.json()["status"]
                if status == "100":
                    break
                time.sleep(5)

            # Retrieve the scan results
            try:
                resp = requests.get(f"{zap_api_url}/OTHER/core/other/htmlreport/?apikey={api_key}")
                report_file_path = os.path.join(settings.BASE_DIR, 'zap_report.html')
                with open(report_file_path, "wb") as f:
                    f.write(resp.content)
            except Exception as e:
                return render(request, 'error.html', {'error': str(e)})  # Render an error page in case of an exception

            # Return an HTML response with a link to download the report
            with open(report_file_path, "rb") as f:
                response = HttpResponse(f.read(), content_type='application/html')
                response['Content-Disposition'] = 'attachment; filename=zap_report.html'
                return response
        else:
            return HttpResponse("Please provide a URL for scanning.")
    else:
        return HttpResponse('Invalid request method.', status=405) # Return a 405 Method Not Allowed if the request method is not GET

import subprocess
from django.shortcuts import render
from django.http import HttpResponse

def nmap_scan(request):
    if request.method == 'POST':
        target = request.POST.get('url', '')
        if target:
            cleaned_target = target.replace("http://", "").replace("https://", "")
            try:
                # Run Nmap command
                result = subprocess.run(['nmap', '-Pn',cleaned_target], capture_output=True, text=True, timeout=300)
                scan_output = result.stdout
                return render(request, 'results.html', {'scan_output': scan_output})
            except subprocess.TimeoutExpired:
                return HttpResponse("Nmap scan timed out.")
            except subprocess.CalledProcessError as e:
                return HttpResponse(f"Nmap error: {e}")
        else:
            return HttpResponse("Please provide a target for scanning.")
    else:
        return render(request, 'url.html')




import os
import requests
from dotenv import load_dotenv
from urllib import parse
import base64
import time
import hashlib
import hmac
import json

load_dotenv()

UPWORK_PUBLIC_KEY = os.getenv("UPWORK_PUBLIC_KEY")
UPWORK_SECRET_KEY = os.getenv("UPWORK_SECRET_KEY")
UPWORK_API_URL = "https://www.upwork.com/api/v3"

def generate_oauth_signature(url, method, params, secret):
    """Generates OAuth signature."""
    base_string = f"{method.upper()}&{parse.quote(url, safe='')}&{parse.quote(parse.urlencode(sorted(params.items()), safe=''), safe='')}"
    key = f"{secret}&"
    hashed = hmac.new(key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    return base64.b64encode(hashed.digest()).decode('utf-8')

def get_oauth_headers(url, method, params, consumer_key, consumer_secret):
    """Generates OAuth headers."""
    oauth_params = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': str(int(time.time())),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0'
    }
    params.update(oauth_params)
    signature = generate_oauth_signature(url, method, params, consumer_secret)
    params['oauth_signature'] = signature
    auth_header = 'OAuth ' + ', '.join([f'{parse.quote(k)}="{parse.quote(v)}"' for k, v in params.items()])
    return {'Authorization': auth_header}

def get_access_token():
    """Gets the access token from Upwork API."""
    url = f"{UPWORK_API_URL}/auth/keys/token"
    method = "POST"
    params = {}

    headers = get_oauth_headers(url, method, params, UPWORK_PUBLIC_KEY, UPWORK_SECRET_KEY)

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

def search_jobs(query):
    """Searches jobs on Upwork based on the search query."""
    access_token = get_access_token()
    if not access_token:
        print("Failed to obtain access token.")
        return []

    url = f"{UPWORK_API_URL}/jobs/search"
    method = "GET"
    params = {'q': query}

    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('jobs', [])
    except requests.exceptions.RequestException as e:
        print(f"Error searching jobs: {e}")
        return []

def submit_proposal(job_id, cover_letter):
    """Submits a proposal to Upwork API."""
    access_token = get_access_token()
    if not access_token:
        print("Failed to obtain access token.")
        return False

    url = f"{UPWORK_API_URL}/jobs/{job_id}/apply"
    method = "POST"
    data = {'cover_letter': cover_letter}

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error submitting proposal: {e}")
        return False

if __name__ == '__main__':
    # Example usage
    # access_token = get_access_token()
    # if access_token:
    #     print(f"Access Token: {access_token}")

    jobs = search_jobs("Python developer")
    if jobs:
        print(f"Found {len(jobs)} jobs.")
        for job in jobs:
            print(f"Job Title: {job['title']}")

    # job_id = "YOUR_JOB_ID"  # Replace with a valid job ID
    # cover_letter = "This is a test cover letter."
    # if submit_proposal(job_id, cover_letter):
    #     print("Successfully submitted proposal.")
    # else:
    #     print("Failed to submit proposal.")
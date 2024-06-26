import requests
import csv
from datetime import datetime, timedelta

# Constants
ORG = "your_organization"  # Replace with your GitHub organization name
TOKEN = "your_personal_access_token"
DAYS = 30
OUTPUT_FILE = "prod_releases_report.csv"

# Calculate the date 30 days ago
since = (datetime.now() - timedelta(days=DAYS)).isoformat()

# Fetch repositories from the organization
def fetch_repositories(org, token):
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {"Authorization": f"token {token}"}
    repos = []
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

# Fetch workflow runs from a repository
def fetch_workflow_runs(repo, token, since):
    url = f"https://api.github.com/repos/{repo}/actions/runs"
    headers = {"Authorization": f"token {token}"}
    params = {"per_page": 100, "created": f">={since}"}
    runs = []
    page = 1
    while True:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data['workflow_runs']:
            break
        runs.extend(data['workflow_runs'])
        page += 1
    return runs

# Filter production releases
def filter_production_releases(runs):
    prod_releases = []
    for run in runs:
        if run['conclusion'] == 'success' and 'production' in run['name'].lower():
            prod_releases.append(run)
    return prod_releases

# Main function to generate the report
def generate_report(org, token, since):
    report = []
    repos = fetch_repositories(org, token)
    for repo in repos:
        repo_name = repo['full_name']
        runs = fetch_workflow_runs(repo_name, token, since)
        prod_releases = filter_production_releases(runs)
        for release in prod_releases:
            report.append({
                'repository': repo_name,
                'id': release['id'],
                'name': release['name'],
                'event': release['event'],
                'status': release['status'],
                'conclusion': release['conclusion'],
                'created_at': release['created_at'],
                'updated_at': release['updated_at']
            })
    return report

# Save the report to a CSV file
def save_report_to_csv(report, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'repository', 'id', 'name', 'event', 'status', 'conclusion', 'created_at', 'updated_at'
        ])
        writer.writeheader()
        writer.writerows(report)

# Generate the report
report = generate_report(ORG, TOKEN, since)

# Save the report to a CSV file
save_report_to_csv(report, OUTPUT_FILE)

print(f"Report saved to {OUTPUT_FILE}")

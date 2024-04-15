import os
import requests
import base64
import xmltodict
import json

ORG_NAME = "lokeshorg"

# Read GitHub token from environment variable
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# GitHub API endpoint for getting user repositories
REPOS_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"

# Make a GET request to fetch repositories with bearer token
headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
repo_response = requests.get(REPOS_URL, headers=headers)
repo_data = repo_response.json()

# Extract repository names
repo_names = [repo["name"] for repo in repo_data]

# Dictionary to store repository information
repository_info = {}

# Loop through each repository
for repo_name in repo_names:
    print("Repository:", repo_name)

    # GitHub API endpoint for getting mulebom/pom.xml content
    MULEBOM_URL = f"https://api.github.com/repos/{ORG_NAME}/{repo_name}/contents/mulebom/pom.xml"

    # Make GET request to fetch mulebom/pom.xml content with bearer token
    mulebom_pom_response = requests.get(MULEBOM_URL, headers=headers)

    # Check if the request was successful
    if mulebom_pom_response.status_code == 200:
        # Decode the content from base64 for mulebom/pom.xml
        mulebom_pom_content = base64.b64decode(mulebom_pom_response.json()['content']).decode('utf-8')

        # Convert XML to dictionary for mulebom/pom.xml
        mulebom_pom_dict = xmltodict.parse(mulebom_pom_content)

        # Extract dependencies
        dependencies = []
        dependency_management = mulebom_pom_dict.get('project', {}).get('dependencyManagement', {}).get('dependencies', {}).get('dependency', [])
        if not isinstance(dependency_management, list):
            dependency_management = [dependency_management]
        for dependency in dependency_management:
            dependency_name = dependency.get('artifactId')
            dependency_version = dependency.get('version')
            dependencies.append({"name": dependency_name, "version": dependency_version})

        # Extract properties
        properties = mulebom_pom_dict.get('project', {}).get('properties', {})
        
        # Replace version placeholders with actual versions in dependencies
        for dependency in dependencies:
            if dependency['version'] and dependency['version'].startswith("${") and dependency['version'].endswith("}"):
                version_key = dependency['version'][2:-1]
                dependency['version'] = properties.get(version_key)

        # Store repository information in the dictionary
        repository_info[repo_name] = dependencies
    else:
        print(f"mulebom/pom.xml not found for repository: {repo_name}")

# Print the combined repository information
print(json.dumps(repository_info, indent=4))

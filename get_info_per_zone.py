import requests
import os
import json

# Cloudflare API credentials
API_EMAIL = os.getenv("CLOUDFLARE_EMAIL")
API_KEY = os.getenv("CLOUDFLARE_API_KEY")
ACCOUNT_ID = "your_account_id" 

# Validate credentials
if not API_EMAIL or not API_KEY or not ACCOUNT_ID:
    print("Error: Missing Cloudflare API credentials or Account ID.")
    exit(1)

# Global variables to store the RULESET_ID and RULE_ID
RULESET_ID = None  # Placeholder for ruleset ID
RULE_ID = None  # Placeholder for rule ID

def get_domains():
    """Fetches all Zone IDs in the Cloudflare account."""
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "X-Auth-Email": API_EMAIL,
        "X-Auth-Key": API_KEY,
        "Content-Type": "application/json"
    }
    params = {"account.id": ACCOUNT_ID}  # Filter by account ID
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        domains = {zone["name"]: zone["id"] for zone in data.get("result", [])}
        return domains
    else:
        print(f"Failed to fetch domains. Status Code: {response.status_code}, Response: {response.text}")
        return None

def get_filtered_ruleset_ids(zone_id):
    """Fetches the RULESET_ID for a given Zone ID."""
    global RULESET_ID  # Use the global RULESET_ID
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    headers = {
        "X-Auth-Email": API_EMAIL,
        "X-Auth-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if data.get("success") and "result" in data:
            rulesets = data["result"]
            # Filter by both phase and name
            filtered_rulesets = [
                ruleset["id"] for ruleset in rulesets 
                if ruleset.get("phase") == "http_request_firewall_managed" and ruleset.get("name") == "default"
            ]

            if filtered_rulesets:
                # Save the first ruleset ID to RULESET_ID (global variable)
                RULESET_ID = filtered_rulesets[0]
                return RULESET_ID
            else:
                print(f"No rulesets found for phase: http_request_firewall_managed and name: default in zone {zone_id}.")
                return None
        else:
            print("Failed to fetch rulesets. Response:", json.dumps(data, indent=2))
    elif response.status_code == 404:
        print(f"Error: The specified zone ID {zone_id} was not found. Double-check the Zone ID.")
    elif response.status_code == 401:
        print("Error: Unauthorized. Please check your API credentials.")
    else:
        print(f"Failed to fetch rulesets. Status Code: {response.status_code}, Response: {response.text}")

    return None

def get_rule_id(zone_id):
    """Fetches the RULE_ID for a given Zone ID and RULESET_ID."""
    global RULE_ID  # Use the global RULE_ID
    
    if not RULESET_ID:
        print("Error: RULESET_ID is not set. Please run the get_filtered_ruleset_ids function first.")
        return None
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{RULESET_ID}"
    headers = {
        "X-Auth-Email": API_EMAIL,
        "X-Auth-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if data.get("success") and "result" in data:
            rules = data["result"].get("rules", [])

            if rules:
                RULE_ID = rules[0]["id"]  # Get the first rule ID
                return RULE_ID
            else:
                print(f"No rules found in the ruleset for zone {zone_id}.")
                return None
        else:
            print("Failed to fetch rules. Response:", json.dumps(data, indent=2))
    else:
        print(f"Failed to fetch rules. Status Code: {response.status_code}, Response: {response.text}")

    return None

def save_zone_info(domain_info):
    """Saves domain information (Zone ID, Ruleset ID, and Rule ID) to a JSON file."""
    try:
        # Check if the file exists
        if os.path.exists("domain_info.json"):
            with open("domain_info.json", "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # Append the new domain information
        existing_data.append(domain_info)

        # Save the updated data to the file
        with open("domain_info.json", "w") as file:
            json.dump(existing_data, file, indent=4)
        print("Domain information saved to 'domain_info.json'.")
    except Exception as e:
        print(f"Error saving domain information: {e}")

if __name__ == "__main__":
    # Fetch the domains from Cloudflare
    domains = get_domains()
    if domains:
        print("\nDomains in your Cloudflare account:")
        for domain_name, zone_id in domains.items():
            print(f"\nDomain: {domain_name} | Zone ID: {zone_id}")
            
            # Fetch the RULESET_ID for each domain
            RULESET_ID = get_filtered_ruleset_ids(zone_id)
            
            if RULESET_ID:
                # Fetch the RULE_ID for each domain's RULESET_ID
                RULE_ID = get_rule_id(zone_id)
                
                if RULE_ID:
                    print(f"Ruleset ID for domain {domain_name}: {RULESET_ID}")
                    print(f"Rule ID for domain {domain_name}: {RULE_ID}")
                    
                    # Prepare domain info to save
                    domain_info = {
                        "domain_name": domain_name,
                        "zone_id": zone_id,  # The Zone ID is directly here
                        "ruleset_id": RULESET_ID,
                        "rule_id": RULE_ID
                    }

                    # Save the domain info to a JSON file
                    save_zone_info(domain_info)

                else:
                    print(f"Failed to retrieve Rule ID for domain {domain_name}")
            else:
                print(f"Failed to retrieve Ruleset ID for domain {domain_name}") 

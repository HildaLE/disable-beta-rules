import requests
import os
import json

# Cloudflare details
managed_ruleset_id = "efb7b8c949ac4650a09736fc376e9aee" #cloudflare managed ruleset id
api_email = os.getenv("CLOUDFLARE_EMAIL")  # Your Cloudflare email
api_key = os.getenv("CLOUDFLARE_API_KEY")  # Your Cloudflare API key

def fetch_ruleset(zone_id):
    # Cloudflare API URL to fetch the ruleset
    base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{managed_ruleset_id}"

    # Prepare headers
    headers = {
        "X-Auth-Email": api_email,
        "X-Auth-Key": api_key,
    }

    # Fetch the current ruleset
    try:
        print("Fetching current ruleset...")
        response = requests.get(base_url, headers=headers)
        print("Request URL:", base_url)
        print("Request Headers:", headers)

        # Check if the request was successful
        if response.status_code == 200:
            print("Ruleset fetched successfully.")
            ruleset_data = response.json()  # Fetch the JSON response
            append_to_file(ruleset_data)  # Append data to file
        else:
            print(f"Error fetching ruleset: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def append_to_file(ruleset_data):
    try:
        # Open rules.json file and append the new ruleset data
        with open("rules.json", "a") as file:
            json.dump(ruleset_data, file, indent=4)  # Write data with indentation
            file.write("\n")  # Ensure new data is on a new line
        print("Ruleset appended to rules.json successfully.")
    except Exception as e:
        print(f"Error writing to file: {e}")

def clean_file(file_path):
    # Read the file content
    with open(file_path, "r") as file:
        data = file.read()

    # Step 1: Locate and keep only the "rules" array
    rules_start_index = data.find('"rules": ')
    if rules_start_index != -1:
        # Retain everything after "rules": [
        data = data[rules_start_index + len('"rules": '):]

    # Step 2: Remove extra content after the closing `]`
    rules_end_index = data.rfind(']')
    if rules_end_index != -1:
        # Keep everything up to the closing bracket `]`
        data = data[:rules_end_index + 1].strip()

    # Step 3: Remove everything after and including `{ "result":`
    result_index = data.find('"source":')
    if result_index != -1:
        # Keep everything before `{ "result":`
        data = data[:result_index].strip()

    # Find the last closing square bracket `]` and remove the trailing comma if it exists
    trailing_comma_index = data.rfind("],")
    if trailing_comma_index != -1:
        # Replace "]," with "]" at the last occurrence
        data = data[:trailing_comma_index] + "]" + data[trailing_comma_index + 2:]


    # Step 4: Write the cleaned data back to the file
    with open(file_path, "w") as file:
        file.write(data)

    print(f"File '{file_path}' has been cleaned successfully.")


def extract_beta_ids(file_path, output_file):
    # Read the file content
    try:
        # Read the file content
        with open(file_path, "r") as file:
            # Print the content of the file
            file_content = file.read()
            #print(f"Contents of '{file_path}':\n{file_content}")

            # Parse the JSON data from the file
            rules = json.loads(file_content)
    except json.JSONDecodeError as e:
        print("Error: The data is not in valid JSON format.")
        return
    except FileNotFoundError as e:
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Step 1: Extract the "id" from all rules where "categories" contains "beta"
    beta_ids = []
    for rule in rules:
        if "beta" in rule.get("categories", []):  # Check if 'beta' is in the categories list
            beta_ids.append(rule.get("id"))  # Append the id to the list

    # Step 2: Print and save the IDs to a text file
    if beta_ids:
        print("IDs of rules with 'beta' in categories:")
        print(beta_ids)

        # Write the list of IDs to the output file
        with open(output_file, "a") as output:
            json.dump(beta_ids, output)
            output.write("\n")  # Separate entries with newline
        print(f"IDs have been written to {output_file}")
    else:
        print("No rules with 'beta' in categories were found.")

def disable_rules(input_file, zone_id, ruleset_id, rule_id):
    # Read the rule IDs from the text file
    try:
        with open(input_file, "r") as file:
            # Read the content of the file and load it as a Python list
            rule_ids_to_disable = json.loads(file.read().strip())
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' does not exist.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: The file content is not in valid JSON format.")
        exit(1)

    # Check if the rule_ids_to_disable list is populated
    if not rule_ids_to_disable:
        print("Error: No rule IDs found in the file.")
        exit(1)

    # Cloudflare API URL for the rule update
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}/rules/{rule_id}"

    # Create the overrides payload dynamically from the list
    overrides_rules = [{"id": rule_id, "enabled": False} for rule_id in rule_ids_to_disable]

    # The payload for the PATCH request
    payload = {
        "action": "execute",
        "description": "",
        "enabled": True,
        "expression": "true",
        "id": rule_id,
        "action_parameters": {
            "id": managed_ruleset_id,
            "overrides": {
                "rules": overrides_rules
            }
        }
    }

    # Headers for the request
    headers = {
        "X-Auth-Email": api_email,
        "X-Auth-Key": api_key,
        "Content-Type": "application/json"
    }

    # Make the PATCH request
    response = requests.patch(url, headers=headers, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Rules updated successfully.")
    else:
        print(f"Failed to update rules. Status Code: {response.status_code}, Response: {response.text}")


def process_domain_info(zone_id, ruleset_id, rule_id):
    # Call the functions you already have here with zone_id, ruleset_id, and rule_id
    fetch_ruleset(zone_id)  # Fetch and append the current ruleset to file
    clean_file("rules.json")  # Clean the rules.json file
    extract_beta_ids("rules.json", "beta_ids.txt")  # Extract beta rule IDs
    disable_rules("beta_ids.txt", zone_id, ruleset_id, rule_id)  # Disable the extracted rules


def main():
    # Load the domain info from domain_info.json
    try:
        with open('domain_info.json', 'r') as file:
            domain_data = json.load(file)
        
        # Process each domain's info
        for domain in domain_data:
            domain_name = domain.get('domain_name')
            zone_id = domain.get('zone_id')
            ruleset_id = domain.get('ruleset_id')
            rule_id = domain.get('rule_id')
            
            # Print domain info (optional)
            print(f"Domain: {domain_name} | Zone ID: {zone_id} | Ruleset ID: {ruleset_id} | Rule ID: {rule_id}")
            
            # Now call the function you have already written with the required parameters
            process_domain_info(zone_id, ruleset_id, rule_id)
    
    except FileNotFoundError:
        print("Error: 'domain_info.json' file not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from 'domain_info.json'.")


# Main execution
if __name__ == "__main__":
    main()

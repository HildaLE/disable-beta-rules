# Cloudflare Ruleset Management Script

## Overview
This script provides functionality to interact with Cloudflare's API for managing rulesets. It performs tasks such as:
1. Fetching the current ruleset from Cloudflare and appending it to a local file.
2. Cleaning the local ruleset file by retaining only necessary data.
3. Extracting rule IDs that belong to the "beta" category.
4. Disabling specific rules in the Cloudflare ruleset based on the extracted rule IDs.

## Requirements
- Python 3.x
- Cloudflare API credentials:
  - Cloudflare email (`CLOUDFLARE_EMAIL`)
  - Cloudflare API key (`CLOUDFLARE_API_KEY`)
- Requests library (`pip install requests`)

## Configuration
Before running the script, you need to set the following configuration variables:
1. `zone_id`: Your Cloudflare zone ID (found in the Cloudflare dashboard).
2. `managed_ruleset_id`: The Cloudflare managed ruleset ID (usually provided by Cloudflare).
3. `ruleset_id`: The specific ruleset ID that you wish to manage.
4. `rule_id`: The rule ID that you are targeting for update operations (e.g., disabling specific rules).
5. `CLOUDFLARE_EMAIL` and `CLOUDFLARE_API_KEY`: Your Cloudflare API credentials, set as environment variables for secure access.
Find ruleset_id and rule_id in the dashboard Security > WAF > Managed Rules.
Edit Cloudflare Managed Ruleset.
Down below click on "Save with API call".
You'll see the following call :
curl -X PATCH \ 
  "https://api.cloudflare.com/client/v4/zones/zone_id/rulesets/ruleset_id/rules/rule_id" \

You can set the `CLOUDFLARE_EMAIL` and `CLOUDFLARE_API_KEY` environment variables using the following commands in your terminal:
```bash
export CLOUDFLARE_EMAIL="your_email@example.com"
export CLOUDFLARE_API_KEY="your_api_key"
```

## Script Functions

### `fetch_ruleset()`
This function retrieves the current ruleset from the Cloudflare API and appends it to the `rules.json` file.

### `append_to_file(ruleset_data)`
This helper function writes the fetched ruleset data into the `rules.json` file, appending it to the existing content.

### `clean_file(file_path)`
This function cleans the `rules.json` file by:
1. Extracting and retaining only the "rules" section.
2. Removing extra content after the rules section.
3. Removing unnecessary data after the rule entries.
4. Writing the cleaned data back to the file.

### `extract_beta_ids(file_path, output_file)`
This function extracts the rule IDs from the `rules.json` file where the "categories" field contains the value "beta". It saves these extracted IDs to the `beta_ids.txt` file.

### `disable_rules(input_file)`
This function reads the rule IDs from the `beta_ids.txt` file, constructs a payload, and sends a PATCH request to the Cloudflare API to disable the listed rules in the specified ruleset.

## Usage

1. **Fetch and store the current ruleset**:  
   The script begins by calling the `fetch_ruleset()` function, which retrieves the current ruleset and saves it to the `rules.json` file.

2. **Clean the ruleset file**:  
   After fetching the ruleset, the script calls `clean_file()` to sanitize the data, keeping only the relevant rule information.

3. **Extract beta rule IDs**:  
   The script then extracts the rule IDs categorized as "beta" from the cleaned `rules.json` file and saves them to `beta_ids.txt`.

4. **Disable the extracted rules**:  
   Finally, the script disables the rules identified as "beta" by sending a PATCH request to Cloudflare using the extracted rule IDs.

### Example Execution

To run the script, execute the following command:

```bash
python3 script.py
```

## Notes
- Ensure that the Cloudflare API credentials are valid and that the appropriate permissions are granted for the operations.
- The `rules.json` and `beta_ids.txt` files will be generated in the same directory where the script is located.
- If no rules with "beta" in the categories are found, the script will notify you accordingly.

## Troubleshooting
- **API Errors**: If there are issues with the API requests (e.g., incorrect credentials or rate limits), check the response status code and message for more details.
- **File Issues**: If the `rules.json` file is missing or not in a valid JSON format, ensure the file is generated correctly or provide a valid input file.

## License
This script is provided under the MIT License. You are free to modify, distribute, and use it for your purposes. However, it is provided as-is without any warranty.
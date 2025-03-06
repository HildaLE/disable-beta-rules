# Cloudflare Beta Rule Disabler

This repository contains two Python scripts to interact with Cloudflare's API. The scripts fetch domain-related information, extract ruleset details, and disable specific beta rules in Cloudflare-managed firewall rulesets.

## Prerequisites
- Python 3.x
- Cloudflare API credentials
- Required environment variables:
  - `CLOUDFLARE_EMAIL`: Your Cloudflare account email
  - `CLOUDFLARE_API_KEY`: Your Cloudflare API key

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Install dependencies (if required):
   ```sh
   pip install requests
   ```

## Usage
### Step 1: Fetch Cloudflare Zone Information
Run the first script to collect Cloudflare zone, ruleset, and rule IDs:
```sh
python3 get_info_per_zone.py
```
This script:
- Fetches all domains and their Zone IDs from your Cloudflare account.
- Retrieves the Ruleset ID and Rule ID for each domain.
- Saves this information in `domain_info.json`.

### Step 2: Disable Beta Rules
Run the second script to process and disable beta rules:
```sh
python3 disable_beta_rules.py
```
This script:
- Fetches the ruleset for each domain.
- Extracts and saves beta rule IDs.
- Sends a request to disable the extracted beta rules.

## Files
- `get_info_per_zonr.py` – Fetches Cloudflare zone, ruleset, and rule IDs.
- `disable_beta_rules.py` – Disables beta rules in Cloudflare-managed rulesets.
- `domain_info.json` – Stores fetched domain details.
- `rules.json` – Stores retrieved ruleset details.
- `beta_ids.txt` – Contains extracted beta rule IDs.

## Notes
- Ensure Cloudflare API credentials are set as environment variables before running the scripts.
- The `domain_info.json` file must exist before running `disable_beta_rules.py`.



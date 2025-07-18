#!/usr/bin/env bash

# This script is safely loading and applying DEV config values and secrets from a Bitwarden storage.
# It is NOT intended to be invoked on cloud - for cloud runs use cloud-native env-injection solutions.
# If you need to override some values, use .env.local alongside and DO NOT commit it.
# For more info on env variables being loaded see .env.example or shallwe/dev Bitwarden vault.

# --------- Check dependencies ---------
echo "🔐 Checking script dependencies..."

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "❌ jq is not installed. Please install it: https://stedolan.github.io/jq/"
  exit 1
fi

# Check if Bitwarden CLI is installed
if ! command -v bw &> /dev/null; then
  echo "❌ Bitwarden CLI (bw) not found. Please install it: https://bitwarden.com/help/cli/"
  exit 1
fi


# --------- Check for login and unlock ---------
echo "🔐 Checking Bitwarden session..."

# Loop until Bitwarden is unlocked
while true; do
  status=$(bw status | jq -r '.status')

  # Break out if unlocked
  if [[ "$status" == "unlocked" ]]; then
    break

  # Try logging in if not
  elif [[ "$status" == "unauthenticated" ]]; then
    echo "🔑 Bitwarden not logged in. Logging in now..."
    bw login
    continue

  # Try unlocking if not
  elif [[ "$status" == "locked" ]]; then
    echo "🔓 Vault is locked. Unlocking..."
    if ! BW_SESSION=$(bw unlock --raw); then
      echo "❌ Unlock failed or cancelled. Will retry..."
      sleep 1
      continue
    fi
    export BW_SESSION
  fi

  sleep 2
done

echo "🔄 Syncing Bitwarden vault to pick up any renames or new items..."
bw sync

echo "✅ Bitwarden unlocked and session ready."


# -------- Load config values from Bitwarden ---------
echo "📦 Fetching dev config from Bitwarden..."

# Make temporary file for .env generation
TMP=".env.tmp"
: > "$TMP"
echo "# Generated .env by load_dev_env_from_bw.sh — DO NOT COMMIT" >> "$TMP"

# Fetch from Bitwarden
bw get item shallwe/dev --raw \
  | jq -r '.fields[]
      | if .value == null
        then "\(.name)="
        else "\(.name)=\(.value)"
      end' \
  >> "$TMP"

# Load manual overrides if present
if [[ -f .env.local ]]; then
  echo "📄 Applying manual overrides from .env.local"

  # Read overrides into an associative array
  declare -A overrides
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    overrides["$key"]="$value"
  done < <(grep -vE '^\s*#|^\s*$' .env.local)

  # Create new TMP file with in-place replacements
  TMP_REPLACED="$TMP.replaced"
  : > "$TMP_REPLACED"

  while IFS= read -r line; do
    key="${line%%=*}"
    if [[ -n "${overrides[$key]+_}" ]]; then
      echo "$key=${overrides[$key]}" >> "$TMP_REPLACED"
      unset "overrides[$key]"  # Mark as handled
    else
      echo "$line" >> "$TMP_REPLACED"
    fi
  done < "$TMP"

  # Add any remaining overrides that weren’t in original Bitwarden list
  for remaining_key in "${!overrides[@]}"; do
    echo "$remaining_key=${overrides[$remaining_key]}" >> "$TMP_REPLACED"
  done

  mv "$TMP_REPLACED" "$TMP"
fi

# Populate the actual .env file
mv "$TMP" .env


# -------- Apply immediately if possible ---------
# If autoenv is present - try applying
if command -v autoenv_init > /dev/null; then
  if [[ -f .env ]]; then
    echo "📦 Detected .env file, triggering autoenv by re-entering directory...."
    cd .
  else
    echo "⚠️ Autoenv detected but no .env file found."
  fi

# No autoenv – try sourcing .env manually
else
  if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "🪄 Applying .env variables to current shell..."
    echo "Hint: install autoenv to automate this step."
    set -a
    source .env 2>/dev/null && echo "✅ .env loaded." || echo "⚠️ No .env file found."
    set +a
  else
    echo "ℹ️  .env updated. To apply changes: run 'source .env'"
  fi
fi
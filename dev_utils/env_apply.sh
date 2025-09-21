#!/usr/bin/env bash


apply_env_file() {
    # If autoenv is present - try triggering
    if command -v autoenv_init > /dev/null; then
        if [[ -f .env ]]; then
            echo "📦 Detected .env file, triggering autoenv by re-entering directory..."
            cd .
        else
            echo "⚠️ Autoenv detected but no .env file found."
        fi
    else
        # No autoenv – try sourcing manually
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
}

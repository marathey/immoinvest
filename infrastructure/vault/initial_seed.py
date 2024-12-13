import os
import hvac
import yaml
import sys
from getpass import getpass

def load_structure():
    with open('config/vault-structure.yaml', 'r') as file:
        return yaml.safe_load(file)

def init_vault_secrets():
    # Get Vault connection details from environment variables
    vault_addr = os.environ.get('VAULT_ADDR', 'http://localhost:8200') 
    if not vault_addr:
        raise ValueError("VAULT_ADDR environment variable must be set")

    # Prompt for root token securely
    vault_token = getpass("Enter Vault root token: ")
    
    client = hvac.Client(
        url=vault_addr,
        token=vault_token
    )
    
    structure = load_structure()
    
    try:
        # Enable KV engine (if not already enabled)
        try:
            client.sys.enable_secrets_engine(
                backend_type='kv',
                path='secret',
                options={'version': 2}
            )
        except hvac.exceptions.InvalidRequest as e:
            if 'path is already in use' not in str(e):
                raise

        # For each secret path in the structure
        for path, config in structure['secrets'].items():
            secrets = {}
            print(f"\nConfiguring secrets for {path}:")
            
            # Prompt for each required value
            for key in config['required_keys']:
                value = getpass(f"Enter value for {key}: ")
                secrets[key] = value
            
            # Store in Vault
            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secrets,
                mount_point='secret'
            )

        print("\nVault secrets initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing Vault secrets: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_vault_secrets()
import base64
import nacl.encoding
import nacl.public
import requests
from typing import Dict
from dotenv import load_dotenv
import os
import getpass

load_dotenv()

def get_public_key(owner: str, repo: str, token: str) -> Dict[str, str]:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    print(f"Sending request for {owner}/{repo} public key")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def encrypt_secret(public_key: str, secret_value: str) -> str:
    public_key_bytes = base64.b64decode(public_key)
    sealed_box = nacl.public.SealedBox(nacl.public.PublicKey(public_key_bytes))
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def add_secret(owner: str, repo: str, token: str, secret_name: str, encrypted_value: str, key_id: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{secret_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    print(f"Sending request to add {secret_name} to {owner}/{repo}")
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Secret '{secret_name}' added successfully.")

def list_secrets(owner: str, repo: str, token: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    print(f"Sending request to list secrets for {owner}/{repo}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    secrets = response.json().get('secrets', [])
    if secrets:
        print("Repository secrets:")
        for secret in secrets:
            print(f"- {secret['name']}")
    else:
        print("No secrets found.")

def get_input(prompt: str, env_var: str) -> str:
    env_value = os.getenv(env_var)
    value = input(f"{prompt} (leave blank to use value from .env: {env_value}): ")
    return value if value else env_value

def get_token_input(prompt: str, env_var: str) -> str:
    env_value = os.getenv(env_var)
    value = getpass.getpass(f"{prompt} (leave blank to use value from .env): ")
    return value if value else env_value

def main() -> None:
    action = input("Choose an action (add/list): ").strip().lower()
    owner = get_input("Enter the repository owner", "REPO_OWNER")
    repo = get_input("Enter the repository name", "REPO_NAME")
    token = get_token_input("Enter your GitHub token", "GITHUB_TOKEN")

    if action == "add":
        secret_name = get_input("Enter the name of the secret", "SECRET_NAME")
        secret_value = get_input("Enter the secret value", "SECRET_VALUE")

        public_key_data = get_public_key(owner, repo, token)
        public_key = public_key_data['key']
        key_id = public_key_data['key_id']

        encrypted_secret = encrypt_secret(public_key, secret_value)

        print(f"Encrypted value: {encrypted_secret}")
        print(f"Key ID: {key_id}")

        add_secret(owner, repo, token, secret_name, encrypted_secret, key_id)
    elif action == "list":
        list_secrets(owner, repo, token)
    else:
        print("Invalid action. Please choose 'add' or 'list'.")

if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv

def check_oauth_setup():
    load_dotenv()
    
    print("Checking GitHub OAuth Setup...")
    print("=" * 40)
    
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if client_id:
        print(f"GITHUB_CLIENT_ID: {client_id[:10]}...")
    else:
        print("GITHUB_CLIENT_ID: Missing")
    
    if client_secret:
        print(f"GITHUB_CLIENT_SECRET: {client_secret[:10]}...")
    else:
        print("GITHUB_CLIENT_SECRET: Missing")
    
    if gemini_key:
        print(f"GEMINI_API_KEY: {gemini_key[:10]}...")
    else:
        print("GEMINI_API_KEY: Missing")
    
    print("=" * 40)
    
    if client_id and client_secret and gemini_key:
        print("All credentials configured!")
        print("You can now run: python main.py")
        return True
    else:
        print("Please add missing credentials to .env file")
        print("See SETUP.md for instructions")
        return False

if __name__ == "__main__":
    check_oauth_setup()

import requests
import json
import uuid
import logging
import sys

logging.basicConfig(
    filename='cli_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def chat():
    # Use a unique session ID for this terminal session
    session_id = str(uuid.uuid4())[:8]
    print(f"--- Scheduling Assistant CLI (Session: {session_id}) ---")
    print("Type 'quit' or 'exit' to stop.\n")
    
    url = "http://localhost:8001/chat"
    
    # If arguments are provided, use them as input
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        if user_input.lower() in ['quit', 'exit']:
            return
            
        payload = {
            "message": user_input,
            "session_id": session_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Slot Bot: {data.get('message')}")
            else:
                logging.error(f"API Error {response.status_code}: {response.text}")
                print(f"Slot Bot: Server returned an error ({response.status_code}). Check logs for details.")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection Error: {e}")
            print(f"Slot Bot: Connection failed. Please ensure the backend server is running at {url}.")
        except Exception as e:
            logging.error(f"Unexpected Error: {e}", exc_info=True)
            print("Slot Bot: An unexpected error occurred. Check logs for details.")
        return
    
    # Otherwise, run interactively
    while True:
        try:
            user_input = input("User: ")
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
            
        if user_input.lower() in ['quit', 'exit']:
            break
            
        payload = {
            "message": user_input,
            "session_id": session_id
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Slot Bot: {data.get('message')}")
            else:
                logging.error(f"API Error {response.status_code}: {response.text}")
                print(f"Slot Bot: Server returned an error ({response.status_code}). Check logs for details.")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection Error: {e}")
            print(f"Slot Bot: Connection failed. Please ensure the backend server is running at {url}.")
        except Exception as e:
            logging.error(f"Unexpected Error: {e}", exc_info=True)
            print("Slot Bot: An unexpected error occurred. Check logs for details.")

if __name__ == "__main__":
    chat()

"""
CLI Chat Interface for Career Companion
"""
import asyncio
import requests
import json
from datetime import datetime
import sys

API_BASE = "http://localhost:8000"
session_id = None


def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("🎓 CAREER COMPANION - AI Placement Officer")
    print("="*60)
    print("Ask me about placements, interviews, skills, or career advice!")
    print("Type 'quit' or 'exit' to end the conversation.\n")


def print_message(role: str, content: str, domain: str = None):
    """Print formatted message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if role == "user":
        print(f"\n[{timestamp}] You:")
        print(f"  {content}")
    else:
        domain_str = f" [{domain}]" if domain else ""
        print(f"\n[{timestamp}] Career Companion{domain_str}:")
        print(f"  {content}")


def print_suggested_actions(actions: list):
    """Print suggested actions"""
    if actions:
        print("\n💡 Suggested actions:")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")


def send_message(message: str) -> dict:
    """Send message to API"""
    global session_id
    
    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={
                "message": message,
                "session_id": session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            return data
        else:
            return {
                "error": f"API error: {response.status_code}",
                "response": "Sorry, I encountered an error. Please try again."
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "Connection error",
            "response": "Could not connect to the server. Make sure the backend is running on http://localhost:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Timeout",
            "response": "Request timed out. Please try again."
        }
    except Exception as e:
        return {
            "error": str(e),
            "response": "An unexpected error occurred."
        }


def main():
    """Main CLI loop"""
    print_header()
    
    # Check server health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: Server health check failed")
    except:
        print("⚠️  Warning: Could not connect to server at http://localhost:8000")
        print("    Make sure the backend is running: python backend/main.py\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\n📝 You: ").strip()
            
            if not user_input:
                continue
            
            # Check for quit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n👋 Thank you for using Career Companion!")
                print("    Good luck with your placements! 🚀\n")
                break
            
            # Special commands
            if user_input.lower() == 'history':
                if session_id:
                    response = requests.get(f"{API_BASE}/api/session/{session_id}/history")
                    if response.status_code == 200:
                        history = response.json()
                        print(f"\n📜 Conversation History ({len(history['messages'])} messages):")
                        for msg in history['messages']:
                            role = "You" if msg['role'] == 'user' else "Assistant"
                            print(f"\n{role}: {msg['content'][:100]}...")
                    else:
                        print("No history available.")
                else:
                    print("No active session.")
                continue
            
            if user_input.lower() == 'clear':
                print("\033[2J\033[H")  # Clear screen
                print_header()
                continue
            
            # Send message
            print("\n⏳ Thinking...")
            result = send_message(user_input)
            
            # Print response
            domain = result.get("domain")
            domain_str = domain.replace("_", " ").title() if domain else None
            
            print_message("assistant", result["response"], domain_str)
            
            # Print suggested actions
            if result.get("suggested_actions"):
                print_suggested_actions(result["suggested_actions"])
            
            # Print sources if available
            if result.get("sources"):
                print(f"\n📚 Sources: {', '.join(result['sources'])}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Good luck with your placements! 🚀\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

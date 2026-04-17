import sys
import os
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.getcwd())

load_dotenv()

from core.agent import run_agent_workflow

def chat():
    print("=" * 60)
    print("B2B Supply Chain AI Agent - Chat Interface")
    print("Simulation Mode: Acting as Retailer (+919900000001)")
    print("=" * 60)
    print("Type 'exit' to quit.")
    
    phone_number = "+919900000001"
    
    while True:
        user_input = input("\nYou (WhatsApp): ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
            
        print("\nAgent is thinking...")
        
        try:
            response = run_agent_workflow(phone_number, user_input)
            print(f"\nAgent (WhatsApp): {response}")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    chat()

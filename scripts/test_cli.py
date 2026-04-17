import json
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.find_nearest_item import find_nearest_item
from tools.inventory_tools import search_wholesale_inventory
from tools.place_regular_order import place_regular_order
from tools.update_inventory import update_inventory
from core.state import get_current_retailer_number, set_current_retailer_number


def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def extract_item_intent(text: str) -> str:
    """
    Extracts the requested item from common natural language patterns.
    Matches: 'I want eggs', 'Need rice', 'eggs', 'restock milk'
    """
    text = text.lower().strip()
    patterns = [
        r"i want (.*)",
        r"need (.*)",
        r"restock (.*)",
        r"buy (.*)",
        r"search for (.*)",
        r"get me (.*)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Default: treat the whole text as the item name if no keywords found
    return text


def chatbot_cli():
    print("=" * 60)
    print("B2B Supply Chain Tool Tester")
    print("Talk to the tools like a chatbot")
    print("=" * 60)
    print(f"Current Retailer Identity: {get_current_retailer_number()}")

    while True:
        print("\nChoose an action:")
        print("1. Find nearest item (Manual Location)")
        print("2. Find nearest item (Automatic Intent-based)")
        print("3. Place regular order")
        print("4. Update inventory")
        print("5. Exit")

        choice = input("\nYou: ").strip()

        if choice == "1":
            print("\nBot: Okay, tell me the item name.")
            item_name = input("You: ").strip()

            print("\nBot: Enter retailer latitude.")
            try:
                latitude = float(input("You: ").strip())
                print("Bot: Enter retailer longitude.")
                longitude = float(input("You: ").strip())

                result = find_nearest_item(
                    item_name=item_name,
                    retailer_location={
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )

                print("\nBot: Based on manual location, here are the best options:")
                print_json(result)
            except ValueError:
                print("\nBot: Invalid coordinates. Please try again.")

        elif choice == "2":
            print("\nBot: I'll find the best deals within 100km using your profile location.")
            print("Bot: What would you like to buy? (e.g., 'I want eggs', 'Need rice')")
            
            user_input = input("You: ").strip()
            item_name = extract_item_intent(user_input)
            
            if not item_name:
                print("\nBot: I couldn't identify the item. Please try again.")
                continue

            print(f"\nBot: Searching for '{item_name}' instantly...")
            
            # TRIGGER TOOL IMMEDIATELY
            result = search_wholesale_inventory(requested_item=item_name)

            if "error" in result:
                print(f"\nBot: Error: {result['error']}")
            else:
                print("\nBot: Based on your current location, here are the best options:")
                print_json(result.get("results", []))

        elif choice == "3":
            print("\nBot: Enter retailer phone number.")
            retailer_num = input("You: ").strip()

            print("\nBot: How many categories of items do you want to order?")
            try:
                n = int(input("You: ").strip())

                item_list = []
                for i in range(n):
                    print(f"\nBot: Enter item {i+1} name.")
                    item_name = input("You: ").strip()

                    print(f"Bot: Enter quantity for {item_name}.")
                    quantity = int(input("You: ").strip())

                    item_list.append({
                        "item_name": item_name,
                        "quantity": quantity
                    })

                result = place_regular_order(
                    retailer_number=retailer_num,
                    item_list=item_list
                )

                print("\nBot: Order result:")
                print_json(result)
            except ValueError:
                print("\nBot: Invalid input. Please try again.")

        elif choice == "4":
            print("\nBot: Enter wholesaler phone number.")
            wholesaler_number = input("You: ").strip()

            print("\nBot: Enter item name.")
            item_name = input("You: ").strip()

            try:
                print("\nBot: Enter quantity.")
                quantity = int(input("You: ").strip())

                print("\nBot: Enter price.")
                price = float(input("You: ").strip())

                result = update_inventory(
                    wholesaler_number=wholesaler_number,
                    item_name=item_name,
                    quantity=quantity,
                    price=price,
                )

                print("\nBot: Inventory update result:")
                print_json(result)
            except ValueError:
                print("\nBot: Invalid numbers. Please try again.")

        elif choice == "5":
            print("\nBot: Exiting. Bye.")
            break

        else:
            print("\nBot: Invalid choice. Please try again.")


if __name__ == "__main__":
    chatbot_cli()
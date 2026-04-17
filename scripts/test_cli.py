import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.find_nearest_item import find_nearest_item
from tools.place_regular_order import place_regular_order
from tools.update_inventory import update_inventory


def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def chatbot_cli():
    print("=" * 60)
    print("B2B Supply Chain Tool Tester")
    print("Talk to the tools like a chatbot")
    print("=" * 60)

    while True:
        print("\nChoose an action:")
        print("1. Find nearest item")
        print("2. Place regular order")
        print("3. Update inventory")
        print("4. Exit")

        choice = input("\nYou: ").strip()

        if choice == "1":
            print("\nBot: Okay, tell me the item name.")
            item_name = input("You: ").strip()

            print("\nBot: Enter retailer latitude.")
            latitude = float(input("You: ").strip())

            print("\nBot: Enter retailer longitude.")
            longitude = float(input("You: ").strip())

            result = find_nearest_item(
                item_name=item_name,
                retailer_location={
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )

            print("\nBot: Here are the best nearby options:")
            print_json(result)

        elif choice == "2":
            print("\nBot: Enter retailer phone number.")
            retailer_number = input("You: ").strip()

            print("\nBot: How many items do you want to add in this order?")
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
                retailer_number=retailer_number,
                item_list=item_list
            )

            print("\nBot: Order result:")
            print_json(result)

        elif choice == "3":
            print("\nBot: Enter wholesaler phone number.")
            wholesaler_number = input("You: ").strip()

            print("\nBot: Enter item name.")
            item_name = input("You: ").strip()

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

        elif choice == "4":
            print("\nBot: Exiting. Bye.")
            break

        else:
            print("\nBot: Invalid choice. Please try again.")


if __name__ == "__main__":
    chatbot_cli()
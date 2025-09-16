from armour_data import post_armour_data
from skill_data import post_skill_data
from charm_data import post_charm_data
from decoration_data import post_deco_data
from weapon_data import post_weapon_data
import sys

"""Display the main menu options"""
def display_menu():
  print("\n" + "="*50)
  print("    Monster Hunter Wilds Data Scraper")
  print("="*50)
  print("1. Post Skills Data")
  print("2. Post Armour Data")
  print("3. Post Charms Data")
  print("4. Post Decorations Data")
  print("5. Post Weapons Data")
  print("0. Exit")
  print("-"*50)

"""Get and validate user input"""
def get_user_choice():
  while True:
    try:
      choice = input("Enter your choice (0-5): ").strip()
      if choice in ['0', '1', '2', '3', '4', '5']:
        return choice
      else:
        print("Invalid choice. Please enter a number between 0-5.")
    except KeyboardInterrupt:
      print("\n\nExiting...")
      sys.exit(0)
    except Exception as e:
      print(f"Error reading input: {e}")

"""Confirmation before executing"""
def confirm_action(action_name):
  response = input(f"Are you sure you want to {action_name}? (y/N): ").strip().lower()
  return response in ['y', 'yes']

"""Execute the selected option"""
def execute_choice(choice):
  success = False
  
  if choice == '1':
    if not confirm_action("post Skills data"):
      print("Operation cancelled.")
      return
    print("\nPosting Skills Data...")
    success = post_skill_data()
  elif choice == '2':
    if not confirm_action("post Armour data"):
      print("Operation cancelled.")
      return
    print("\nPosting Armour Data...")
    success = post_armour_data()
  elif choice == '3':
    if not confirm_action("post Charms data"):
      print("Operation cancelled.")
      return
    print("\nPosting Charms Data...")
    success = post_charm_data()
  elif choice == '4':
    if not confirm_action("post Decorations data"):
      print("Operation cancelled.")
      return
    print("\nPosting Decorations Data...")
    success = post_deco_data()
  elif choice == '5':
    if not confirm_action("post Weapons data"):
      print("Operation cancelled.")
      return
    print("\nPosting Weapons Data...")
    success = post_weapon_data()
  elif choice == '0':
    print("\nGoodbye!")
    sys.exit(0)
  
  # show result
  if success:
    print("Operation completed successfully!")
  else:
    print("Operation failed. Check the logs above for details.")

"""Main application loop"""
def main():
  print("Welcome to Monster Hunter Wilds Data Scraper!")
  
  while True:
    try:
      display_menu()
      choice = get_user_choice()
      execute_choice(choice)
      
      # prompt user to continue (except for exit)
      if choice != '0':
        input("\nPress Enter to continue...")
            
    except KeyboardInterrupt:
      print("\n\nExiting...")
      break
    except Exception as e:
      print(f"\nUnexpected error: {e}")
      input("Press Enter to continue...")

if __name__ == "__main__":
  main()
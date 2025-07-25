
def print_welcome():
    print("Welcome to the Personal Finance Tracker!\n")


def add_expense(data):
    try:
        description = input("Enter expense description: ").strip()
        if not description:
            raise ValueError("Description cannot be empty.")

        category = input("Enter category: ").strip()
        if not category:
            raise ValueError("Category cannot be empty.")

        amount_input = input("Enter amount: ").strip()
        amount = float(amount_input)
        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        # Add expense to category
        if category not in data:
            data[category] = []
        data[category].append((description, amount))
        print("Expense added successfully.\n")

    except ValueError as ve:
        print(f"Invalid input: {ve}\n")
    except Exception as e:
        print(f"An unexpected error occurred: {e}\n")


def view_expenses(data):
    if not data:
        print("No expenses recorded yet.\n")
        return

    print("\nAll Expenses:")
    for category, expenses in data.items():
        print(f"Category: {category}")
        for desc, amt in expenses:
            print(f"  - {desc}: ${amt:.2f}")
    print()


def view_summary(data):
    if not data:
        print("No expenses to summarize.\n")
        return

    print("\nSummary:")
    for category, expenses in data.items():
        total = sum(amount for _, amount in expenses)
        print(f"{category}: ${total:.2f}")
    print()


def main():
    expenses_data = {}
    print_welcome()

    while True:
        print("What would you like to do?")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Summary")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense(expenses_data)
        elif choice == "2":
            view_expenses(expenses_data)
        elif choice == "3":
            view_summary(expenses_data)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.\n")


if __name__ == "__main__":
    main()

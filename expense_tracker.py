
import json
import os
from typing import Dict, List

FILENAME = "expenses_python.json"

# ===================== EXPENSE CLASS =====================
class Expense:
    def __init__(self, expense_id: int, description: str, category: str,
                 amount: float, date: str):
        self.id = expense_id
        self.description = description
        self.category = category
        self.amount = amount
        self.date = date
        # Parse month and year
        self.year = int(date[:4])
        self.month = int(date[5:7])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "amount": self.amount,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        return cls(data["id"], data["description"], data["category"],
                   data["amount"], data["date"])

    def __repr__(self) -> str:
        return (f"ID: {self.id} | {self.description:<20} | {self.category:<15} | "
                f"KES {self.amount:<10.2f} | {self.date}")


# ===================== EXPENSE TRACKER CLASS =====================
class ExpenseTracker:
    def __init__(self):
        self.expenses: List[Expense] = []
        self.next_id = 1
        self.load_from_file()

    # ===================== ADD EXPENSE =====================
    def add_expense(self) -> None:
        print("\n--- Add New Expense ---")
        desc = input("Description: ")
        cat = input("Category (Food/Transport/Academics/Entertainment/Other): ")
        amount = float(input("Amount (KES): "))
        date = input("Date (YYYY-MM-DD): ")

        expense = Expense(self.next_id, desc, cat, amount, date)
        self.expenses.append(expense)  # O(1) amortized
        self.next_id += 1
        print(f"\n[+] Expense added successfully! ID: {expense.id}")

    # ===================== DISPLAY ALL =====================
    def display_all(self) -> None:
        if not self.expenses:
            print("\n[!] No expenses recorded yet.")
            return

        print("\n" + "=" * 70)
        print(f"         ALL EXPENSES ({len(self.expenses)} total)")
        print("=" * 70)
        print(f"{'ID':<5} {'Description':<22} {'Category':<15} {'Amount':<13} {'Date':<12}")
        print("-" * 70)

        total = 0
        for exp in self.expenses:
            print(f"{exp.id:<5} {exp.description:<22} {exp.category:<15} "
                  f"KES {exp.amount:<10.2f} {exp.date:<12}")
            total += exp.amount

        print("-" * 70)
        print(f"TOTAL SPENT: KES {total:.2f}")

    # ===================== SEARCH =====================
    def search_expense(self) -> None:
        if not self.expenses:
            print("\n[!] No expenses to search.")
            return

        print("\n--- Search Options ---")
        print("1. Search by Keyword (Linear Search)")
        print("2. Search by Amount (Binary Search - sorts first)")
        choice = input("Choice: ")

        if choice == "1":
            keyword = input("Enter keyword: ").lower()
            found = False
            print("\n--- Search Results ---")
            for exp in self.expenses:  # O(n) Linear Search
                if keyword in exp.description.lower() or keyword in exp.category.lower():
                    print(exp)
                    found = True
            if not found:
                print("No matching expenses found.")

        elif choice == "2":
            target = float(input("Enter exact amount: "))
            # Sort by amount first, then binary search
            self._merge_sort_amount()
            index = self._binary_search_amount(target)

            if index != -1:
                print(f"\n[✓] Found at index {index}:")
                print(self.expenses[index])
            else:
                print(f"\n[!] No expense with exact amount KES {target}")

    # ===================== MERGE SORT BY AMOUNT =====================
    def sort_by_amount_merge(self) -> None:
        if len(self.expenses) < 2:
            print("[!] Not enough expenses to sort.")
            return
        self.expenses = self._merge_sort_amount_recursive(self.expenses)
        print("\n[✓] Expenses sorted by amount using Merge Sort (ascending).")
        self.display_all()

    def _merge_sort_amount_recursive(self, arr: List[Expense]) -> List[Expense]:
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = self._merge_sort_amount_recursive(arr[:mid])
        right = self._merge_sort_amount_recursive(arr[mid:])

        return self._merge_amount(left, right)

    def _merge_amount(self, left: List[Expense], right: List[Expense]) -> List[Expense]:
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i].amount <= right[j].amount:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _merge_sort_amount(self) -> None:
        """In-place merge sort for binary search prep"""
        self.expenses = self._merge_sort_amount_recursive(self.expenses)

    # ===================== QUICK SORT BY DATE =====================
    def sort_by_date_quick(self) -> None:
        if len(self.expenses) < 2:
            print("[!] Not enough expenses to sort.")
            return
        self._quick_sort_date(0, len(self.expenses) - 1)
        print("\n[✓] Expenses sorted by date using Quick Sort (chronological).")
        self.display_all()

    def _quick_sort_date(self, low: int, high: int) -> None:
        if low < high:
            pi = self._partition_date(low, high)
            self._quick_sort_date(low, pi - 1)
            self._quick_sort_date(pi + 1, high)

    def _partition_date(self, low: int, high: int) -> int:
        pivot = self.expenses[high].date
        i = low - 1

        for j in range(low, high):
            if self.expenses[j].date <= pivot:
                i += 1
                self.expenses[i], self.expenses[j] = self.expenses[j], self.expenses[i]

        self.expenses[i + 1], self.expenses[high] = self.expenses[high], self.expenses[i + 1]
        return i + 1

    # ===================== BINARY SEARCH =====================
    def _binary_search_amount(self, target: float) -> int:
        left, right = 0, len(self.expenses) - 1
        while left <= right:
            mid = (left + right) // 2
            diff = self.expenses[mid].amount - target
            if abs(diff) < 0.01:
                return mid
            elif diff < 0:
                left = mid + 1
            else:
                right = mid - 1
        return -1

    # ===================== MONTHLY REPORT =====================
    def monthly_report(self) -> None:
        if not self.expenses:
            print("\n[!] No expenses recorded.")
            return

        target_month = int(input("\nEnter month (1-12): "))
        target_year = int(input("Enter year (YYYY): "))

        total = 0
        count = 0
        categories: Dict[str, float] = {}

        print("\n" + "=" * 70)
        print(f"    MONTHLY REPORT: {target_month:02d}/{target_year}")
        print("=" * 70)

        for exp in self.expenses:
            if exp.month == target_month and exp.year == target_year:
                print(exp)
                total += exp.amount
                count += 1
                categories[exp.category] = categories.get(exp.category, 0) + exp.amount

        print("-" * 70)
        print(f"Total Expenses: {count} | Total Amount: KES {total:.2f}")

        print("\n--- Category Breakdown ---")
        for cat, amt in categories.items():
            pct = (amt / total * 100) if total > 0 else 0
            print(f"{cat:<15}: KES {amt:<10.2f} ({pct:.1f}%)")

    # ===================== FILE OPERATIONS =====================
    def save_to_file(self) -> None:
        data = {
            "next_id": self.next_id,
            "expenses": [exp.to_dict() for exp in self.expenses]
        }
        with open(FILENAME, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[✓] Data saved to {FILENAME}")

    def load_from_file(self) -> None:
        if not os.path.exists(FILENAME):
            return
        try:
            with open(FILENAME, 'r') as f:
                data = json.load(f)
            self.next_id = data.get("next_id", 1)
            self.expenses = [Expense.from_dict(e) for e in data.get("expenses", [])]
            print(f"[✓] Loaded {len(self.expenses)} expenses from file.")
        except Exception as e:
            print(f"Error loading file: {e}")


# ===================== MAIN =====================
def main():
    tracker = ExpenseTracker()

    print("\n" + "=" * 70)
    print("   PERSONAL EXPENSE TRACKER (Python)")
    print("=" * 70)

    while True:
        print("\n--- Main Menu ---")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Search Expense")
        print("4. Sort by Amount (Merge Sort)")
        print("5. Sort by Date (Quick Sort)")
        print("6. Monthly Report")
        print("7. Save & Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            tracker.add_expense()
        elif choice == "2":
            tracker.display_all()
        elif choice == "3":
            tracker.search_expense()
        elif choice == "4":
            tracker.sort_by_amount_merge()
        elif choice == "5":
            tracker.sort_by_date_quick()
        elif choice == "6":
            tracker.monthly_report()
        elif choice == "7":
            tracker.save_to_file()
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
    
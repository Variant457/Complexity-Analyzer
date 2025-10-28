import requests
import json
import os

# The main entry point for the application
ANALYZER_URL = os.getenv("ANALYZER_URL", "http://localhost:5000/analyze")
headers = {"Content-Type": "application/json"}

# --------------------------------------------------------------------
# A collection of test cases for different recursive complexities
# --------------------------------------------------------------------

TEST_CASES = {
    "Factorial (O(n))": """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
""",

    "Binary Search (O(log n))": """
def binary_search(arr, low, high, x):
    if high >= low:
        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)
        else:
            return binary_search(arr, mid + 1, high, x)
    else:
        return -1
""",

    "Fibonacci (O(2^n))": """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
""",

    "Merge Sort (O(n log n))": """
def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr)//2
        L = arr[:mid]
        R = arr[mid:]

        merge_sort(L) # Recursive call 1
        merge_sort(R) # Recursive call 2

        i = j = k = 0
        
        # This loop is O(n) work
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1
""",
    
    "Recursive Selection Sort (O(n^2))": """
def recursive_sort(arr, n, index=0):
    if index == n:
        return

    # This loop is O(n) work
    min_idx = index
    for j in range(index + 1, n):
        if arr[j] < arr[min_idx]:
            min_idx = j
            
    arr[index], arr[min_idx] = arr[min_idx], arr[index]
    
    # This is one T(n-1) call
    recursive_sort(arr, n, index + 1)
""",

    "Infinite Recursion (O(inf))": """
def infinite_loop(n):
    # No base case that returns
    if n > 0:
        infinite_loop(n-1)
    return infinite_loop(n-1)
""",

    "Mixed Iterative and Recursive": """
# This iterative loop is O(n^3)
for i in range(n):
    for j in range(n):
        for k in range(n):
            print(i, j, k)

# This recursive function is O(n)
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
}

def run_test(name, code):
    """Helper function to send a test case and print the result."""
    print("=" * 70)
    print(f"TESTING: {name}")
    print("-" * 70)
    
    payload = {"code": code}
    
    try:
        response = requests.post(ANALYZER_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            # Highlight the most important results
            print("\n--- Key Results ---")
            print(f"Overall Big-O:   {result.get('big_o')}")
            print(f"Explanation:     {result.get('explanation')}")
            if 'recursive_analysis' in result:
                print("Recursive Analysis: SUCCESS")
            print("-" * 70)
            
        else:
            print(f"ERROR: Server returned status code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"FATAL ERROR: Could not connect to {ANALYZER_URL}")
        print("Please make sure the Docker containers are running.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return True

# --- Run all tests ---
if __name__ == "__main__":
    print("Starting Recursive Complexity Analyzer Test Suite...")
    all_passed = True
    for name, code in TEST_CASES.items():
        if not run_test(name, code):
            all_passed = False
            break
            
    if all_passed:
        print("\nTest suite finished.")
    else:
        print("\nTest suite failed to run.")
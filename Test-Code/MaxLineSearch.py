from random import randint

def main():
    size = randint(5, 30)
    a = []

    for i in range(size):
        a.append(i)

    max_value = a[0]
    print(f"Input size: {size}")
    print(f"Input array: {a}")
    for i in range(size):
        print(i)

    global c1, c2
    c1 = c2 = 0
    print(f"Linear Search: {linearSearch(a, max_value)}\t{c1}")
    print(f"Max Search: {maxValue(a)}\t{c2}")

def linearSearch(arr, x):
    for i in range(len(arr)):
        global c1
        c1 += 1
        if arr[i] == x:
            c1 += 1
            return True
    
    c1 += 1
    return False

def maxValue(arr):
    max_val = arr[0]
    for i in range(len(arr)):
        global c2
        c2 += 1
        if arr[i] > max_val:
            max_val = arr[i]
            c2 += 1
    c2 += 1
    return max_val
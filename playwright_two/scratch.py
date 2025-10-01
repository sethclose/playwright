count = 0
nums = [3, 5, 5, 3, 2, ]
print(f"{nums=}")
for i, num in enumerate(nums):
    if num in nums[:i]:
        nums.pop(i)
        print(f"remove {num=} {i=} {count=}")
    else:
        print(f"{num=}  keep {i=}  {count=}")
    count += 1
print(f"{nums=}")

import pandas as pd

# Create a sample Pandas Series
s = pd.Series([10, 20, 25, 27, 28.5], name="MySeries")

# Print the Series elements horizontally
print("Series values:", end=" ") # Optional: Add a label and a space
for item in s:
    print(item, end=" ") # Print each item followed by a space
print() # Print a newline character at the end

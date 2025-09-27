count = 0
nums = [3, 5, 5, 5, 2, ]
print(f"{nums=}")
for i, num in enumerate(nums):
    if num in nums[:i]:
        nums.pop(i)
        print(f"remove {num=} {i=} {count=}")
    else:
        print(f"{num=}  keep {i=}  {count=}")
    count += 1

for i, num in enumerate(nums):
    if num in nums[:i]:
        nums.pop(i)
        print(f"remove {num=} {i=} {count=}")
    else:
        print(f"{num=}  keep {i=}  {count=}")
    count += 1
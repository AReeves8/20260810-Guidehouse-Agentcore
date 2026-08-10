print("Hello World!")

# branching - if/elif/else
priority = "urgent"
if priority == "urgent" :
    print("Need action now!!!!")
elif priority == "high" :
    print("Action will be needed soon")
else :
    print("nothing needed now")


# loops - for and while

tags = ["urgent", "important", "billing", "finance"]

# iterating over some sort of iterable (a list, a string, a dict, etc)
for tag in tags:
    print(f"tag: {tag}")

# if you want the index or value of each loop, then range() can give you that
for i in range(4):
    print("tags pt2: " + tags[i])

# if you want the index and the value, then enumerate() is helpful
for i, tag in enumerate(tags) :
    print(f"Index {i} contains value {tag}")


countdown = 3
while True:
    print(countdown)
    countdown -= 1
    if countdown == 0:

        # break - will exit out of any currently running loop
        break               

# better version:
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1



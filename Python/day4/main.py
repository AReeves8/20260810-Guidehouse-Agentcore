import logging
from support_api.store import load_tickets
from pathlib import Path
from support_api.config import AppSettings
from support_api.filters import filter_tickets

# configuring logger for the app
logging.basicConfig(level=AppSettings().log_level, format="%(levelname)s %(name)s: %(message)s")


# exceptions/errors will stop a program all together
# number = 12435
# print(number / 0)

# try/except blocks allow you to keep the program running and handle the errors *gracefully*
try:
    # put some risky code
    number = 12435
    print(number / 0)           # immediately stops the try block and jumps to the corresponding except block

    print(num)

except NameError:
    print("make sure you decalred all your variables!")

except ZeroDivisionError:
    print("make sure you don't divide by zero!")

except Exception as e:      # Exception will catch EVERYTHING
    # catches any exception or error that is thrown
    print(e)


finally :
    print("a block of code that ALWAYS runs regardless of if an exception was thrown or not")

print("code after the error still runs")
print("\n-------------------------------------\n")


valid_tickets, error_tickets = load_tickets()

print("--- Valid Tickets ---")
print(valid_tickets)

print("\n--- Error Tickets ---")
print(error_tickets)

print("\n--- Filtering Tickets ---")
print(filter_tickets(valid_tickets, tenant="acme-corp", category="auth"))
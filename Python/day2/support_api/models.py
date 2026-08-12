
"""
models 
    programatically represent the shape of your data in your database
    meant to be VERY close to your database
"""

class Ticket:

    # python constructors is where you define your instance variables
    def __init__(self, id, tenant, title, priority, status = "open"):
        self.id = id
        self.tenant = tenant
        self.title = title
        self.priority = priority
        self.status = status

    # controls how the values of an object is formatted when called in print()
    def __repr__(self):
        return f"Ticket(id={self.id}, priority={self.priority}, status={self.status})"

    # self must be the first parameter if you're going to use it
    def is_open(self):
        return self.status in ("open", "ack", "escalated")

    # cls represents the CLASS itself, vs self represents an object
    # decorators - use the @ and change what a function is supposed to do
    # @classmethod - defines a class that will create an instance from some other data source
    @classmethod
    def from_row(cls, row):

        # calls the __init__ function
        return cls(
            id = row["id"],
            tenant = row["tenant"],
            title = row["title"],
            priority = row["priority"],
            status = row["status"]
        )

# inheritance - add parenthesis and "pass-in" parent class
class EscalatedTicket(Ticket):

    def __init__(self, id, tenant, title, priority, status, escalated_to):

        # super() - reperesents the parent class
        super().__init__(id, tenant, title, priority, status)
        self.escalated_to = escalated_to

    def __repr__(self):
        return f"EscalatedTicket(id={self.id}, escalated_to={self.escalated_to})"
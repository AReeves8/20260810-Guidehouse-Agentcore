""" fixed set of Tickets to test various prompts against """


# (ticket_id, expected_priority, text)
TICKETS = [
    (
        "T-01",
        "high",
        "Production checkout has been down for two hours. No customer can "
        "complete a purchase. We are losing roughly four thousand dollars an "
        "hour and our phones will not stop ringing.",
    ),
    (
        "T-02",
        "high",
        "It is fine, I suppose. It has only been three days since I reported "
        "that checkout fails for saved cards, and I have only had to explain "
        "to about forty of my own customers why their orders will not go "
        "through. I am sure someone will get to it eventually.",
    ),
    (
        "T-03",
        "low",
        "URGENT!!! The dark mode button on the settings page is two pixels "
        "off centre and it has been driving me CRAZY all morning. Please fix "
        "immediately!!!",
    ),
    (
        "T-04",
        "medium",
        "Reports have been taking about 40 seconds to load since last week's "
        "release. They still finish, and we can work around it, but the "
        "finance team runs about twenty of these a day and it is adding up.",
    ),
    (
        "T-05",
        "low",
        "Quick question -- does the Standard plan include SSO, or is that "
        "Enterprise only? No rush, just planning our rollout for next quarter.",
    ),
    (
        "T-06",
        "high",
        "Not sure this is a bug exactly, but our staging environment is "
        "returning real customer records instead of the seeded test data. "
        "Anyone with a staging login can see them. Let me know when you get "
        "a chance.",
    ),
    (
        "T-07",
        "medium",
        "The CSV export drops the last row whenever the file has more than "
        "1,000 records. We noticed because our monthly reconciliation was off "
        "by one order. We can re-export manually for now.",
    ),
    (
        "T-08",
        "low",
        "Loving the new dashboard! One small thing -- it would be great if "
        "the date filter remembered my last selection between visits. Not "
        "important, just a nice-to-have.",
    ),
]

VALID_PRIORITIES = {"low", "medium", "high"}

# converting the list of tickets to a proper list[dict]
def format_tickets() -> list[dict]:
    return [{"id": id, "expected": priority, "text": text} for id, priority, text in TICKETS]


SUPPORT_CONVERSATION = [
    (
        "user",
        "Customer Priya Raghavan, account NW-4417, reports that order A-1003 "
        "failed at checkout this morning. She was paying with a saved card. "
        "That's the third report of this today.",
    ),
    (
        "assistant",
        "That matches INC-4471, which is currently open. Saved-card payments "
        "have been failing since the March 5 release. The documented "
        "workaround is to ask the customer to re-enter their card details at "
        "checkout rather than selecting a stored card.",
    ),
    (
        "user",
        "Is it only saved cards, or is all payment processing affected?",
    ),
    (
        "assistant",
        "Only saved cards. Card details entered fresh at checkout process "
        "normally, which is why the failure rate looks lower than a full "
        "payment outage would.",
    ),
    (
        "user",
        "Roughly how many customers are hitting this?",
    ),
    (
        "assistant",
        "The incident register puts it at approximately 8% of transactions. "
        "That figure is from the March 6 update and has not been revised.",
    ),
    (
        "user",
        "She's asking about returning an item she ordered last month. Does "
        "this incident change anything there?",
    ),
    (
        "assistant",
        "It can. The standard return window is 45 days from delivery, with a "
        "12% restocking fee on returns received after day 30. INC-4471 is "
        "listed as qualifying for a restocking-fee waiver, so if her return "
        "is connected to the checkout failure, the fee can be waived without "
        "a supervisor's approval.",
    ),
    (
        "user",
        "Has engineering given an ETA for the fix?",
    ),
    (
        "assistant",
        "No ETA is recorded. The incident is still marked OPEN as of the "
        "March 6 update, with no target date attached.",
    ),
    (
        "user",
        "Anything else open right now that might be related?",
    ),
    (
        "assistant",
        "One other open incident: INC-4468, where CSV exports silently drop "
        "the final row above 1,000 records. Different subsystem, so it is "
        "unlikely to be connected to the payment failures.",
    ),
    (
        "user",
        "What should I tell her about the workaround without making it sound "
        "like we're blaming her card?",
    ),
    (
        "assistant",
        "Frame it as a known issue on our side with a temporary workaround. "
        "Something like: we have identified a problem affecting stored "
        "payment methods, our team is working on it, and in the meantime "
        "entering card details directly at checkout will complete the order.",
    ),
    (
        "user",
        "Good. Draft that as a short reply to her, and include her order "
        "number so she can reference it.",
    ),
]

# tracking key facts to compare different contexts too
KEY_FACTS = {
    "customer_name": "Priya Raghavan",
    "account_id": "NW-4417",
    "order_id": "A-1003"
}

def format_conversation() -> list[dict]:
    return [{"role": role, "content": [{"text": text}]} for role, text in SUPPORT_CONVERSATION]
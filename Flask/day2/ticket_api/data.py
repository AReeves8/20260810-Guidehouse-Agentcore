""" Use this as mock data for this app until we can connect to a real database. """


TICKETS = [
    {"id": "TKT-1", "tenant": "acme-corp",  "title": "Login fails on SSO",   "priority": "urgent", "status": "open"},
    {"id": "TKT-2", "tenant": "globex",     "title": "CSV export broken",    "priority": "low",    "status": "resolved"},
    {"id": "TKT-3", "tenant": "acme-corp",  "title": "Double billing issue", "priority": "urgent", "status": "open"},
    {"id": "TKT-4", "tenant": "initech",    "title": "Slow dashboard load",  "priority": "medium", "status": "ack"},
    {"id": "TKT-5", "tenant": "globex",     "title": "Password reset email", "priority": "high",   "status": "escalated"},
    {"id": "TKT-6", "tenant": "acme-corp",  "title": "Typo on invoice PDF",  "priority": "low",    "status": "open"},
]
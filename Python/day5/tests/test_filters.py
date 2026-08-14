
from support_api.filters import count_by_priority, filter_tickets
from support_api.data import SAMPLE_TICKETS
from support_api.models import Ticket

# using _ in front of the func name tells pytest that it is a helper function used by your tests
def _tickets():
    return [Ticket.model_validate(row) for row in SAMPLE_TICKETS]

# pytest looks for files and functions prefixed with "test_"
def test_filter_by_tenant_and_priority():

    output = filter_tickets(_tickets(), tenant="acme-corp", priority="urgent")

    # assert keyword to check the results of your test
    #   - throw an exception if the assertion is false
    #       - ANY raised exception results in a failed test
    assert [t.id for t in output] == ["TKT-0001"]

    # testing what happens if tenant is an invalid value
    output = filter_tickets(_tickets(), tenant="garbage value", priority="urgent")
    assert [t.id for t in output] == []

    # testing what happens if priority is an invalid value
    output = filter_tickets(_tickets(), tenant="acme-corp", priority="garbage value")
    assert [t.id for t in output] == [], f"Expected result: {True} was not received."

##########################################################################
### would be best to add tests for status and category filters as well ###
##########################################################################


def test_no_filters_returns_everything():
    # testing that all tickets get returned when there are no filters
    assert len(filter_tickets(_tickets())) == len(_tickets())
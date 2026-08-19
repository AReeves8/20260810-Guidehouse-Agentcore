from flask import Blueprint, jsonify, request
from ticket_api import ticket_store
from ticket_api.responses import single_envelope, list_envelope, ApiError
from pydantic import ValidationError

tickets_bp = Blueprint("tickets", __name__)


# GET /api/v1/tickets
@tickets_bp.get("")
def get_tickets():
    """ 
        query parameters: 
            ?some-param=some-value&param2=value2....
            can use the 'request' object from flask to extract these as a dictionary
                ex: params = request.args
    """
    # get a specific query param
    priority = request.args.get("priority")

    # return all tickets of no priority is given
    if priority is None:
        return list_envelope(ticket_store.list_tickets())

    # return matching tickets
    return list_envelope(ticket_store.find_tickets_by_priority(priority))
    

# GET /api/v1/tickets/{id}
@tickets_bp.get("/<ticket_id>")
def get_ticket_by_id(ticket_id):
    """ 
        path variables (aka path parameters): 
            dynamic variables in the URI path
            always required
            denote them with '<>' in flask route
            flask will map them to a function param with the same name

        example path: /api/v1/tickets/TKT-1
    """
    ticket = ticket_store.find_ticket_by_id(ticket_id)

    # raise an ApiError if there is no ticket
    if ticket is None:
        raise ApiError(code="not_found", status=400, detail=ticket_id)

    # status code defaults to 200 if not provided
    return single_envelope(ticket)


# POST /api/v1/tickets
@tickets_bp.post("")
def create_new_ticket():

    # use request object to retrieve request body
    #       silent=True make it so that Flask doesn't raise an exception when thre is no request body
    #       alternatively, you could just wrap this in a try/except block and handle that exception accordingly
    body = request.get_json(silent=True) or {}     # if there's no request body, set the value to an empty object
    return single_envelope(ticket_store.create_ticket(body)), 201        # setting status code as 201 - CREATED
   
    
# PUT /api/v1/tickets/{id}
@tickets_bp.put("/<ticket_id>")
def update_existing_ticket(ticket_id):

    body = request.get_json(silent=True) or {}     # if there's no request body, set the value to an empty object
    return single_envelope(ticket_store.update_ticket(ticket_id, body)), 200     # if you want to return nothing on updates, return a 204 instead of 200
    
    
# DELETE /api/v1/tickets/{id}
@tickets_bp.delete("/<ticket_id>")
def delete_ticket_by_id(ticket_id):

    success = ticket_store.delete_ticket(ticket_id)
    if success:
        return jsonify(status="deleted"), 204
    return jsonify(error="not found"), 404
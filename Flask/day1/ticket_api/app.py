
from flask import Flask, jsonify, request
from ticket_api.store import *

API_PREFIX = "/api/v1/tickets"

def create_app():

    # uses the factory pattern to create and return a new Flask app
    app = Flask(__name__)

    # could do: @app.route(...., methods=["GET", "POST", "PUT"]) - less recommended
    @app.get(f"{API_PREFIX}/ping")      # endpoint full name: /api/v1/tickets/ping
    def ping():
        return jsonify(status="ok")

    # GET /api/v1/tickets
    @app.get(API_PREFIX)
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
            return jsonify(list_tickets())

        # return matching tickets if possible
        return jsonify(find_tickets_by_priority(priority))

    # GET /api/v1/tickets/{id}
    @app.get(f"{API_PREFIX}/<ticket_id>")
    def get_ticket_by_id(ticket_id):
        """ 
            path variables (aka path parameters): 
                dynamic variables in the URI path
                always required
                denote them with '<>' in flask route
                flask will map them to a function param with the same name

            example path: /api/v1/tickets/TKT-1
        """
        ticket = find_ticket_by_id(ticket_id)

        # returning tuple with json body and status code 404 if no ticket was found
        if ticket is None:
            return jsonify(error="not_found", detail=ticket_id), 404

        # status code defaults to 200 if not provided
        return jsonify(ticket)

    # POST /api/v1/tickets
    @app.post(API_PREFIX)
    def create_new_ticket():

        # use request object to retrieve request body
        #       silent=True make it so that Flask doesn't raise an exception when thre is no request body
        #       alternatively, you could just wrap this in a try/except block and handle that exception accordingly
        body = request.get_json(silent=True) or {}     # if there's no request body, set the value to an empty object

        return jsonify(create_ticket(body)), 201        # setting status code as 201 - CREATED
        
    # PUT /api/v1/tickets/{id}
    @app.put(f"{API_PREFIX}/<ticket_id>")
    def update_existing_ticket(ticket_id):

        body = request.get_json(silent=True) or {}     # if there's no request body, set the value to an empty object
        
        return jsonify(update_ticket(ticket_id, body)), 200     # if you want to return nothing on updates, return a 204 instead of 200

    # DELETE /api/v1/tickets/{id}
    @app.delete(f"{API_PREFIX}/<ticket_id>")
    def delete_ticket_by_id(ticket_id):

        success = delete_ticket(ticket_id)
        if success:
            return jsonify(status="deleted"), 204
        return jsonify(error="not found"), 404




    
    return app



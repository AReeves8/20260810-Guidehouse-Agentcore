from flask import Flask
from pydantic import ValidationError
from ticket_api.health import health_bp
from ticket_api.tickets import tickets_bp
from ticket_api.responses import ApiError, error_response


def create_app():

    # uses the factory pattern to create and return a new Flask app
    app = Flask(__name__)

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(tickets_bp, url_prefix="/api/v1/tickets")


    """
        Global Exception Handling
            you will handle your errors and exceptions in one place rather than in each individual endpoint
            Flask's will pick the most specific exception it can find when one is raised
                - so its safe to have a handler for Exception to catch anything you didn't anticipate
                    - (as long as you still are handling more specific exceptions)
    """

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):

        first_error = error.errors()[0]
        detail_str = f"{first_error['loc']}: {first_error['msg']}"

        # 422 - UNPROCESSABLE_ENTITY - more specific than a 400
        return error_response("validation_failed", 422, detail_str)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception):
        return error_response("internal", 500, "an unexpected error ocurred")

    # can handle status codes as well, not just exceptions and errors
    @app.errorhandler(404)
    def handle_resource_not_found(error):
        """ this will handle the times where FLASK throws a 404, not when your code sets the status as 404 """

        return error_response("not_found", 404, "no route for the given path")
    
    return app



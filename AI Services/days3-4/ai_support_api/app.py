from flask import Flask
from pydantic import ValidationError
from botocore.exceptions import BotoCoreError, ClientError
from ai_support_api.responses import ApiError, error_response
from ai_support_api.health.routes import health_bp
from ai_support_api.translate.routes import translation_bp
from ai_support_api.analysis.routes import analysis_bp


# Common AWS Errors and their codes
_CLIENT_FAULT_STATUS = {
    "AccessDeniedException": 403,
    "AccessDenied": 403,
    "UnrecognizedClientException": 403,
    "ValidationException": 422,
    "InvalidParameterException": 422,
    "InvalidParameterValueException": 422,
    "TextSizeLimitExceededException": 422,
    "InvalidRequestException": 422,
    "UnsupportedLanguagePairException": 422,
    "ThrottlingException": 429,
    "TooManyRequestsException": 429,
    "ResourceNotFoundException": 404,
}


def create_app():

    # uses the factory pattern to create and return a new Flask app
    app = Flask(__name__)

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(translation_bp, url_prefix="/api/v1/translation")
    app.register_blueprint(analysis_bp, url_prefix="/api/v1/analysis")

    """
        Global Exception Handling
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
        app.logger.exception(error)
        return error_response("internal", 500, "an unexpected error ocurred")

    # can handle status codes as well, not just exceptions and errors
    @app.errorhandler(404)
    def handle_resource_not_found(error):
        """ this will handle the times where FLASK throws a 404, not when your code sets the status as 404 """

        return error_response("not_found", 404, "no route for the given path")


    """
        Boto3 Errors
    """
    @app.errorhandler(ClientError)
    def handle_aws_client_error(error):

        # only extracting the code from aws so we don't reveal too much info to client
        aws_code = error.get("Error", {}).get("Code", "UnknownAwsError")
        status = _CLIENT_FAULT_STATUS.get(aws_code, 502)    # default to 502 - Bad Gateway error
        app.logger.exception("AWS call failed: %s", aws_code)
        return error_response("aws_error", status, aws_code)



    @app.errorhandler(BotoCoreError)
    def handle_botocore_error(error):
        app.logger.exception("AWS SDK/configuration error")
        return error_response("aws_configuration_error", 500, type(error).__name__)
    
    return app



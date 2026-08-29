""" Shared validation for multipart file uploads """


from ai_support_api.responses import ApiError
from werkzeug.datastructures import FileStorage


def read_upload(
        file_storage: FileStorage | None, 
        allowed_extensions: set[str],
        max_bytes: int
    ) -> tuple[bytes, str]:
    """ validate one uploaded file and return its bytes and the filename """

    # validate that we received a file
    if file_storage is None or not file_storage.filename:
        raise ApiError("validation_failed", 422, "no file uploaded - multi-part/form-data expected")

    # validate the file extension
    extension = file_storage.filename.rsplit(".", 1)[-1].lower()    # -1 gives you the LAST value in an array
    if extension not in allowed_extensions:
        raise ApiError(
            "unsupported_media_type", 
            415,            # UNSUPPORTED_MEDIA_TYPE
            f"{extension} is not supported. Expected one of the following: {[e for e in allowed_extensions]}"
        )

    # reads in all the bytes from the file
    content = file_storage.read()

    # validate that the file is within the allowed number of bytes
    if len(content) > max_bytes:
        raise ApiError(
            "payload_to_large",
            413,            # CONTENT_TO_LARGE
            f"file is {len(content)} bytes; max allowed is {max_bytes} bytes."
        )

    # validate the file actually has data
    if not content:
        raise ApiError("validation_failed", 422, "uploaded file is empty")

    return content, file_storage.filename
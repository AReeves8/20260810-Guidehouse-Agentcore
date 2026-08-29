""" 
    use rekognition and textract to read text from a support ticket 

    Amazon Rekognition - identify content of an image. works with jpeg and png. 

    Amazon Textract - pulling text out of a document or image. works with jpeg, png, and pdf. 
"""


from ai_support_api.aws import get_client

# Rekognition caps file sizes at 5 MB
MAX_IMAGE_BYTES = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def extract_document_text(doc_bytes: bytes) -> list[str]:
    """ use Textract to return the document's text """

    # AWS expects ALL bytes at once
    response = get_client("textract").detect_document_text(Document={"Bytes": doc_bytes})
    return [block["Text"] for block in response["Blocks"] if block["BlockType"] == "LINE"]


def detect_image_text(image_bytes: bytes) -> list[str]:
    """ use Rekognition to return the text in an image """

    # AWS expects ALL bytes at once
    response = get_client("rekognition").detect_text(Image={"Bytes": image_bytes})
    return [detection["DetectedText"] for detection in response["TextDetections"] if detection["Type"] == "LINE"]


def detect_image_labels(image_bytes: bytes, max_labels: int = 10) -> list[dict]:
    """ use Rekognition to determine objects and scene of image """

    # AWS expects ALL bytes at once
    response = get_client("rekognition").detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=max_labels,
            MinConfidence=70            # only return labels that the model is at least 70% confident in
        )
    return [
        {"name": label["Name"], "confidence": round(label["Confidence"], 3)}
        for label in response["Labels"] 
    ]


def read_attachment(image_bytes: bytes) -> dict:
    """ call both textract and rekognition to compare results """

    return {
        "textract_lines": extract_document_text(image_bytes),
        "rekognition_lines": detect_image_text(image_bytes),
        "rekognition_labels": detect_image_labels(image_bytes)
    }
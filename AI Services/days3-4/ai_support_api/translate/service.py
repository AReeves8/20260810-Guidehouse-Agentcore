""" calling AWS Translate with boto3 """


from ai_support_api.aws import get_client


def translate(text: str, src_lang: str, trg_lang: str) -> dict:

    # calling AWS Translate with boto3
    response = get_client("translate").translate_text(
        Text=text,
        SourceLanguageCode=src_lang,
        TargetLanguageCode=trg_lang
    )

    # if the request took in "auto", response["SourceLanguageCode"] will contain the language AWS detected
    return {
        "translated_text": response["TranslatedText"],
        "source_language": response["SourceLanguageCode"],
        "target_language": response["TargetLanguageCode"]
    }
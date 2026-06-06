from app.security.sensitive_detector import (
    detect_sensitive_data
)


def filter_response(
    response: str
):

    sensitive = detect_sensitive_data(
        response
    )

    if sensitive["decision"] == "BLOCK":

        return {

            "response":

                "Sensitive information "
                "was prevented from "
                "being exposed.",

            "blocked": True

        }

    if sensitive["decision"] == "MASK":

        return {

            "response":

                "[MASKED SENSITIVE DATA]",

            "blocked": False

        }

    return {

        "response": response,

        "blocked": False

    }
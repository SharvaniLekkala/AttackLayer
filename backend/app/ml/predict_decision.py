from app.ml.model_loader import load_model


def predict_decision(
    embedding
):

    model = load_model()

    prediction = model.predict(
        [embedding]
    )[0]

    probabilities = model.predict_proba(
        [embedding]
    )[0]

    confidence = max(
        probabilities
    )

    return {

        "prediction": int(prediction),

        "confidence": float(confidence)

    }
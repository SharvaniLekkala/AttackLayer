from app.ml.ensemble import get_ensemble_prediction
from app.security.adversarial_guard import AdversarialGuard

def predict_decision(embedding) -> dict:
    """
    Predict security decision using the robust multi-model ensemble
    and adversarial defense layers.
    """
    # 1. Run ensemble prediction
    ensemble_res = get_ensemble_prediction(embedding)
    
    # 2. Run adversarial guard checks
    adv_res = AdversarialGuard.assess_adversarial_risk(ensemble_res["model_predictions"])
    
    prediction = ensemble_res["prediction"]
    confidence = ensemble_res["confidence"]
    
    # If adversarial guard flags a critical disagreement or anomaly, 
    # override or flag it. For example, if critical model disagreement, 
    # we force review state by adjusting confidence/prediction, or flagging it.
    if adv_res["adversarial_detected"]:
        # If there's a risk of adversarial attack/disagreement, flag low trust
        print(f"Adversarial Guard Triggered: {adv_res['reasons']}")
        # Keep prediction but force a quarantine/review confidence level if it was an attack prediction,
        # or flag it for review.
        if prediction == 1:
            # Boost confidence to BLOCK if highly likely, or lower to force QUARANTINE/REVIEW
            # Let's adjust to ensure human review is triggered
            confidence = min(confidence, 0.85)  # Forces Quarantine / Review
            
    # Return output format expected by the system
    return {
        "prediction": prediction,
        "confidence": confidence,
        "ensemble_info": ensemble_res,
        "adversarial_info": adv_res
    }
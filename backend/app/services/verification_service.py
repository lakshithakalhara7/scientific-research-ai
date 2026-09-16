class VerificationService:
    """
    Contains the basic logic used to check whether
    a scientific claim is supported by retrieved evidence.
    """

    def verify_claim(self, claim, evidence):
        """
        Compare a claim with evidence.

        For this first simple version, we check whether
        important words from the claim appear in the evidence.
        """

        claim_words = set(claim.lower().split())
        evidence_words = set(evidence.lower().split())

        matching_words = claim_words.intersection(evidence_words)

        if len(claim_words) == 0:
            score = 0
        else:
            score = len(matching_words) / len(claim_words)

        if score >= 0.6:
            status = "SUPPORTED"

        elif score >= 0.3:
            status = "PARTIALLY_SUPPORTED"

        else:
            status = "UNSUPPORTED"

        return {
            "claim": claim,
            "status": status,
            "score": round(score, 2),
            "matching_words": list(matching_words)
        }
import re


class VerificationService:
    """
    Contains the basic logic used to check whether
    a scientific claim is supported by retrieved evidence.
    """

    def clean_text(self, text):
        """
        Convert text to lowercase and remove punctuation.
        """

        text = text.lower()

        text = re.sub(r"[^\w\s]", "", text)

        return text

    def verify_claim(self, claim, evidence):
        """
        Compare a claim with evidence.
        """

        cleaned_claim = self.clean_text(claim)
        cleaned_evidence = self.clean_text(evidence)

        claim_words = set(cleaned_claim.split())
        evidence_words = set(cleaned_evidence.split())

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
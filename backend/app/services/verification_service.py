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
    def extract_claims(self, answer):
        """
        Split an AI-generated answer into individual claims.
        """

        if not answer or not answer.strip():
            return []

        claims = re.split(
            r'(?<=[.!?])\s+',
            answer.strip()
        )

        claims = [
            claim.strip()
            for claim in claims
            if claim.strip()
        ]

        return claims

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
    def verify_against_sources(self, claim, sources):
        """
        Verify one scientific claim against multiple research sources.
        """

        results = []

        for source in sources:

            verification = self.verify_claim(
                claim,
                source["text"]
            )

            verification["source"] = source["source"]

            results.append(verification)

        if len(results) == 0:
            return {
                "claim": claim,
                "status": "UNSUPPORTED",
                "best_source": None,
                "score": 0,
                "all_results": []
            }

        best_result = max(
            results,
            key=lambda result: result["score"]
        )

        if best_result["status"] == "UNSUPPORTED":
            best_source = None
        else:
            best_source = best_result["source"]

        return {
            "claim": claim,
            "status": best_result["status"],
            "best_source": best_source,
            "score": best_result["score"],
            "matching_words": best_result["matching_words"],
            "all_results": results
        }
    def verify_answer(self, answer, sources):
        """
        Verify all claims in an AI-generated answer.
        """

        claims = self.extract_claims(answer)

        verification_results = []

        for claim in claims:

            result = self.verify_against_sources(
                claim,
                sources
            )

            verification_results.append(result)

        if len(verification_results) == 0:
            overall_status = "UNVERIFIED"

        else:
            statuses = [
                result["status"]
                for result in verification_results
            ]

            if all(
                status == "SUPPORTED"
                for status in statuses
            ):
                overall_status = "VERIFIED"

            elif all(
                status == "UNSUPPORTED"
                for status in statuses
            ):
                overall_status = "UNVERIFIED"

            else:
                overall_status = "PARTIALLY_VERIFIED"
                
        hallucinations = self.detect_hallucinations(
                        verification_results
                    )
        return {
            "answer": answer,
            "overall_status": overall_status,
            "total_claims": len(claims),
            "verified_claims": sum(
                1
                for result in verification_results
                if result["status"] == "SUPPORTED"
            ),
            "unsupported_claims": sum(
                1
                for result in verification_results
                if result["status"] == "UNSUPPORTED"
            ),
            "hallucination_detected": len(hallucinations) > 0,
            "hallucinations": hallucinations,
            "claims": verification_results
        }

    #hallucination detection method
    def detect_hallucinations(self, verification_results):
        """
        Identify unsupported claims as potential hallucinations.
        """

        hallucinations = []

        for result in verification_results:

            if result["status"] == "UNSUPPORTED":

                hallucinations.append({
                    "claim": result["claim"],
                    "reason": (
                        "No retrieved scientific source provides "
                        "sufficient evidence for this claim."
                    ),
                    "action": (
                        "Do not present this claim as verified "
                        "scientific information."
                    )
                })

        return hallucinations
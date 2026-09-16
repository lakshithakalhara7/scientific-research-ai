import re
STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "that",
    "this",
    "these",
    "those"
}

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "neither",
    "nor",
    "cannot",
    "without"
}

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

    def get_important_words(self, text):
        """
        Remove common stop words and return
        the meaningful words from the text.
        """

        cleaned_text = self.clean_text(text)

        words = cleaned_text.split()

        important_words = {
            word
            for word in words
            if word not in STOP_WORDS
        }

        return important_words

    def contains_negation(self, text):
        """
        Check whether text contains a common negation word.
        """

        cleaned_text = self.clean_text(text)

        words = set(cleaned_text.split())

        return len(words.intersection(NEGATION_WORDS)) > 0

    def detect_contradiction(self, claim, evidence):
        """
        Detect a simple contradiction based on
        different negation patterns.
        """

        claim_has_negation = self.contains_negation(claim)
        evidence_has_negation = self.contains_negation(evidence)

        if claim_has_negation != evidence_has_negation:
            return True

        return False

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

        claim_words = self.get_important_words(claim)
        evidence_words = self.get_important_words(evidence)

        matching_words = claim_words.intersection(evidence_words)

        if len(claim_words) == 0:
            score = 0
        else:
            score = len(matching_words) / len(claim_words)

        has_negation_difference = self.detect_contradiction(
            claim,
            evidence
        )

        is_contradiction = (
            has_negation_difference
            and score >= 0.3
)   

        if is_contradiction and score >= 0.3:
            status = "CONTRADICTED"

        elif score >= 0.6:
            status = "SUPPORTED"

        elif score >= 0.3:
            status = "PARTIALLY_SUPPORTED"

        else:
            status = "UNSUPPORTED"

        return {
            "claim": claim,
            "status": status,
            "score": round(score, 2),
            "matching_words": list(matching_words),
            "contradiction": is_contradiction
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

        contradicted_claims = sum(
    1
            for result in verification_results
            if result["status"] == "CONTRADICTED"
        )

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

            "contradicted_claims": contradicted_claims,

            "hallucination_detected": len(hallucinations) > 0,
            "hallucinations": hallucinations,
            "claims": verification_results
        }

    #hallucination detection method
    def detect_hallucinations(self, verification_results):
        """
        Identify unsupported or contradicted claims
        as potential hallucinations.
        """

        hallucinations = []

        for result in verification_results:

            if result["status"] == "UNSUPPORTED":

                hallucinations.append({
                    "claim": result["claim"],
                    "type": "UNSUPPORTED",
                    "reason": (
                        "No retrieved scientific source provides "
                        "sufficient evidence for this claim."
                    ),
                    "action": (
                        "Do not present this claim as verified "
                        "scientific information."
                    )
                })

            elif result["status"] == "CONTRADICTED":

                hallucinations.append({
                    "claim": result["claim"],
                    "type": "CONTRADICTION",
                    "reason": (
                        "Retrieved scientific evidence contradicts "
                        "this claim."
                    ),
                    "action": (
                        "Review or remove this claim before "
                        "presenting the final answer."
                    )
                })

        return hallucinations
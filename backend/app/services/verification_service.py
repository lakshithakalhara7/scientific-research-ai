import re
import json

from app.services.llm_service import LLMService

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
    def __init__(self):
        self.llm = LLMService()

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

    def semantic_verify_claim(self, claim, evidence):
        """
        Use Gemini to semantically verify a scientific claim
        against provided research evidence.
        """

        prompt = f"""
    You are a Scientific Research Verification Agent.

    Your task is to verify a generated scientific claim using
    ONLY the provided research evidence.

    CLAIM:
    {claim}

    EVIDENCE:
    {evidence}

    Classify the claim as exactly one of:

    SUPPORTED
    - The evidence clearly supports the claim.

    CONTRADICTED
    - The evidence clearly conflicts with the claim.

    NOT_ENOUGH_EVIDENCE
    - The evidence does not provide enough information to verify
    or contradict the claim.

    Important rules:
    1. Use ONLY the provided evidence.
    2. Do not use outside knowledge.
    3. Do not assume missing information.
    4. Be conservative when evidence is unclear.
    5. Return ONLY valid JSON.
    6. Do not use markdown or code fences.

    Return exactly this structure:

    {{
        "status": "SUPPORTED | CONTRADICTED | NOT_ENOUGH_EVIDENCE",
        "reason": "short explanation based only on the evidence"
    }}
    """

        raw_response = self.llm.generate_response(prompt)

        cleaned_response = (
            raw_response
            .strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        try:
            result = json.loads(cleaned_response)

        except json.JSONDecodeError:

            return {
                "status": "NOT_ENOUGH_EVIDENCE",
                "reason": (
                    "The semantic verification model returned "
                    "an invalid response."
                )
            }

        allowed_statuses = {
            "SUPPORTED",
            "CONTRADICTED",
            "NOT_ENOUGH_EVIDENCE"
        }

        if result.get("status") not in allowed_statuses:

            return {
                "status": "NOT_ENOUGH_EVIDENCE",
                "reason": (
                    "The semantic verification model returned "
                    "an invalid verification status."
                )
            }

        return {
            "status": result["status"],
            "reason": result.get(
                "reason",
                "No explanation was provided."
            )
        }

    def semantic_verify_against_sources(self, claim, sources):
        """
        Semantically verify one claim against all retrieved
        scientific sources in a single Gemini request.
        """

        if not sources:
            return {
                "claim": claim,
                "status": "NOT_ENOUGH_EVIDENCE",
                "supported_sources": [],
                "contradicted_sources": [],
                "reason": "No research sources were provided."
            }

        evidence_sections = []

        for source in sources:
            evidence_sections.append(
                f"""
    SOURCE: {source["source"]}
    EVIDENCE:
    {source["text"]}
    """
            )

        combined_evidence = "\n".join(evidence_sections)

        prompt = f"""
    You are a Scientific Research Verification Agent.

    Verify the scientific claim using ONLY the research
    evidence supplied below.

    CLAIM:
    {claim}

    RESEARCH SOURCES:
    {combined_evidence}

    Classify the claim as exactly one of:

    SUPPORTED
    - One or more sources clearly support the claim and
    there is no clear contradictory source.

    CONTRADICTED
    - One or more sources clearly contradict the claim and
    there is no clear supporting source.

    CONFLICTING_EVIDENCE
    - At least one source supports the claim and at least
    one other source contradicts it.

    NOT_ENOUGH_EVIDENCE
    - The sources do not provide enough information.

    Rules:
    1. Use ONLY the provided evidence.
    2. Do not use outside knowledge.
    3. Do not invent source names.
    4. Do not assume missing information.
    5. Be conservative when evidence is unclear.
    6. Return ONLY valid JSON.
    7. Do not use markdown code fences.

    Return exactly:

    {{
        "status": "SUPPORTED | CONTRADICTED | CONFLICTING_EVIDENCE | NOT_ENOUGH_EVIDENCE",
        "supported_sources": [],
        "contradicted_sources": [],
        "reason": "short evidence-based explanation"
    }}
    """

        try:
            raw_response = self.llm.generate_response(prompt)

        except Exception as error:
            return {
                "claim": claim,
                "status": "VERIFICATION_UNAVAILABLE",
                "supported_sources": [],
                "contradicted_sources": [],
                "reason": (
                    "Semantic verification is temporarily unavailable. "
                    f"Error: {type(error).__name__}"
                )
            }

        cleaned_response = (
            raw_response
            .strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        try:
            result = json.loads(cleaned_response)

        except json.JSONDecodeError:
            return {
                "claim": claim,
                "status": "VERIFICATION_UNAVAILABLE",
                "supported_sources": [],
                "contradicted_sources": [],
                "reason": (
                    "The semantic verification model returned "
                    "an invalid JSON response."
                )
            }

        allowed_statuses = {
            "SUPPORTED",
            "CONTRADICTED",
            "CONFLICTING_EVIDENCE",
            "NOT_ENOUGH_EVIDENCE"
        }

        status = result.get("status")

        if status not in allowed_statuses:
            status = "VERIFICATION_UNAVAILABLE"

        return {
            "claim": claim,
            "status": status,
            "supported_sources": result.get(
                "supported_sources",
                []
            ),
            "contradicted_sources": result.get(
                "contradicted_sources",
                []
            ),
            "reason": result.get(
                "reason",
                "No explanation was provided."
            )
        }
    def hybrid_verify_against_sources(self, claim, sources):
        """
        Combine rule-based and semantic verification.
        """

        rule_result = self.verify_against_sources(
            claim,
            sources
        )

        semantic_result = self.semantic_verify_against_sources(
            claim,
            sources
        )

        if semantic_result["status"] == "VERIFICATION_UNAVAILABLE":
            final_status = rule_result["status"]
            decision_method = "RULE_BASED_FALLBACK"

        else:
            final_status = semantic_result["status"]
            decision_method = "SEMANTIC"

        return {
            "claim": claim,
            "final_status": final_status,
            "decision_method": decision_method,

            "rule_based": {
                "status": rule_result["status"],
                "score": rule_result["score"],
                "best_source": rule_result["best_source"]
            },

            "semantic": semantic_result
        }

    def hybrid_verify_answer(self, answer, sources):
        """
        Verify every claim in a complete AI-generated answer
        using rule-based and semantic verification.
        """

        claims = self.extract_claims(answer)

        results = []

        for claim in claims:

            result = self.hybrid_verify_against_sources(
                claim,
                sources
            )

            results.append(result)

        verified_claims = sum(
            1
            for result in results
            if result["final_status"] == "SUPPORTED"
        )

        contradicted_claims = sum(
            1
            for result in results
            if result["final_status"] == "CONTRADICTED"
        )

        insufficient_claims = sum(
            1
            for result in results
            if result["final_status"] == "NOT_ENOUGH_EVIDENCE"
        )

        conflicting_claims = sum(
            1
            for result in results
            if result["final_status"] == "CONFLICTING_EVIDENCE"
        )

        if len(results) == 0:
            overall_status = "UNVERIFIED"

        elif verified_claims == len(results):
            overall_status = "VERIFIED"

        else:
            overall_status = "PARTIALLY_VERIFIED"

        return {
            "answer": answer,
            "overall_status": overall_status,
            "total_claims": len(results),

            "verified_claims": verified_claims,
            "contradicted_claims": contradicted_claims,
            "insufficient_evidence_claims": insufficient_claims,
            "conflicting_claims": conflicting_claims,

            "claims": results
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
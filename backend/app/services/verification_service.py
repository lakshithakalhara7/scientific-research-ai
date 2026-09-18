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
        Rule-based verification using the most relevant
        evidence sentence instead of the whole source chunk.
        """

        evidence_sentences = self.split_into_sentences(
            evidence
        )

        if not evidence_sentences:
            return {
                "claim": claim,
                "status": "UNSUPPORTED",
                "score": 0.0,
                "matching_words": [],
                "contradiction": False,
                "matched_evidence": None
            }

        best_sentence = None
        best_score = 0.0
        best_matching_words = []

        for sentence in evidence_sentences:

            score, matching_words = (
                self.calculate_overlap_score(
                    claim,
                    sentence
                )
            )

            if score > best_score:
                best_score = score
                best_sentence = sentence
                best_matching_words = matching_words

        if best_sentence is None:
            return {
                "claim": claim,
                "status": "UNSUPPORTED",
                "score": 0.0,
                "matching_words": [],
                "contradiction": False,
                "matched_evidence": None
            }

        has_negation_difference = (
            self.detect_contradiction(
                claim,
                best_sentence
            )
        )

        is_contradiction = (
            has_negation_difference
            and best_score >= 0.6
        )

        if is_contradiction:
            status = "CONTRADICTED"

        elif best_score >= 0.6:
            status = "SUPPORTED"

        elif best_score >= 0.3:
            status = "PARTIALLY_SUPPORTED"

        else:
            status = "UNSUPPORTED"

        return {
            "claim": claim,
            "status": status,
            "score": best_score,
            "matching_words": best_matching_words,
            "contradiction": is_contradiction,
            "matched_evidence": best_sentence
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

    def prepare_sources_from_retrieval(self, retrieval_output):
        """
        Convert the Retrieval Agent output into the source
        format required by the Verification Agent.
        """

        sources = []

        if not isinstance(retrieval_output, dict):
            return sources

        retrieval_results = retrieval_output.get(
            "results",
            []
        )

        for result in retrieval_results:

            text = result.get("text", "").strip()

            if not text:
                continue

            filename = result.get(
                "filename",
                "unknown_source"
            )

            page_number = result.get(
                "page_number",
                "unknown"
            )

            chunk_number = result.get(
                "chunk_number",
                "unknown"
            )

            source_name = (
                f"{filename} "
                f"(page {page_number}, chunk {chunk_number})"
            )

            sources.append({
                "source": source_name,
                "text": text,
                "filename": filename,
                "page_number": page_number,
                "chunk_number": chunk_number,
                "chunk_id": result.get("chunk_id"),
                "retrieval_score": result.get("score")
            })

        return sources

    def extract_analysis_claims(self, analysis_output):
        """
        Extract verifiable claims from the structured
        output produced by the Analysis Agent.
        """

        claims = []

        if not isinstance(analysis_output, dict):
            return claims

        summary = analysis_output.get(
            "summary",
            ""
        )

        for claim in self.extract_claims(summary):
            claims.append({
                "section": "summary",
                "claim": claim
            })

        key_findings = analysis_output.get(
            "key_findings",
            []
        )

        for finding in key_findings:

            for claim in self.extract_claims(finding):
                claims.append({
                    "section": "key_findings",
                    "claim": claim
                })

        methods = analysis_output.get(
            "methods",
            []
        )

        for method in methods:

            if method and method.strip():
                claims.append({
                    "section": "methods",
                    "claim": method.strip()
                })

        conclusion = analysis_output.get(
            "conclusion",
            ""
        )

        for claim in self.extract_claims(conclusion):
            claims.append({
                "section": "conclusion",
                "claim": claim
            })

        return claims

    def verify_analysis_output(
        self,
        analysis_output,
        retrieval_output
    ):
        """
        Verify the actual Analysis Agent output against
        evidence returned by the Retrieval Agent.
        """

        sources = self.prepare_sources_from_retrieval(
            retrieval_output
        )

        analysis_claims = self.extract_analysis_claims(
            analysis_output
        )

        results = []

        for item in analysis_claims:

            verification = (
                self.hybrid_verify_against_sources(
                    item["claim"],
                    sources
                )
            )

            verification["section"] = item["section"]

            results.append(verification)

        verified_claims = sum(
            1
            for result in results
            if result["final_status"] == "SUPPORTED"
        )

        partially_supported_claims = sum(
            1
            for result in results
            if result["final_status"]
            == "PARTIALLY_SUPPORTED"
        )

        contradicted_claims = sum(
            1
            for result in results
            if result["final_status"]
            == "CONTRADICTED"
        )

        insufficient_claims = sum(
            1
            for result in results
            if result["final_status"] in {
                "UNSUPPORTED",
                "NOT_ENOUGH_EVIDENCE"
            }
        )

        conflicting_claims = sum(
            1
            for result in results
            if result["final_status"]
            == "CONFLICTING_EVIDENCE"
        )

        if not results:
            overall_status = "UNVERIFIED"

        elif verified_claims == len(results):
            overall_status = "VERIFIED"

        elif verified_claims == 0:
            overall_status = "UNVERIFIED"

        else:
            overall_status = "PARTIALLY_VERIFIED"

        return {
            "overall_status": overall_status,
            "total_claims": len(results),
            "verified_claims": verified_claims,
            "partially_supported_claims":
                partially_supported_claims,
            "contradicted_claims":
                contradicted_claims,
            "insufficient_evidence_claims":
                insufficient_claims,
            "conflicting_claims":
                conflicting_claims,
            "claims": results
        }

    def split_into_sentences(self, text):
        """
        Split evidence into smaller sentences for
        more reliable rule-based verification.
        """

        if not text:
            return []

        sentences = re.split(
            r'(?<=[.!?])\s+',
            text.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]
    def calculate_overlap_score(self, claim, evidence):
        """
        Calculate lexical overlap between a claim
        and one piece of evidence.
        """

        claim_words = self.get_important_words(claim)
        evidence_words = self.get_important_words(evidence)

        if not claim_words:
            return 0.0, []

        matching_words = claim_words.intersection(
            evidence_words
        )

        score = (
            len(matching_words)
            / len(claim_words)
        )

        return round(score, 2), list(matching_words)

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
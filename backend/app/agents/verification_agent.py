from app.services.verification_service import VerificationService


class VerificationAgent:
    """
    Verifies AI-generated answers against
    retrieved scientific research evidence.
    """

    def __init__(self):
        self.verification_service = VerificationService()

    def verify(self, claim, evidence):
        """
        Send the claim and evidence to the verification service.
        """

        result = self.verification_service.verify_claim(
            claim,
            evidence
        )

        return result

    def verify_with_sources(self, claim, sources):
        """
        Verify a claim against multiple scientific sources.
        """

        result = self.verification_service.verify_against_sources(
            claim,
            sources
        )

        return result

    def verify_answer(self, answer, sources):
        """
        Verify a complete AI-generated answer.
        """

        result = self.verification_service.verify_answer(
            answer,
            sources
        )

        return result


if __name__ == "__main__":

    agent = VerificationAgent()

    claim = (
        "The technique increases predictive performance."
    )

    evidence = (
        "The experiment used a ResNet-50 architecture "
        "and was trained for 100 epochs."
    )

    result = (
        agent.verification_service
        .semantic_verify_claim(
            claim,
            evidence
        )
    )

    print(result)
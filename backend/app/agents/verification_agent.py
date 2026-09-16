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


if __name__ == "__main__":

    agent = VerificationAgent()

    claim = (
        "Contrastive learning improves transferability."
    )

    evidence = (
        "The study found that contrastive learning "
        "demonstrated improved transferability "
        "across downstream tasks."
    )

    result = agent.verify(claim, evidence)

    print(result)
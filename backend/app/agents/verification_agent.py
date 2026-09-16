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


if __name__ == "__main__":

    agent = VerificationAgent()

    claim = (
        "Contrastive learning improves transferability."
    )

    sources = [
        {
            "source": "paper1.txt",
            "text": (
                "The study found that contrastive learning "
                "demonstrated improved transferability "
                "across downstream tasks."
            )
        },
        {
            "source": "paper2.txt",
            "text": (
                "Supervised learning achieved strong results "
                "on specialized classification tasks."
            )
        },
        {
            "source": "paper3.txt",
            "text": (
                "Deep neural networks require significant "
                "computational resources for training."
            )
        }
    ]

    result = agent.verify_with_sources(
        claim,
        sources
    )

    print(result)
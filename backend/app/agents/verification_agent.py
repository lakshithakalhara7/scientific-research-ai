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
    def hybrid_verify_answer(self, answer, sources):
        """
        Run hybrid verification on a complete AI-generated answer.
        """

        return self.verification_service.hybrid_verify_answer(
            answer,
            sources
        )
    def verify_analysis(
        self,
        analysis_output,
        retrieval_output
    ):
        """
        Verify the Analysis Agent output against
        Retrieval Agent evidence.
        """

        return self.verification_service.verify_analysis_output(
            analysis_output,
            retrieval_output
        )
if __name__ == "__main__":

    from pprint import pprint

    agent = VerificationAgent()

    answer = (
        "Contrastive learning improves transferability. "
        "Supervised learning performs strongly on "
        "specialized classification tasks. "
        "The dataset contained one million medical images."
    )

    sources = [
        {
            "source": "paper1.txt",
            "text": (
                "The proposed contrastive learning approach "
                "showed improved transfer performance across "
                "multiple downstream datasets."
            )
        },
        {
            "source": "paper2.txt",
            "text": (
                "Supervised learning achieved strong performance "
                "on specialized classification tasks."
            )
        },
        {
            "source": "paper3.txt",
            "text": (
                "The experiments used a ResNet-50 architecture "
                "trained for 100 epochs."
            )
        }
    ]

    result = agent.hybrid_verify_answer(
        answer,
        sources
    )

    pprint(result)
from pprint import pprint

from app.agents.retrieval_agent import RetrievalAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.verification_agent import VerificationAgent


question = (
    "What machine learning methods are used "
    "for disease prediction and detection?"
)


# ---------------------------------
# Member 01 - Retrieval
# ---------------------------------

retrieval_agent = RetrievalAgent()

retrieval_output = retrieval_agent.run(
    question,
    top_k=3
)

print("\n========== RETRIEVAL ==========\n")

pprint(retrieval_output)


if not retrieval_output.get("results"):
    print("No research evidence was retrieved.")
    raise SystemExit


# ---------------------------------
# Member 02 - Analysis
# ---------------------------------

chunks = [
    result["text"]
    for result in retrieval_output["results"]
]


analysis_agent = AnalysisAgent()

try:
    analysis_output = analysis_agent.analyze(
        question,
        chunks
    )

except Exception as error:

    print("\nAnalysis Agent unavailable.")
    print("Reason:", type(error).__name__)
    print("Using temporary analysis output for integration testing.\n")

    analysis_output = {
        "summary": (
            "Deep learning approaches are widely used "
            "for cancer prediction and detection."
        ),

        "key_findings": [
            (
                "Convolutional neural networks are commonly "
                "used for cancer prediction."
            ),
            (
                "Support vector machines and ensemble learning "
                "methods are also used in cancer research."
            )
        ],

        "methods": [
            "Convolutional neural networks",
            "Support vector machines",
            "Transfer learning",
            "Ensemble learning"
        ],

        "conclusion": (
            "Several deep learning and machine learning methods "
            "are used for cancer detection and prediction."
        )
    }

print("\n========== ANALYSIS ==========\n")

pprint(analysis_output)


# ---------------------------------
# Member 03 - Verification
# ---------------------------------

verification_agent = VerificationAgent()

verification_output = (
    verification_agent.verify_analysis(
        analysis_output,
        retrieval_output
    )
)

print("\n========== VERIFICATION ==========\n")

pprint(verification_output)
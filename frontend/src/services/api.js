const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";


// Search research
export async function searchResearch(query) {

  /*
   * TEMPORARY DEMO DATA
   *
   * Replace this section with the real backend API
   * once your group provides the endpoint.
   */

  console.log("Research query:", query);

  await new Promise((resolve) =>
    setTimeout(resolve, 1500)
  );


  return {

    papers: [

      {
        id: 1,
        title: "Applications of Machine Learning in Healthcare",
        authors: "Example Research Authors",
        abstract:
          "This is demonstration data. The actual research paper information will come from the Information Retrieval agent.",
        score: 0.92,
        year: 2025,
        source: "#"
      },

      {
        id: 2,
        title: "Artificial Intelligence for Modern Healthcare",
        authors: "Example Research Authors",
        abstract:
          "This is demonstration data used to test the frontend before backend API integration.",
        score: 0.87,
        year: 2024,
        source: "#"
      },

      {
        id: 3,
        title: "Deep Learning Applications in Medical Research",
        authors: "Example Research Authors",
        abstract:
          "The real system will display papers retrieved by the research retrieval agent.",
        score: 0.81,
        year: 2024,
        source: "#"
      }

    ],


    analysis: {

      summary:
        "Machine learning and artificial intelligence are increasingly being applied to healthcare research and clinical applications. These technologies can support diagnosis, prediction, medical imaging, and decision-making.",

      findings:
        "The retrieved research indicates that machine learning can be applied to several healthcare tasks. However, research quality, data quality, model reliability, and appropriate validation remain important considerations.",

      comparison:
        "Different studies focus on different healthcare applications and datasets. Their results should therefore be interpreted according to the specific research context."

    },


    verification: [

      {
        claim:
          "Machine learning is being applied in healthcare research.",
        status: "verified",
        explanation:
          "The claim is supported by the retrieved research papers.",
        source: "#"
      },

      {
        claim:
          "AI can support healthcare decision-making.",
        status: "warning",
        explanation:
          "This claim requires checking against the specific evidence and context of the retrieved studies.",
        source: "#"
      }

    ]

  };
}



// Upload PDF
export async function uploadPdf(file) {

  console.log("Uploading:", file.name);


  /*
   * TEMPORARY DEMO
   *
   * Replace this with the real backend upload API.
   */

  await new Promise((resolve) =>
    setTimeout(resolve, 1200)
  );


  return {
    success: true,
    message: `${file.name} is ready for research analysis.`
  };


  /*
   * REAL API VERSION WILL LOOK LIKE:

   const formData = new FormData();
   formData.append("file", file);

   const response = await fetch(
     `${API_BASE_URL}/upload`,
     {
       method: "POST",
       body: formData
     }
   );

   if (!response.ok) {
     throw new Error("PDF upload failed");
   }

   return await response.json();

   */
}



// Optional health check
export async function checkBackend() {

  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  if (!response.ok) {
    throw new Error("Backend is unavailable");
  }

  return await response.json();
}
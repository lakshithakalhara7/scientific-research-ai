/* =========================================================
   RESOMIND API SERVICE
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


/* =========================================================
   ERROR HANDLING
========================================================= */

const getErrorMessage = async (response) => {
  try {
    const data = await response.json();

    if (data?.detail) {
      if (typeof data.detail === "string") {
        return data.detail;
      }

      return JSON.stringify(data.detail);
    }

    if (data?.message) {
      return data.message;
    }
  } catch {
    // Response did not contain JSON.
  }

  return `Request failed with status ${response.status}.`;
};


/* =========================================================
   AUTH HEADER
========================================================= */

/*
  Protected backend endpoints require:

  Authorization: Bearer <Supabase access token>

  We will connect this function to the real Supabase session
  in the next authentication step.
*/

const getAuthHeaders = (accessToken) => {
  if (!accessToken) {
    throw new Error(
      "You must be signed in before using this feature."
    );
  }

  return {
    Authorization: `Bearer ${accessToken}`,
  };
};


/* =========================================================
   HEALTH CHECK
========================================================= */

export const checkBackendHealth = async () => {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new Error(message);
  }

  return await response.json();
};


/* =========================================================
   DOCUMENT UPLOAD
========================================================= */

/*
  Backend:
  POST /documents/upload

  Multipart fields:
    file       -> required
    category   -> optional
    title      -> optional
    doi        -> optional
    source_url -> optional

  IMPORTANT:
  Do not manually set Content-Type for FormData.
  The browser generates the multipart boundary.
*/

export const uploadDocument = async (
  file,
  accessToken,
  metadata = {}
) => {
  if (!file) {
    throw new Error(
      "Please select a PDF file."
    );
  }

  if (
    file.type &&
    file.type !== "application/pdf"
  ) {
    throw new Error(
      "Only PDF files are allowed."
    );
  }

  // Backend limit: 25,000,000 bytes.
  const MAX_PDF_SIZE_BYTES = 25_000_000;

  if (file.size > MAX_PDF_SIZE_BYTES) {
    throw new Error(
      "PDF exceeds the 25 MB upload limit."
    );
  }

  const formData = new FormData();

  formData.append("file", file);

  if (metadata.category) {
    formData.append(
      "category",
      metadata.category
    );
  }

  if (metadata.title) {
    formData.append(
      "title",
      metadata.title
    );
  }

  if (metadata.doi) {
    formData.append(
      "doi",
      metadata.doi
    );
  }

  if (metadata.sourceUrl) {
    formData.append(
      "source_url",
      metadata.sourceUrl
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",

      headers: {
        ...getAuthHeaders(accessToken),
      },

      body: formData,
    }
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new Error(message);
  }

  return await response.json();
};


/* =========================================================
   RESEARCH WORKFLOW
========================================================= */

/*
  Backend:
  POST /research

  Body:
  {
    question: string,
    document_id: string | null,
    top_k: number
  }

  The backend then runs:

  Security
      ↓
  Retrieval Agent
      ↓
  Analysis Agent
      ↓
  Verification Agent
*/

export const searchResearch = async (
  question,
  accessToken,
  documentId = null,
  topK = 3
) => {
  if (!question || !question.trim()) {
    throw new Error(
      "Research question is required."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}/research`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(accessToken),
      },

      body: JSON.stringify({
        question: question.trim(),
        document_id: documentId,
        top_k: topK,
      }),
    }
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new Error(message);
  }

  return await response.json();
};


/* =========================================================
   TEMPORARY BACKWARD-COMPATIBILITY FUNCTION
========================================================= */

/*
  Your existing Research.js / PdfUpload.js may still import
  analyzePdf().

  Keeping this export temporarily prevents Vite from failing
  while we migrate the UI to uploadDocument().
*/

export const analyzePdf = async (
  file,
  accessToken
) => {
  return uploadDocument(
    file,
    accessToken
  );
};
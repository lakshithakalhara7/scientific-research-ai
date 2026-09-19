import { useRef, useState } from "react";
import "./PdfUpload.css";

function PdfUpload({ onClose, onAnalyze }) {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);

  // ==========================================
  // OPEN FILE PICKER
  // ==========================================

  const openFilePicker = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  // ==========================================
  // VALIDATE FILE
  // ==========================================

  const validateFile = (file) => {
    setError("");

    if (!file) {
      return;
    }

    const isPdf =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      setSelectedFile(null);
      setError("Please select a PDF file only.");
      return;
    }

    // Maximum size = 20 MB
    const maxSize = 20 * 1024 * 1024;

    if (file.size > maxSize) {
      setSelectedFile(null);
      setError("PDF must be smaller than 20 MB.");
      return;
    }

    setSelectedFile(file);
  };

  // ==========================================
  // FILE INPUT
  // ==========================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      validateFile(file);
    }
  };

  // ==========================================
  // DRAG & DROP
  // ==========================================

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      validateFile(file);
    }
  };

  // ==========================================
  // REMOVE FILE
  // ==========================================

  const removeFile = () => {
    setSelectedFile(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // ==========================================
  // ANALYZE
  // ==========================================

  const handleAnalyze = () => {
    if (!selectedFile) {
      setError("Please select a PDF first.");
      return;
    }

    onAnalyze(selectedFile);
  };

  // ==========================================
  // FORMAT FILE SIZE
  // ==========================================

  const formatFileSize = (bytes) => {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div
      className="pdf-modal-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="pdf-modal">

        {/* REAL FILE INPUT */}

        <input
          ref={fileInputRef}
          className="pdf-hidden-input"
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
        />

        {/* HEADER */}

        <div className="pdf-modal-header">

          <div>
            <span className="pdf-label">
              DOCUMENT ANALYSIS
            </span>

            <h2>Analyze Research Paper</h2>

            <p>
              Upload a scientific paper and ResoMind will
              prepare it for intelligent document analysis.
            </p>
          </div>

          <button
            type="button"
            className="pdf-close"
            onClick={onClose}
            aria-label="Close PDF upload"
          >
            ×
          </button>

        </div>

        {/* UPLOAD AREA */}

        {!selectedFile && (
          <div
            className={
              dragging
                ? "pdf-dropzone dragging"
                : "pdf-dropzone"
            }
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >

            <div className="pdf-upload-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 16V4M7 9L12 4L17 9"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                <path
                  d="M5 15V19C5 20.1 5.9 21 7 21H17C18.1 21 19 20.1 19 19V15"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>

            </div>

            <h3>Upload your research paper</h3>

            <p>
              Drag and drop your PDF here or choose a
              document from your computer.
            </p>

            <button
              type="button"
              className="browse-pdf"
              onClick={openFilePicker}
            >
              Choose PDF
            </button>

            <small>
              PDF documents only • Maximum 20 MB
            </small>

          </div>
        )}

        {/* SELECTED FILE */}

        {selectedFile && (
          <div className="selected-file-area">

            <div className="selected-pdf">

              <div className="selected-pdf-icon">
                PDF
              </div>

              <div className="selected-pdf-info">

                <strong>
                  {selectedFile.name}
                </strong>

                <span>
                  {formatFileSize(selectedFile.size)}
                </span>

              </div>

              <div className="selected-ready">
                ✓ Ready
              </div>

              <button
                type="button"
                className="remove-pdf"
                onClick={removeFile}
                aria-label="Remove PDF"
              >
                ×
              </button>

            </div>

            <button
              type="button"
              className="change-pdf-button"
              onClick={openFilePicker}
            >
              Choose another PDF
            </button>

          </div>
        )}

        {/* ERROR */}

        {error && (
          <div className="pdf-error">
            <span>!</span>

            <p>{error}</p>
          </div>
        )}

        {/* PROCESS */}

        <div className="pdf-analysis-features">

          <div>
            <span>01</span>

            <strong>Extract</strong>

            <p>
              Extract text and research sections
              from the uploaded document.
            </p>
          </div>

          <div>
            <span>02</span>

            <strong>Analyze</strong>

            <p>
              Identify methods, findings,
              limitations and important concepts.
            </p>
          </div>

          <div>
            <span>03</span>

            <strong>Verify</strong>

            <p>
              Review important claims using
              supporting scientific evidence.
            </p>
          </div>

        </div>

        {/* ACTIONS */}

        <div className="pdf-modal-actions">

          <button
            type="button"
            className="pdf-cancel"
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            type="button"
            className="pdf-analyze"
            disabled={!selectedFile}
            onClick={handleAnalyze}
          >
            Analyze Paper

            <span>→</span>
          </button>

        </div>

      </div>
    </div>
  );
}

export default PdfUpload;
function PdfUpload({ selectedFile, setSelectedFile, onUpload, uploading }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed.");
      event.target.value = "";
      return;
    }

    const maxSize = 10 * 1024 * 1024;

    if (file.size > maxSize) {
      alert("PDF file must be smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  return (
    <section className="upload-section">
      <div className="upload-header">
        <div>
          <span className="eyebrow">DOCUMENT ANALYSIS</span>
          <h2>Analyze a Research Paper</h2>
          <p>
            Upload a scientific paper and let the AI research agents
            extract and analyze its content.
          </p>
        </div>

        <div className="document-icon">PDF</div>
      </div>

      <label className="drop-zone">
        <input
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          hidden
        />

        <div className="upload-symbol">↑</div>

        <strong>Drop your PDF here</strong>
        <span>or click to browse from your computer</span>

        <small>PDF • Maximum 10 MB</small>
      </label>

      {selectedFile && (
        <div className="selected-file-modern">
          <div className="file-left">
            <div className="file-icon">PDF</div>

            <div>
              <strong>{selectedFile.name}</strong>
              <span>
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>
          </div>

          <button
            className="upload-button-modern"
            onClick={onUpload}
            disabled={uploading}
          >
            {uploading ? "Analyzing..." : "Analyze PDF →"}
          </button>
        </div>
      )}
    </section>
  );
}

export default PdfUpload;
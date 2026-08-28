/* ==========================================================================
   Django RAG Application - Document Upload & Ingestion Handler
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('id_file');
    const fileNameDisplay = document.getElementById('selected-file-name');
    const uploadForm = document.getElementById('document-upload-form');
    const uploadSubmitBtn = document.getElementById('upload-submit-btn');

    if (dropzone && fileInput) {
        // Clicking anywhere in dropzone triggers file picker
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag & Drop visual states
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');

            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                updateFileDisplay();
            }
        });

        fileInput.addEventListener('change', () => {
            updateFileDisplay();
        });
    }

    function updateFileDisplay() {
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

            if (fileNameDisplay) {
                fileNameDisplay.innerHTML = `
                    <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:8px; color:#6ee7b7;">
                        <span>✓ Ready:</span>
                        <strong style="color:#ffffff;">${file.name}</strong>
                        <span style="opacity:0.75; font-size:11px;">(${sizeMB} MB)</span>
                    </div>
                `;
            }
            dropzone.style.borderColor = 'rgba(16, 185, 129, 0.5)';
            dropzone.style.background = 'rgba(16, 185, 129, 0.05)';
        }
    }

    if (uploadForm && uploadSubmitBtn) {
        uploadForm.addEventListener('submit', (e) => {
            // Validation: Ensure file is selected
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                dropzone.style.borderColor = '#f43f5e';
                dropzone.style.background = 'rgba(244, 63, 94, 0.08)';
                if (fileNameDisplay) {
                    fileNameDisplay.innerHTML = `
                        <span style="color:#fda4af; font-weight:600; font-size:12.5px;">
                            ⚠️ Please select or drop a document before clicking Ingest!
                        </span>
                    `;
                }
                fileInput.click();
                return;
            }

            // Show loading state on button
            uploadSubmitBtn.disabled = true;
            uploadSubmitBtn.style.opacity = '0.8';
            uploadSubmitBtn.innerHTML = `
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation: spin 1s linear infinite;">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <span>Parsing & Vectorizing into ChromaDB...</span>
            `;
        });
    }
});

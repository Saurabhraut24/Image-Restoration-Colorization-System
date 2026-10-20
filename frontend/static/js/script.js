document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const processBtn = document.getElementById('process-btn');
    const originalPreview = document.getElementById('original-preview');
    const resultImage = document.getElementById('result-image');
    const resultSection = document.getElementById('result-section');
    const loader = document.getElementById('loader');
    const downloadBtn = document.getElementById('download-btn');
    const restoreToggle = document.getElementById('restore-toggle');
    const colorToggle = document.getElementById('color-toggle');

    let selectedFile = null;

    // Trigger file input
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        selectedFile = file;
        processBtn.disabled = false;

        // Preview original
        const reader = new FileReader();
        reader.onload = (e) => {
            originalPreview.src = e.target.result;
            resultSection.style.display = 'block';
            resultImage.style.display = 'none';
            downloadBtn.style.display = 'none';
            window.scrollTo({ top: resultSection.offsetTop, behavior: 'smooth' });
        };
        reader.readAsDataURL(file);
    }

    // Process button click
    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Reset UI
        loader.style.display = 'block';
        resultImage.style.display = 'none';
        downloadBtn.style.display = 'none';
        processBtn.disabled = true;

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('restore', restoreToggle.checked);
        formData.append('color', colorToggle.checked);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                resultImage.src = data.image;
                resultImage.style.display = 'block';
                downloadBtn.href = data.image;
                downloadBtn.download = 'restored_photo.png';
                downloadBtn.style.display = 'inline-block';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Something went wrong. Please try again.');
        } finally {
            loader.style.display = 'none';
            processBtn.disabled = false;
        }
    });
});

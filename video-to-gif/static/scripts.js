// Updated JavaScript
document.getElementById('uploadButton').addEventListener('click', () => {
    const videoFile = document.getElementById('videoUpload').files[0];
    const caption = document.getElementById('caption').value;
    const style = document.getElementById('style').value;

    if (videoFile) {
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('caption', caption);
        formData.append('style', style);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const gifContainer = document.getElementById('gifContainer');
            gifContainer.innerHTML = '';
            data.gifs.forEach(gif => {
                const img = document.createElement('img');
                img.src = gif.url;
                gifContainer.appendChild(img);
            });
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('Please select a video file to upload.');
    }
});

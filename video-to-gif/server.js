// server.js
const express = require('express');
const multer = require('multer');
const path = require('path');
const { exec } = require('child_process');
const cors = require('cors');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.static('public'));

app.post('/upload', upload.single('video'), (req, res) => {
    const videoPath = req.file.path;
    const outputDir = path.join(__dirname, 'public', 'gifs');

    // Call Python script to process video
    exec(`python3 process_video.py ${videoPath} ${outputDir}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error.message}`);
            return res.status(500).send('Error processing video');
        }

        const gifs = JSON.parse(stdout);
        res.json({ gifs });
    });
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});


My project, "Video to GIF Converter," is a web application built using Flask that allows users to upload a video file and convert it into a GIF. The application also extracts the audio from the video, uses speech recognition to convert the audio to text, and adds this text as a caption to the generated GIF. The main components of the project include video processing, audio extraction, speech recognition, and GIF creation.

What the Project Does

1. Video Upload and Processing:
   - Users upload a video file through a form on the web interface.
   - The video file is saved to the server and keyframes are extracted from the video.

2. Audio Extraction:
   - The audio from the uploaded video is extracted and saved as a separate file.

3. Speech Recognition:
   - The extracted audio is processed using a speech recognition service (Google Speech Recognition in this case).
   - The recognized text is then used as a caption for the GIF.

4. GIF Creation:
   - Keyframes from the video are resized and used to create a sequence of images.
   - The recognized text is added as a caption to each frame.
   - These captioned frames are then combined to create a GIF.
   - The GIF is made available for download.

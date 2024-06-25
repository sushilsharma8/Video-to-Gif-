import os
import shutil
from flask import Flask, request, render_template, send_from_directory
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, ImageSequenceClip
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont, ImageSequence

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)

    segments_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'segments')
    os.makedirs(segments_folder, exist_ok=True)

    segment_duration = 5  # seconds
    segment_files = split_video(video_path, segments_folder, segment_duration)

    gifs = []
    for segment_file in segment_files:
        frames_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'frames')
        os.makedirs(frames_folder, exist_ok=True)
        output_gif = os.path.join(app.config['STATIC_FOLDER'], f'{os.path.splitext(os.path.basename(segment_file))[0]}.gif')

        extract_keyframes(segment_file, frames_folder)
        audio_path = extract_audio(segment_file)
        recognized_text = recognize_audio(audio_path)
        caption = recognized_text
        generate_gif(frames_folder, output_gif, caption)
        gifs.append(output_gif)
        shutil.rmtree(frames_folder, ignore_errors=True)

    return render_template('result.html', gifs=gifs)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename, as_attachment=True)

def split_video(video_path, segments_folder, segment_duration):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    segment_files = []

    for i in range(0, int(duration), segment_duration):
        start = i
        end = min(i + segment_duration, duration)
        segment_path = os.path.join(segments_folder, f'segment_{i}.mp4')
        clip.subclip(start, end).write_videofile(segment_path, codec='libx264')
        segment_files.append(segment_path)

    return segment_files

def extract_keyframes(video_path, frames_folder):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    print(f"Video duration: {duration} seconds")

    for t in range(0, int(duration)):
        frame_path = os.path.join(frames_folder, f"frame_{t}.png")
        clip.save_frame(frame_path, t)
        print(f"Extracted frame at {t} seconds")

def extract_audio(video_path):
    clip = VideoFileClip(video_path)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_audio.wav')
    clip.audio.write_audiofile(audio_path)
    print(f"Audio extracted to: {audio_path}")
    return audio_path

def recognize_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized text: {text}")
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def clear_uploads_folder(uploads_folder):
    for filename in os.listdir(uploads_folder):
        file_path = os.path.join(uploads_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def generate_gif(frames_folder, output_gif, caption):
    frame_files = sorted([os.path.join(frames_folder, f) for f in os.listdir(frames_folder) if f.endswith('.png')])
    sample_frame = Image.open(frame_files[0])
    width, height = sample_frame.size
    target_size = (width, height)
    print(f"Target frame size: {target_size}")
    sample_frame.close()

    for frame_file in frame_files:
        frame_image = Image.open(frame_file)
        frame_image = frame_image.resize(target_size, Image.BICUBIC)  # Ensure all frames have the same size
        frame_image.save(frame_file)
        frame_image.close()

    frames = ImageSequenceClip(frame_files, fps=50)

    # Create an image with caption for each frame
    captioned_frames = []
    for frame_file in frame_files:
        frame_image = Image.open(frame_file)
        draw = ImageDraw.Draw(frame_image)
        font_path = "Super Impacto.otf"
        font = ImageFont.truetype(font_path, 160, encoding="unic")
        bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (frame_image.width - text_width) // 2
        y = frame_image.height - text_height - 20
        draw.text((x, y), caption, font=font, fill="white")
        captioned_frame_file = frame_file.replace("frame_", "captioned_frame_")
        frame_image.save(captioned_frame_file)
        captioned_frames.append(captioned_frame_file)
        frame_image.close()

    captioned_clip = ImageSequenceClip(captioned_frames, fps=50)
    captioned_clip.write_gif(output_gif)
    print(f"GIF generated at: {output_gif}")

    # Clear the uploads folder after generating the GIF
    clear_uploads_folder(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)

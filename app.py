from flask import Flask, request, jsonify
import librosa
import numpy as np
import pickle
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from moviepy.editor import VideoFileClip

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model and RFE selector
with open('model/dog_bark_classifier33.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('model/rfe_selector.pkl', 'rb') as rfe_file:
    rfe = pickle.load(rfe_file)

# Function to extract features from audio
def extract_features(y, sr):
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=10)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    return np.concatenate((np.mean(mfccs.T, axis=0), 
                           np.mean(chroma.T, axis=0),
                           np.mean(spectral_contrast.T, axis=0)))

# Default route to show backend is running
@app.route('/')
def index():
    return "<h1>Backend is running</h1>" 

@app.route('/predict', methods=['POST'])
def predict():
    if 'videofile' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['videofile']
    
    # Log file details for debugging
    print(f"Received file: {file.filename}, MIME type: {file.mimetype}")

    # Check MIME type to confirm it's a video file
    if file and file.mimetype.startswith('video/'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Extract audio from the video
        try:
            video = VideoFileClip(filepath)
            audio_path = os.path.join('uploads', 'extracted_audio.wav')
            video.audio.write_audiofile(audio_path)
        except Exception as e:
            return jsonify({"error": f"Error extracting audio: {str(e)}"}), 500

        # Process the extracted audio
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            features = extract_features(y, sr)
            features_rfe = rfe.transform(features.reshape(1, -1))

            prediction = model.predict(features_rfe)[0]

            return jsonify({"prediction": prediction})
        except Exception as e:
            return jsonify({"error": f"Error processing audio: {str(e)}"}), 500
        finally:
            # Clean up extracted audio
            if os.path.exists(audio_path):
                os.remove(audio_path)

    return jsonify({"error": "Only video files are accepted"}), 400

if __name__ == '__main__':
    # Ensure uploads folder exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host='0.0.0.0', port=443)  # Change host to '0.0.0.0'

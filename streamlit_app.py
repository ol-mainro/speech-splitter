import streamlit as st
import os
import tempfile
import base64
from math import floor
import mimetypes
import logging
import zipfile
import io
from pydub import AudioSegment
from pydub.utils import mediainfo
import moviepy.editor as mp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Clap Studio Speech Splitter",
    page_icon="🎵",
    layout="wide"
)

def check_openai_key():
    """Check if OpenAI API key is available"""
    if "OPENAI_API_KEY" not in os.environ:
        st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    return True

def import_speech_splitter():
    """Import speech splitter functions only when needed"""
    from speech_splitter.splitter import (
        transcribe_audio, 
        split_text_into_sentences, 
        get_sentences_as_audio,
        split_text_into_words
    )
    return transcribe_audio, split_text_into_sentences, get_sentences_as_audio, split_text_into_words

def process_audio_file(uploaded_file):
    """Process the uploaded audio file and return transcription results"""
    
    # Check OpenAI API key first
    check_openai_key()
    
    # Import speech splitter functions
    transcribe_audio, split_text_into_sentences, get_sentences_as_audio, split_text_into_words = import_speech_splitter()
    
    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name
    
    try:
        # Determine content type and process accordingly
        content_type = mimetypes.guess_type(temp_path)[0]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            if content_type and content_type.startswith("video"):
                st.info("Input file is a video file. Extracting audio...")
                # Extract audio from video
                audio_path = os.path.join(temp_dir, "audio.mp3")
                video = mp.VideoFileClip(temp_path)
                video.audio.write_audiofile(audio_path)
                os.unlink(temp_path)  # Clean up original file
                temp_path = audio_path
            elif content_type and content_type.startswith("audio"):
                st.info("Input file is an audio file.")
                audio_path = temp_path
            else:
                st.error("Error: Input file is not a valid audio or video file.")
                return None
            
            # Load the original audio for accurate sentence splitting
            audio = AudioSegment.from_file(audio_path)
            audio_bitrate = mediainfo(audio_path).get("bit_rate", "128")
            
            # Transcribe the audio
            with st.spinner("Transcribing audio..."):
                language, full_text, words = transcribe_audio(audio_path)
            
            st.success("Transcription complete!")
            
            # Split the transcribed text into sentences
            with st.spinner("Splitting text into sentences..."):
                sentences = split_text_into_sentences(full_text, language)
            
            # Get sentences as audio segments
            with st.spinner("Processing audio segments..."):
                audio_sentences = get_sentences_as_audio(sentences, audio, words, language)
            
            return {
                'language': language,
                'full_text': full_text,
                'sentences': sentences,
                'audio_sentences': audio_sentences,
                'original_audio': audio,
                'audio_bitrate': audio_bitrate,
                'title': uploaded_file.name.split('.')[0]
            }
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def create_audio_player(audio_segment, title, audio_bitrate):
    """Create a base64 encoded audio player for a given audio segment"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        audio_segment.export(tmp_file.name, format="wav")
        
        with open(tmp_file.name, "rb") as audio_file:
            encoded = base64.b64encode(audio_file.read()).decode("utf-8")
            src = f"data:audio/wav;base64,{encoded}"
        
        os.unlink(tmp_file.name)
        
        return f"""
        <audio title="{title}" controls style="width: 100%;">
            <source src="{src}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """

def create_zip_with_audio_fragments(result):
    """Create a zip file containing all audio fragments and a transcript"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the full transcript as a text file
        transcript_filename = f"{result['title']}_transcript.txt"
        zip_file.writestr(transcript_filename, result['full_text'])
        
        # Add each audio fragment
        for i, (sentence, audio_item) in enumerate(zip(result['sentences'], result['audio_sentences'])):
            # Create a safe filename from the sentence
            safe_sentence = sentence[:50].replace(' ', '_').replace('/', '_').replace('\\', '_').replace('.', '').replace(',', '').replace('?', '').replace('!', '')
            safe_filename = f"{safe_sentence}.wav"
            
            # Export the audio segment to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                audio_item['audio'].export(tmp_file.name, format="wav")
                
                # Read the file and add it to the zip
                with open(tmp_file.name, "rb") as audio_file:
                    zip_file.writestr(safe_filename, audio_file.read())
                
                # Clean up the temporary file
                os.unlink(tmp_file.name)
        
        # Add a metadata file with timing information
        metadata_content = f"""Audio Fragments Metadata
========================

Title: {result['title']}
Language: {result['language']}
Total Sentences: {len(result['sentences'])}
Audio Format: WAV (uncompressed)

Sentence Details:
"""
        
        for i, (sentence, audio_item) in enumerate(zip(result['sentences'], result['audio_sentences'])):
            metadata_content += f"\n{i+1:03d}. {sentence}\n"
            metadata_content += f"    Start: {audio_item['start_time']:.2f}s\n"
            metadata_content += f"    End: {audio_item['end_time']:.2f}s\n"
            metadata_content += f"    Duration: {audio_item['end_time'] - audio_item['start_time']:.2f}s\n"
        
        zip_file.writestr(f"{result['title']}_metadata.txt", metadata_content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    st.title("🎵 Speech Splitter")
    st.markdown("Upload an audio file to split it into individual sentences with corresponding audio players.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an audio or video file",
        type=['mp3', 'wav', 'm4a', 'ogg', 'mp4', 'avi', 'mov'],
        help="Upload an audio or video file to split into sentences"
    )
    
    if uploaded_file is not None:
        # Process the file
        result = process_audio_file(uploaded_file)
        
        if result:
            st.success("File processed successfully!")
            
            # Display results
            st.subheader(f"Results for: {result['title']}")
            st.write(f"**Language detected:** {result['language']}")
            
            # Download section
            st.subheader("📥 Download Audio Fragments")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("Download all audio fragments as a zip file containing:")
                st.write("• Individual WAV files for each sentence")
                st.write("• Full transcript as text file")
                st.write("• Metadata with timing information")
            
            with col2:
                # Create and provide download button
                zip_data = create_zip_with_audio_fragments(result)
                zip_filename = f"{result['title']}_audio_fragments.zip"
                
                st.download_button(
                    label="📦 Download ZIP",
                    data=zip_data,
                    file_name=zip_filename,
                    mime="application/zip",
                    help="Download all audio fragments and metadata as a zip file"
                )
            
            st.divider()
            
            # Full text section
            with st.expander("📝 Full Transcript", expanded=True):
                st.write(result['full_text'])
            
            # Individual sentences with audio players
            st.subheader("🎧 Sentence-by-Sentence Audio")
            
            # Add autoplay toggle
            col1, col2 = st.columns([1, 4])
            with col1:
                autoplay = st.checkbox("Enable Autoplay", help="Automatically play the next sentence when one ends")
            
            # Create a container for the audio players
            audio_container = st.container()
            
            with audio_container:
                for i, (sentence, audio_item) in enumerate(zip(result['sentences'], result['audio_sentences'])):
                    with st.container():
                        st.markdown(f"**{i+1}.** {sentence}")
                        
                        # Create audio player
                        audio_html = create_audio_player(
                            audio_item['audio'], 
                            f"{sentence[:50].replace(' ', '_').replace('/', '_').replace('\\', '_').replace('.', '').replace(',', '').replace('?', '').replace('!', '')}", 
                            result['audio_bitrate']
                        )
                        st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # Show timing information
                        st.caption(f"Time: {audio_item['start_time']:.2f}s - {audio_item['end_time']:.2f}s")
                        st.divider()
            
            # Add JavaScript for autoplay functionality if enabled
            if autoplay:
                st.markdown("""
                <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const audioElements = document.querySelectorAll('audio');
                    audioElements.forEach((audio, index) => {
                        audio.addEventListener('ended', () => {
                            const nextAudio = audioElements[index + 1];
                            if (nextAudio) {
                                setTimeout(() => {
                                    nextAudio.scrollIntoView({ behavior: 'smooth' });
                                    nextAudio.play();
                                }, 1500);
                            }
                        });
                    });
                });
                </script>
                """, unsafe_allow_html=True)
    
    # Add sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This app uses OpenAI's Whisper model to transcribe audio and split it into individual sentences. 
        Each sentence gets its own audio player for easy listening practice.
        
        **Features:**
        - Supports audio and video files
        - Automatic language detection
        - Sentence-by-sentence audio playback
        - Autoplay functionality
        - Download all fragments as ZIP
        - Responsive design
        """)
        
        st.header("🔧 Requirements")
        st.markdown("""
        - OpenAI API key must be set as environment variable
        - Supported formats: MP3, WAV, M4A, OGG, MP4, AVI, MOV
        """)

if __name__ == "__main__":
    main()

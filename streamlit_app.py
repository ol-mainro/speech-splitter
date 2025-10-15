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
import nltk
nltk.download('punkt_tab')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Clap Studio Speech Splitter",
    page_icon="🎵",
    layout="wide"
)

# Initialize session state for authentication and language
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "language" not in st.session_state:
    st.session_state.language = "fr"  # Default to French

# Translation dictionary
TRANSLATIONS = {
    "en": {
        "access_required": "🔐 Access Required",
        "enter_password": "Please enter the password to access this application:",
        "password_placeholder": "Enter password...",
        "login_button": "🔑 Login",
        "invalid_password": "❌ Invalid password. Please try again.",
        "password_protected": "This application is password protected for security.",
        "speech_splitter_title": "🎵 Speech Splitter",
        "upload_description": "Upload an audio file to split it into individual sentences with corresponding audio players.",
        "choose_file": "Choose an audio or video file",
        "upload_help": "Upload an audio or video file to split into sentences",
        "file_processed": "File processed successfully!",
        "results_for": "Results for:",
        "language_detected": "Language detected:",
        "download_fragments": "📥 Download Audio Fragments",
        "download_description": "Download all audio fragments as a zip file containing:",
        "individual_files": "• Individual WAV files for each sentence",
        "transcript_file": "• Full transcript as text file",
        "metadata_file": "• Metadata with timing information",
        "download_zip": "📦 Download ZIP",
        "full_transcript": "📝 Full Transcript",
        "sentence_audio": "🎧 Sentence-by-Sentence Audio",
        "enable_autoplay": "Enable Autoplay",
        "autoplay_help": "Automatically play the next sentence when one ends",
        "time": "Time:",
        "logout": "🚪 Logout",
        "about": "ℹ️ About",
        "about_description": "This app uses OpenAI's Whisper model to transcribe audio and split it into individual sentences. Each sentence gets its own audio player for easy listening practice.",
        "features": "Features:",
        "features_list": [
            "Supports audio and video files",
            "Automatic language detection",
            "Sentence-by-sentence audio playback",
            "Autoplay functionality",
            "Download all fragments as ZIP"
        ],
        "requirements": "🔧 Requirements",
        "requirements_list": [
            "Supported formats: MP3, WAV, M4A, OGG, MP4, AVI, MOV"
        ]
    },
    "fr": {
        "access_required": "🔐 Accès Requis",
        "enter_password": "Veuillez entrer le mot de passe pour accéder à cette application:",
        "password_placeholder": "Entrez le mot de passe...",
        "login_button": "🔑 Connexion",
        "invalid_password": "❌ Mot de passe invalide. Veuillez réessayer.",
        "password_protected": "Cette application est protégée par mot de passe pour la sécurité.",
        "speech_splitter_title": "🎵 Diviseur de Discours",
        "upload_description": "Téléchargez un fichier audio pour le diviser en phrases individuelles avec des lecteurs audio correspondants. Il est préférable que les phrases dites par le locuteur soient séparées de quelques secondes pour une découpe plus fiable.",
        "choose_file": "Choisir un fichier audio ou vidéo",
        "upload_help": "Téléchargez un fichier audio ou vidéo pour le diviser en phrases",
        "file_processed": "Fichier traité avec succès!",
        "results_for": "Résultats pour:",
        "language_detected": "Langue détectée:",
        "download_fragments": "📥 Télécharger les Fragments Audio",
        "download_description": "Téléchargez tous les fragments audio sous forme de fichier zip contenant:",
        "individual_files": "• Fichiers WAV individuels pour chaque phrase",
        "transcript_file": "• Transcription complète en fichier texte",
        "metadata_file": "• Métadonnées avec informations de timing",
        "download_zip": "📦 Télécharger ZIP",
        "full_transcript": "📝 Transcription Complète",
        "sentence_audio": "🎧 Audio Phrase par Phrase",
        "enable_autoplay": "Activer la Lecture Automatique",
        "autoplay_help": "Lire automatiquement la phrase suivante quand une se termine",
        "time": "Temps:",
        "logout": "🚪 Déconnexion",
        "about": "ℹ️ À Propos",
        "about_description": "Cette application utilise le modèle Whisper d'OpenAI pour transcrire l'audio et le diviser en phrases individuelles. Chaque phrase obtient son propre lecteur audio pour une pratique d'écoute facile.",
        "features": "Fonctionnalités:",
        "features_list": [
            "Supporte les fichiers audio et vidéo",
            "Détection automatique de la langue",
            "Lecture audio phrase par phrase",
            "Fonctionnalité de lecture automatique",
            "Téléchargement de tous les fragments en ZIP"
        ],
        "requirements": "🔧 Exigences",
        "requirements_list": [
            "Formats supportés: MP3, WAV, M4A, OGG, MP4, AVI, MOV"
        ]
    }
}

def get_text(key):
    """Get translated text for current language"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

def switch_language():
    """Switch between languages"""
    if st.session_state.language == "en":
        st.session_state.language = "fr"
    else:
        st.session_state.language = "en"

def check_password():
    """Check if user is authenticated or show password dialog"""
    if not st.session_state.authenticated:
        # Get password from environment variable
        required_password = os.getenv("STREAMLIT_PASSWORD")
        
        if not required_password:
            st.error("⚠️ No password configured. Please set STREAMLIT_PASSWORD environment variable.")
            st.stop()
        
        # Create a centered container for the login form
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Use columns to center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Language selector
            col_lang1, col_lang2 = st.columns([1, 1])
            with col_lang1:
                if st.button("🇺🇸 English", key="lang_en"):
                    st.session_state.language = "en"
                    st.rerun()
            with col_lang2:
                if st.button("🇫🇷 Français", key="lang_fr"):
                    st.session_state.language = "fr"
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Create a nice container for the login form
            st.markdown("""
            <div style="
                background-color: #f0f2f6;
                padding: 2rem;
                border-radius: 10px;
                border: 1px solid #e1e5e9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
            """, unsafe_allow_html=True)
            
            st.markdown(f"## {get_text('access_required')}")
            st.markdown(get_text('enter_password'))
            
            # Password input form
            with st.form("password_form"):
                password_input = st.text_input(
                    "Password:", 
                    type="password", 
                    placeholder=get_text('password_placeholder'),
                    label_visibility="collapsed"
                )
                submitted = st.form_submit_button(get_text('login_button'), use_container_width=True)
                
                if submitted:
                    if password_input == required_password:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error(get_text('invalid_password'))
            
            st.markdown("---")
            st.markdown(f"*{get_text('password_protected')}*")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Stop execution to prevent showing the main app
        st.stop()
    
    return True

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
    # Check authentication first
    check_password()
    
    # Language selector in the top right
    col_title, col_lang = st.columns([4, 1])
    with col_title:
        st.title(get_text('speech_splitter_title'))
    with col_lang:
        if st.button("🇺🇸 EN" if st.session_state.language == "fr" else "🇫🇷 FR"):
            switch_language()
            st.rerun()
    
    st.markdown(get_text('upload_description'))
    
    # File upload
    uploaded_file = st.file_uploader(
        get_text('choose_file'),
        type=['mp3', 'wav', 'm4a', 'ogg', 'mp4', 'avi', 'mov'],
        help=get_text('upload_help')
    )
    
    if uploaded_file is not None:
        # Process the file
        result = process_audio_file(uploaded_file)
        
        if result:
            st.success(get_text('file_processed'))
            
            # Display results
            st.subheader(f"{get_text('results_for')} {result['title']}")
            st.write(f"**{get_text('language_detected')}** {result['language']}")
            
            # Download section
            st.subheader(get_text('download_fragments'))
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(get_text('download_description'))
                st.write(get_text('individual_files'))
                st.write(get_text('transcript_file'))
                st.write(get_text('metadata_file'))
            
            with col2:
                # Create and provide download button
                zip_data = create_zip_with_audio_fragments(result)
                zip_filename = f"{result['title']}_audio_fragments.zip"
                
                st.download_button(
                    label=get_text('download_zip'),
                    data=zip_data,
                    file_name=zip_filename,
                    mime="application/zip",
                    help="Download all audio fragments and metadata as a zip file"
                )
            
            st.divider()
            
            # Full text section
            with st.expander(get_text('full_transcript'), expanded=True):
                st.write(result['full_text'])
            
            # Individual sentences with audio players
            st.subheader(get_text('sentence_audio'))
            
            # Add autoplay toggle
            col1, col2 = st.columns([1, 4])
            with col1:
                autoplay = st.checkbox(get_text('enable_autoplay'), help=get_text('autoplay_help'))
            
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
                        st.caption(f"{get_text('time')} {audio_item['start_time']:.2f}s - {audio_item['end_time']:.2f}s")
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
        # Logout button
        if st.button(get_text('logout'), use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.header(get_text('about'))
        st.markdown(get_text('about_description'))
        
        st.markdown(f"**{get_text('features')}**")
        for feature in get_text('features_list'):
            st.markdown(f"- {feature}")
        
        st.header(get_text('requirements'))
        for requirement in get_text('requirements_list'):
            st.markdown(f"- {requirement}")

if __name__ == "__main__":
    main()

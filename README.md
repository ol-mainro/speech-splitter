# Speech Splitter

![Test](https://github.com/bubenkoff/speech-splitter/actions/workflows/test.yml/badge.svg)
[![PyPI Version](https://img.shields.io/pypi/v/speech-splitter.svg)
](https://pypi.python.org/pypi/speech-splitter)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/speech-splitter)
](https://pypi.python.org/pypi/speech-splitter)
[![Coverage](https://img.shields.io/coveralls/bubenkoff/speech-splitter/main.svg)
](https://coveralls.io/r/bubenkoff/speech-splitter)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description
Speech Splitter is a command-line tool designed to split a speech audio into separate sentences. This tool aims to make it easier for language learners to train the hearing, pronounciation and word accents.

> [!WARNING]
> It uses OpenAI API and requires an API key to work, which is not provided with the package. It can also be quite expensive to use, depending on the size of the provided source.

## Streamlit Web App
This project now includes a Streamlit web application that provides a user-friendly interface for the speech splitting functionality.

### Running the Streamlit App
1. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
   Or using the Makefile:
   ```bash
   make run
   ```

4. Open your browser to `http://localhost:8501` and upload an audio or video file.

### Features
- **File Upload**: Support for audio (MP3, WAV, M4A, OGG) and video (MP4, AVI, MOV) files
- **Automatic Transcription**: Uses OpenAI's Whisper model for accurate transcription
- **Sentence Splitting**: Automatically splits the transcribed text into individual sentences
- **Audio Players**: Each sentence gets its own audio player for easy listening practice
- **Autoplay**: Optional autoplay functionality to play sentences sequentially
- **Download ZIP**: Download all audio fragments as a zip file with metadata
- **Language Detection**: Automatically detects the language of the audio
- **Responsive Design**: Works well on desktop and mobile devices

### Download Package Contents
When you download the ZIP file, it contains:
- **Individual MP3 files**: Each sentence as a separate audio file (numbered and named)
- **Full transcript**: Complete text transcription as a `.txt` file
- **Metadata file**: Detailed information including timing data for each sentence

## Motivation
This tool was developed by request of a Dutch teacher. She wanted to have a tool that would split the audio of a provided source into separate sentences, so that the students could listen to each sentence separately and repeat after it.

## Installation
To install Speech Splitter, follow these steps:

``
pip install speech-splitter
``

It also requires `ffmpeg` to be installed on your system. You can install it using the following command (for Ubuntu):

``
sudo apt-get install ffmpeg
``
or (for macOS or Windows)
``
brew install ffmpeg
``
or (for Windows)
``
choco install ffmpeg
``

## Local installation
``
brew install ffmpeg
python -m venv venv
$ source venv/bin/activate
pip install requirements.txt
pip install .
speech-split audio_sources/audio.mp3 ./output
``

## Usage
After installation, you can use the Speech Splitter tool directly from your command line. The basic command structure is as follows:

``
export OPENAI_API_KEY=your_api_key
``

Optionally, set the organization ID if you have one:

``
export OPENAI_ORG_ID=your_org_id
``

Run the command:

``
speech-split --help
``

## Example Commands

``
speech-split audio.mp3 ./output
``

This command will read `audio.mp3`, get the transcription, split it into sentences, align the audio fragments accordingly, and save the result as `output/audio.html`, that can be viewed by the browser.


``
speech-split video.mp4 ./output
``

This command will read `video.mp4`, split the audio, get the transcription, split it into sentences, align the audio fragments accordingly, and save the result as `output/video.html`, that can be viewed by the browser.


``
speech-split text.txt ./output
``

This command will read `text.txt`, convert text too speech, get the transcription, split it into sentences, align the audio fragments accordingly, and save the result as `output/text.html`, that can be viewed by the browser.

## Demo

You can see the demo of the tool in action [here](https://bubenkoff.github.io/speech-splitter.github.io/demo.html).

## Requirements
The dependencies will be installed automatically during the package installation process.

## Feedback and Contributions
Your feedback and contributions are welcome! If you encounter any issues or have suggestions for improvements, please feel free to open an issue on the GitHub repository or submit a pull request with your changes.

## License
MIT

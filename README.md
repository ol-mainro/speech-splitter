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

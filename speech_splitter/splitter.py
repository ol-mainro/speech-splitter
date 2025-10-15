import argparse
import base64
from math import floor
import mimetypes
import os
import string
import sys
import tempfile
import logging
from importlib.metadata import version
import json

import moviepy.editor as mp
from pydub import AudioSegment
from pydub.utils import mediainfo
from openai import OpenAI
import nltk
from nltk import tokenize
from progress.spinner import Spinner

# require environment variables
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
client = OpenAI()
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        logger.info("\nTranscribing audio...")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            timestamp_granularities=["word"],
            response_format="verbose_json",
            # language="nl",
        )
        logger.info("\nTranscription complete!")
        return transcript.language, transcript.text, transcript.words


# Split the given text into sentences
def split_text_into_sentences(text, language):
    return nltk.sent_tokenize(text, language=language)


wordTokenizer = tokenize.TweetTokenizer()


# Split the given text into words
def split_text_into_words(text, language):
    res = [x for x in wordTokenizer.tokenize(text) if x not in string.punctuation and x[0] not in string.punctuation]
    return res


def get_boundary_words(sentence_index, word_index, sentence, words, language):
    sentence_words = split_text_into_words(sentence, language)
    start_word = words[word_index]
    end_word = start_word
    # print(words)
    for i, sentence_word in enumerate(sentence_words):
        audio_word = words[word_index]
        # if the word is not the same as the sentence word, then most likely it has a punctuation and OpenAI falsely separated
        # it, so correct the word index
        if audio_word.word.lower() != sentence_word.lower():
            while not sentence_word.lower().endswith(audio_word.word.lower()):
                logger.warning(
                    f"Correcting word in sentence {sentence_index+1}: "
                    f"{audio_word.word} to {sentence_word} (word index: {word_index+1})"
                )
                word_index += 1
                if word_index > len(words) - 1:
                    break
                audio_word = words[word_index]
        if i == len(sentence_words) - 1:
            # last word in the sentence
            end_word = audio_word
        word_index += 1
        if word_index > len(words) - 1:
            word_index = len(words) - 1
    return start_word, end_word, word_index


def get_sentences_as_audio(sentences, original_audio, words, language):
    word_index = 0
    result = []
    for index, sentence in enumerate(sentences):
        start_word, end_word, word_index = get_boundary_words(index, word_index, sentence, words, language)
        start_time = start_word.start
        # add time buffer before the start
        start_time = start_time - 0.3
        if start_time < 0:
            start_time = 0
        end_time = end_word.end + 0.3
        chunk = original_audio[floor(start_time * 1000) : floor(end_time * 1000)]
        result.append(
            {"audio": chunk, "start_time": start_time, "end_time": end_time, "start_word": start_word, "end_word": end_word}
        )
    return result


def generate_html(audio_path, sentences, output_dir, title, audio_sentences, spinner, temp_dir, audio_bitrate):
    # Generate a responsive html file with the sentences and corresponding audio players
    with open(os.path.join(output_dir, f"{title}.html"), "w") as file:
        file.write(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            section {{
                margin-bottom: 20px;
                border: 1px solid #ddd;
                padding: 10px;
            }}
            audio {{
                width: 100%;
            }}
            </style>
            </head>
            <body>
            <h1>{title}</h1>
            """
        )
        full_text = "<br>".join(sentences)
        with open(audio_path, "rb") as audio_file:
            # encode the file data to base64
            encoded = base64.b64encode(audio_file.read()).decode("utf-8")
            src = f"data:audio/mp3;base64,{encoded}"
            file.write(
                f"""
            <section>
                <div style="max-height: 50vh; overflow: auto;">
                    <p>{full_text}</p>
                </div>
                <audio controls><source src="{src}" type="audio/mpeg"></audio>
            </section>
            <section>
                <button id="toggleAutoplay">Commencer à jouer</button>
            </section>
            <div style="max-height: 50vh; overflow: auto;">
            """
            )
        for i, sentence in enumerate(sentences):
            item = audio_sentences[i]
            audio_segment = item["audio"]
            # start_word = item["start_word"]
            # end_word = item["end_word"]
            # write to tempfile
            with tempfile.TemporaryFile(dir=temp_dir) as audio_file:
                audio_segment.export(audio_file, format="mp3", bitrate=f"{audio_bitrate}k")
                audio_file.seek(0)
                # encode the file data to base64
                encoded = base64.b64encode(audio_file.read()).decode("utf-8")
                src = f"data:audio/mp3;base64,{encoded}"

                # with open(output_dir + "/" + sentence[:30] + ".mp3", "a") as f:
                #  f.write(src)
		
                # save the audio to a file
                audio_segment.export(
                  os.path.join(output_dir, sentence[:30] + ".mp3"), format="mp3")

                file.write(
                    f"""
                <section>
                    <a id="{i+1}" href="#{i+1}">{i+1}.</a>
                    <p>{sentence}</p>
                    <audio title="{sentence[:30]}.mp3" controls><source src="{src}" type="audio/mpeg"></audio>
                </section>"""
                )
            spinner.next()
        file.write(
            """
            </div>
            <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const audioElements = document.querySelectorAll('audio');
                    const toggleButton = document.getElementById('toggleAutoplay');
                    let autoplayEnabled = false;

                    toggleButton.addEventListener('click', () => {
                        autoplayEnabled = !autoplayEnabled;
                        toggleButton.textContent = autoplayEnabled ? 'Automatisch afspelen uitschakelen' :
                            'Automatisch afspelen inschakelen';
                    });

                    audioElements.forEach((audio, index) => {
                        audio.addEventListener('ended', () => {
                            if (autoplayEnabled) {
                                const nextAudio = audioElements[index + 1];
                                if (nextAudio) {
                                    setTimeout(() => {
                                        nextAudio.parentElement.scrollIntoView({ behavior: 'smooth' });
                                        nextAudio.play();
                                    }, 1.5 * audio.duration * 1000);
                                }
                            }
                        });
                    });
                });
            </script>
            </body>
            </html>"""
        )


def float_range(mini=None, maxi=None):
    """Return function handle of an argument type function for
    ArgumentParser checking a float range: mini <= arg <= maxi
      mini - minimum acceptable argument
      maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def float_range_checker(arg):
        """New Type function for argparse - a float within predefined range."""

        try:
            f = float(arg)
        except ValueError:
            raise argparse.ArgumentTypeError("must be a floating point number")
        if mini is not None and f < mini or maxi is not None and f > maxi:
            raise argparse.ArgumentTypeError("must be in range [" + str(mini) + " .. " + str(maxi) + "]")
        return f

    # Return function handle to checking function
    return float_range_checker


def text_to_speech(text_path, temp_dir):
    logger.info("\nConverting text to speech...")
    with open(text_path, "r") as file:
        text = file.read()
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=text,
        )
        audio_path = os.path.join(temp_dir, "text_audio.mp3")
        response.write_to_file(audio_path)
        logger.info("\nText converted to speech successfully!")
        return audio_path


def main():
    # DEBUG = os.getenv("DEBUG", False)
    parser = argparse.ArgumentParser(description="Split a speech audio into separate sentences for language learners.")
    parser.add_argument(
        "input_path",
        type=str,
        metavar="path",
        action="store",
        nargs="+",
        help="""Path to the input file(s) (audio, video, or text).
                If it's a video file, the audio will be extracted.
                If it's a text file, the text will be converted to speech.""",
    )
    parser.add_argument("output_path", type=str, help="Path to save the output file(s).")
    parser.add_argument(
        "--offset",
        type=float_range(
            mini=0,
        ),
        help="Offset in seconds to start the audio from.",
    )
    # log level
    parser.add_argument(
        "--log-level",
        type=str,
        help="Log level. Default is INFO.",
        default="INFO",
    )
    # version
    parser.add_argument("--version", action="version", version=f"%(prog)s {version('speech-splitter')}")

    args = parser.parse_args()
    # set log level
    logger.setLevel(args.log_level)
    # check for input and output paths not being the same
    if args.input_path == args.output_path:
        raise ValueError("Input and output paths cannot be the same.")
    with Spinner("Loading...") as spinner:
        nltk.download("punkt_tab")
        output_dir = args.output_path
        os.makedirs(output_dir, exist_ok=True)
        for input_path in args.input_path:
            spinner.next()
            title = os.path.basename(input_path).split(".")[0]

            with tempfile.TemporaryDirectory() as temp_dir:
                input_content_type = mimetypes.guess_type(input_path)[0]
                if input_content_type.startswith("video"):
                    logger.info("\nInput file is a video file.")
                    # Extract audio from the video
                    audio_path = os.path.join(temp_dir, "audio.mp3")
                    video = mp.VideoFileClip(input_path)
                    video.audio.write_audiofile(audio_path)
                elif input_content_type.startswith("audio"):
                    logger.info("\nInput file is an audio file.")
                    audio_path = input_path
                elif input_content_type.startswith("text"):
                    audio_path = text_to_speech(input_path, temp_dir)
                else:
                    logger.error("\nError: Input file is not a valid audio or video file.")
                    sys.exit(1)
                # Load the original audio for accurate sentence splitting
                audio = AudioSegment.from_mp3(audio_path)
                audio_bitrate = mediainfo(audio_path)["bit_rate"]

                spinner.next()

                if args.offset:
                    audio = audio[args.offset * 1000 :]
                    # save audio to a new file
                    audio_path = os.path.join(temp_dir, "offset_audio.mp3")
                    audio.export(audio_path, format="mp3", bitrate=f"{audio_bitrate}k")
                    spinner.next()

                # Transcribe the chunks and combine the text
                language, full_text, words = transcribe_audio(audio_path)
                spinner.next()

                if args.log_level == "DEBUG":
                    # save the audio to a file
                    audio.export(
                        os.path.join(output_dir, f"{title}_extracted_audio.mp3"), format="mp3", bitrate=f"{audio_bitrate}k"
                    )

                    # save the transcribed text to a file
                    with open(os.path.join(output_dir, f"{title}_transcribed_text.txt"), "w") as file:
                        file.write(full_text)
                    spinner.next()

                    # save words to a file
                    with open(os.path.join(output_dir, f"{title}_words.json"), "w") as file:
                        file.write(str(words))
                    spinner.next()

                # Split the transcribed text into sentences
                sentences = split_text_into_sentences(full_text, language)
                spinner.next()

                # Save each sentence as a separate audio file
                audio_sentences = get_sentences_as_audio(sentences, audio, words, language)
                spinner.next()

                generate_html(audio_path, sentences, output_dir, title, audio_sentences, spinner, temp_dir, audio_bitrate)

            logger.info("\nAudio split into sentences successfully!")
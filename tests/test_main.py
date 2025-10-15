from openai.types.audio.transcription import Transcription
from speech_splitter.splitter import main


def test_main(mocker, tmp_path):
    def create_transcription(**params):
        return Transcription(
            text="Hello, world!",
            language="english",
            words=[
                {"start": 0.0, "end": 0.5, "word": "Hello"},
                {"start": 0.5, "end": 1.0, "word": "world"},
            ],
        )

    patched = mocker.patch(
        # api_call is from slow.py but imported to main.py
        "speech_splitter.splitter.client.audio.transcriptions.create",
        side_effect=create_transcription,
    )
    input_path = "./tests/data/audio.mp3"
    output_path = str(tmp_path / "output")
    mocker.patch(
        "sys.argv",
        [
            "speech-split",
            input_path,
            output_path,
        ],
    )
    main()
    assert patched.call_count == 1
    html_path = tmp_path / "output" / "audio.html"
    assert html_path.exists()
    html_text = html_path.read_text()
    assert "Hello, world!" in html_text
    assert "<audio" in html_text

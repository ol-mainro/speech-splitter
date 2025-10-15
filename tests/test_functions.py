import pytest

from speech_splitter.splitter import split_text_into_words


@pytest.mark.parametrize(
    "language, text, expected",
    [
        ("english", "Hello, world!", ["Hello", "world"]),
        ("english", "Hello, world! ", ["Hello", "world"]),
        ("english", " Hello, world! ", ["Hello", "world"]),
        (
            "dutch",
            "wel isn't zat can't: haven't.",
            [
                "wel",
                "isn't",
                "zat",
                "can't",
                "haven't",
            ],
        ),
        (
            "dutch",
            "Musée d'Orsay.",
            [
                "Musée",
                "d'Orsay",
            ],
        ),
        (
            "dutch",
            "Zo'n ding heb ik niet.",
            [
                "Zo'n",
                "ding",
                "heb",
                "ik",
                "niet",
            ],
        ),
        (
            "dutch",
            "Because they're going to do like, we went to the hotel, and it was very good.",
            [
                "Because",
                "they're",
                "going",
                "to",
                "do",
                "like",
                "we",
                "went",
                "to",
                "the",
                "hotel",
                "and",
                "it",
                "was",
                "very",
                "good",
            ],
        ),
        (
            "dutch",
            "Dus als je het niet eens bent met iemand, maar iemand zegt hé... dan moet je dus actief er tegenin gaan.",
            [
                "Dus",
                "als",
                "je",
                "het",
                "niet",
                "eens",
                "bent",
                "met",
                "iemand",
                "maar",
                "iemand",
                "zegt",
                "hé",
                "dan",
                "moet",
                "je",
                "dus",
                "actief",
                "er",
                "tegenin",
                "gaan",
            ],
        ),
    ],
)
def test_split_text_into_words(language, text, expected):
    words = split_text_into_words(text, language)
    assert words == expected

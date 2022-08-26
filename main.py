import os
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
from google.cloud import texttospeech
from lib import Html_Parser as HP

SKIP_NET_CALLS = False
FILES_LOCATION = "unused for now, will define folder that contains many epubs"


def main():
    pth = Path(".")
    key_file = "{}\\.secrets\\tts-key.json".format(pth.parent.absolute())
    # Set g-cloud api key (they make you stick it in an environment variable)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
    print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    # Build tts profile
    tts_client = texttospeech.TextToSpeechClient()
    tts_voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    tts_audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    book_files = [x.name for x in pth.glob("*.epub")]
    for book_file in book_files:
        book = epub.read_epub(book_file)
        # Remove spaces from book title
        book_name = book.title.replace(" ", "_")
        # Drop any other weird characters
        book_name = "".join(c for c in book_name if (c.isalnum() or c in "_-"))
        # Spine gives "proper" order of documents. Gives id found in items list
        all_docs = [book.get_item_with_id(x[0]) for x in book.spine]
        chap_num = 1
        for item in all_docs:
            print(item.id)
            # Determining chapters and breaks is a difficult problem. EPUB formatting
            # is not standardized, and so there will be books out there that just
            # don't look like we expect. We do our best.
            # See https://cran.r-project.org/web/packages/epubr/vignettes/epubr.html
            chapter_html = item.get_content()
            # parse_html only pulls text between <p> tags - presumably only
            # chapter text.
            # sections_text should be a list of strings, each under Google's 5k char limit
            chapter_secs = HP.parse_html(chapter_html)
            chapter_audio = bytearray()
            for sec_txt in chapter_secs:
                if len(sec_txt):
                    print("Section length: {}".format(len(sec_txt)))
                    print(sec_txt[:50])
                    # Perform the text-to-speech request
                    tts_input = texttospeech.SynthesisInput(text=sec_txt)
                    if not SKIP_NET_CALLS:
                        tts_response = tts_client.synthesize_speech(
                            input=tts_input,
                            voice=tts_voice,
                            audio_config=tts_audio_config,
                        )
                    else:
                        tts_response = type("Foo", (), dict(audio_content=bytes(1024)))
                    chapter_audio.extend(tts_response.audio_content)
            if len(chapter_audio):
                output_name = "output\\{}\\chapter_{:03d}.mp3".format(
                    book_name, chap_num
                )
                os.makedirs(os.path.dirname(output_name), exist_ok=True)
                # The response's audio_content is binary, open as "wb".
                with open(output_name, "wb") as out:
                    # Write the response to the output file.
                    out.write(chapter_audio)
                    print("Audio content written to file {}".format(output_name))
                chap_num += 1


if __name__ == "__main__":
    main()

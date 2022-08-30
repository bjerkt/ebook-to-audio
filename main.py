import os
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
from google.cloud import texttospeech
from lib import Html_Parser as HP, EPUB_Reader as ER, Book_Writer as BW

SKIP_NET_CALLS = False


def main():
    pth = Path(".")
    key_file = "{}\\.secrets\\tts-key.json".format(pth.parent.absolute())
    # Set g-cloud api key (they make you stick it in an environment variable)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
    print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    # Build tts profile
    # make several voices here for quick switching
    voice = {
        "Male-Deep-US": texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-B",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        ),
        "Female-HQ-AU": texttospeech.VoiceSelectionParams(
            language_code="en-AU",
            name="en-AU-Neural2-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        ),
        "Female-HQ-UK": texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Neural2-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        ),
        "Female-Fun-UK": texttospeech.VoiceSelectionParams(
            language_code="en-GB",
            name="en-GB-Wavenet-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        ),
        "Female-Assistant-Maybe": texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        ),
    }
    tts_profile = {
        "tts_client": texttospeech.TextToSpeechClient(),
        "tts_voice": voice["Female-HQ-UK"],
        "tts_audio_config": texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        ),
    }
    # Gather all epub files
    epub_files = [x for x in pth.glob("input/*.epub")]
    # Gather all pdf files
    pdf_files = []
    # Only process to HTML here, we need the <p> tags to figure out good splicing points
    # Process EPUBs into list of HTML chapters (many probably longer than google's 5k char limit for tts requests)
    # {title, [chapters]}
    epubs_as_html = ER.process_file_list(epub_files)
    # Process pdfs into list of HTML?
    # TODO: pdf work
    # Content is now homogenous, concat it all
    all_books_as_html = {}
    all_books_as_html.update(epubs_as_html)
    for title, chapters_html in all_books_as_html.items():
        print(title)
        [total_chars, total_chaps] = BW.write_book_audio(
            title, chapters_html, tts_profile
        )
        print(
            "Book was {} chars long, across {} chapters.".format(
                total_chars, total_chaps
            )
        )
    return
    """
    Below this can eventually be deleted
    """
    for book_file in epub_files:
        book = epub.read_epub(book_file.__str__())
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
                    print("    Section length: {}".format(len(sec_txt)))
                    print("    " + sec_txt[:50])
                    # Perform the text-to-speech request
                    tts_input = texttospeech.SynthesisInput(text=sec_txt)
                    if not SKIP_NET_CALLS:
                        print("    Making tts request...")
                        tts_response = tts_client.synthesize_speech(
                            input=tts_input,
                            voice=tts_voice,
                            audio_config=tts_audio_config,
                        )
                        print("    Got tts response")
                    else:
                        tts_response = type("Foo", (), dict(audio_content=bytes(1024)))
                    print("    Adding audio section to chapter")
                    chapter_audio.extend(tts_response.audio_content)
            if len(chapter_audio):
                output_name = "output\\{}\\chapter_{:03d}.mp3".format(
                    book_name, chap_num
                )
                os.makedirs(os.path.dirname(output_name), exist_ok=True)
                # The response's audio_content is binary, open as "wb".
                print("    Writing chapter audio as {}".format(output_name))
                with open(output_name, "wb") as out:
                    # Write the response to the output file.
                    out.write(chapter_audio)
                chap_num += 1


if __name__ == "__main__":
    main()

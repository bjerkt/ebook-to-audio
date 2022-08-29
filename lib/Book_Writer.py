import os
from google.cloud import texttospeech
from lib import Html_Parser as HP
from main import SKIP_NET_CALLS


def write_book_audio(
    title,
    chapters_html,
    tts_profile,
):
    chap_num = 1
    total_chars = 0
    for chap_html in chapters_html:
        print("-   Chapter {:03d}?".format(chap_num))
        chapter_sections = HP.parse_html(chap_html)
        chapter_audio = bytearray()
        for sec_txt in chapter_sections:
            if len(sec_txt):
                total_chars += len(sec_txt)
                print("-       New section - len: {}".format(len(sec_txt)))
                print("-           " + sec_txt[:50])
                # Perform the text-to-speech request
                tts_input = texttospeech.SynthesisInput(text=sec_txt)
                if not SKIP_NET_CALLS:
                    print("-       Making tts request...")
                    tts_response = tts_profile["tts_client"].synthesize_speech(
                        input=tts_input,
                        voice=tts_profile["tts_voice"],
                        audio_config=tts_profile["tts_audio_config"],
                    )
                    print("-       Got tts response")
                else:
                    tts_response = type("Foo", (), dict(audio_content=bytes(1024)))
                print("-           Adding audio section to chapter")
                chapter_audio.extend(tts_response.audio_content)
        if len(chapter_audio):
            output_name = "output\\{}\\chapter_{:03d}.mp3".format(title, chap_num)
            os.makedirs(os.path.dirname(output_name), exist_ok=True)
            # The response's audio_content is binary, open as "wb".
            print("-   Writing chapter audio as {}".format(output_name))
            with open(output_name, "wb") as out:
                # Write the response to the output file.
                out.write(chapter_audio)
            chap_num += 1
    return [total_chars, chap_num - 1]

import argparse, os, sys, requests
from app_rvc import SoniTranslate, edge_tts_voices_list, logger
from soni_translate.text_to_speech import create_wav_file_vc
from soni_translate.utils import copy_files
from soni_translate.text_to_speech import supported_lang_coqui
from soni_translate import language_configuration

XILABS_API_KEY = os.environ.get("XILABS_API_KEY")


def extract_voices(voice_list, language, gender):
    # Split each item and filter based on language and gender
    filtered_voices = [
        voice
        for voice in voice_list
        if voice.startswith(language) and voice.endswith(gender)
    ]
    return filtered_voices


def add_voice_xilabs(audio_path, audio_name):
    url = "https://api.elevenlabs.io/v1/voices/add"

    headers = {
        "xi-api-key": XILABS_API_KEY,
    }

    data = {
        "files": [open(audio_path, "rb")],
        "name": audio_name,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        logger.info("Voice added successfully!")
        return (response.json())["voice_id"]
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(response.text)


def main():
    parser = argparse.ArgumentParser(
        description="""Video dubbing with support for following lang_codes: af, am, ar, az, bg, bn, bs, ca, cs, cy, da, de, el, en, es, et, fa, fi, fil, fr, ga, gl, gu, he, hi, hr, hu, id, is, it, ja, jv, ka, kk, km, kn, ko, lo, lt, lv, mk, ml, mn, mr, ms, mt, my, nb, ne, nl, pl, ps, pt, ro, ru, si, sk, sl, so, sq, sr, su, sv, sw, ta, te, th, tr, uk, ur, uz, vi, zh, zu.
        
        With Voice cloning support for the following languages:"zh-cn","en","fr","de","it","pt","pl","tr","ru","nl","cs","ar","es","hu","ko","ja",
        (Chinese, English, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Spanish, Hungarian, Korean, Japanese)
        """
    )

    # Add command line arguments for all the options
    parser.add_argument(
        "--media_file", type=str, required=True, help="Path to input media file"
    )
    parser.add_argument(
        "--source_language",
        type=str,
        default="Automatic detection",
        help="Source language (eg. 'English (en)')",
    )
    parser.add_argument(
        "--target_language", type=str, required=True, help="Target language"
    )
    parser.add_argument(
        "--transcriber_model",
        type=str,
        default="small",
        help="Whisper model type (e.g., base, small, medium, large)",
    )
    parser.add_argument(
        "--min_speakers", type=int, default=1, help="Minimum number of speakers"
    )
    parser.add_argument(
        "--max_speakers", type=int, default=1, help="Maximum number of speakers"
    )
    parser.add_argument("--gender", type=str, default="Male", help="Male or Female")
    parser.add_argument(
        "--custom_vocab",
        default="",
        type=str,
        help="Vocabulary to improve transcription quality",
    )
    parser.add_argument("--output_name", type=str, default="", help="Output filename")
    parser.add_argument(
        "--audio_path_vc",
        default="",
        type=str,
        help="Sample audio file to be used for voice cloning",
    )

    # Add more arguments as needed for other options

    args = parser.parse_args()
    media_path = "/tmp/gradio/"
    copy_files(args.media_file, media_path)
    args.media_file = os.path.join(media_path, os.path.basename(args.media_file))

    target_lang_code = (args.target_language).split("(")[1][:2]

    if args.audio_path_vc:
        file_name = os.path.splitext(os.path.basename(args.audio_path_vc))[0]
        if target_lang_code in supported_lang_coqui:
            vc_audio_path = create_wav_file_vc(
                file_name, args.audio_path_vc, 0, 0, "_XTTS_", True
            )
        elif target_lang_code in ["hi", "ta"]:
            vc_audio_path = create_wav_file_vc(
                file_name, args.audio_path_vc, 0, 0, "_XILABS_", True
            )
            voice_name = f"xilabs_{target_lang_code}_custom"
            voice_id_xilabs = add_voice_xilabs(vc_audio_path, voice_name)
            language_configuration.XILABS_VOICES_LIST[voice_name] = voice_id_xilabs

    # Initialize SoniTranslate
    translator = SoniTranslate()

    # Extract voice on the basis of gender and lang
    voice_list = edge_tts_voices_list()

    selected_voices = extract_voices(voice_list, target_lang_code, args.gender)

    # Call the translation function with arguments
    output = translator.batch_multilingual_media_conversion(
        *[
            [args.media_file],  # video_input_path
            "",  # youtube link
            "",
            "",
            False,
            args.transcriber_model,
            4,
            "auto",
            args.source_language,
            args.target_language,
            args.min_speakers,
            args.max_speakers,
            selected_voices[0] if not args.audio_path_vc else vc_audio_path,
            "en-US-AndrewMultilingualNeural-Male",
            "en-US-AvaMultilingualNeural-Female",
            "en-US-BrianMultilingualNeural-Male",
            "de-DE-SeraphinaMultilingualNeural-Female",
            "de-DE-FlorianMultilingualNeural-Male",
            "fr-FR-VivienneMultilingualNeural-Female",
            "fr-FR-RemyMultilingualNeural-Male",
            "en-US-EmmaMultilingualNeural-Female",
            "en-US-AndrewMultilingualNeural-Male",
            "en-US-EmmaMultilingualNeural-Female",
            "en-US-AndrewMultilingualNeural-Male",
            args.output_name,
            "Adjusting volumes and mixing audio",
            1.5,
            True,
            0,
            2,
            "srt",
            False,
            False,
            "{}",
            True,
            True,
            False,
            15,
            "pyannote_3.1",
            "google_translator_batch",
            None,
            "video (mp4)",
            False,
            False,
            3,
            False,
            True,
            "freevc",
            True,
            "sentence",
            ".|!|?",
            False,
            False,
            False,
            False,
            1,
            args.custom_vocab,
            False,
        ]
    )

    logger.info(f"Translation complete. Output: {output}")


if __name__ == "__main__":
    main()

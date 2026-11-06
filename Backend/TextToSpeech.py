
import pygame
import random
import asyncio
import edge_tts
import os
import re
from dotenv import dotenv_values


# ============================================================
# BASE PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "Data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# ============================================================
# ENV
# ============================================================

env_vars = dotenv_values(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

AssistantVoice = env_vars.get(
    "AssistantVoice",
    "en-IN-NeerjaNeural"
)


# ============================================================
# MULTILINGUAL VOICES
# ============================================================

LANGUAGE_VOICES = {

    "english":
        "en-IN-NeerjaNeural",

    "hindi":
        "hi-IN-SwaraNeural",

    "telugu":
        "te-IN-ShrutiNeural",

    "tamil":
        "ta-IN-PallaviNeural",

    "kannada":
        "kn-IN-SapnaNeural",

    "malayalam":
        "ml-IN-SobhanaNeural",

    "bengali":
        "bn-IN-TanishaaNeural",

    "marathi":
        "mr-IN-AarohiNeural",

    "gujarati":
        "gu-IN-DhwaniNeural",

    "punjabi":
        "pa-IN-OjasNeural",

    "urdu":
        "ur-IN-GulNeural"
}


# ============================================================
# DETECT LANGUAGE FROM SCRIPT
# ============================================================

def DetectLanguage(Text):

    if not Text:
        return "english"

    # --------------------------------------------------------
    # Hindi / Devanagari
    # --------------------------------------------------------

    if re.search(
        r"[\u0900-\u097F]",
        Text
    ):

        return "hindi"


    # --------------------------------------------------------
    # Telugu
    # --------------------------------------------------------

    if re.search(
        r"[\u0C00-\u0C7F]",
        Text
    ):

        return "telugu"


    # --------------------------------------------------------
    # Tamil
    # --------------------------------------------------------

    if re.search(
        r"[\u0B80-\u0BFF]",
        Text
    ):

        return "tamil"


    # --------------------------------------------------------
    # Kannada
    # --------------------------------------------------------

    if re.search(
        r"[\u0C80-\u0CFF]",
        Text
    ):

        return "kannada"


    # --------------------------------------------------------
    # Malayalam
    # --------------------------------------------------------

    if re.search(
        r"[\u0D00-\u0D7F]",
        Text
    ):

        return "malayalam"


    # --------------------------------------------------------
    # Bengali
    # --------------------------------------------------------

    if re.search(
        r"[\u0980-\u09FF]",
        Text
    ):

        return "bengali"


    # --------------------------------------------------------
    # Gujarati
    # --------------------------------------------------------

    if re.search(
        r"[\u0A80-\u0AFF]",
        Text
    ):

        return "gujarati"


    # --------------------------------------------------------
    # Punjabi
    # --------------------------------------------------------

    if re.search(
        r"[\u0A00-\u0A7F]",
        Text
    ):

        return "punjabi"


    # --------------------------------------------------------
    # Urdu
    # --------------------------------------------------------

    if re.search(
        r"[\u0600-\u06FF]",
        Text
    ):

        return "urdu"


    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    return "english"


# ============================================================
# GET VOICE
# ============================================================

def GetVoice(Text):

    language = DetectLanguage(
        Text
    )

    return LANGUAGE_VOICES.get(
        language,
        AssistantVoice
    )


# ============================================================
# TEXT TO AUDIO
# ============================================================

async def TextToAudioFile(
    text,
    voice
):

    file_path = os.path.join(
        DATA_DIR,
        "speech.mp3"
    )

    if os.path.exists(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

        except Exception:
            pass


    communicate = edge_tts.Communicate(

        text,

        voice,

        pitch="+5Hz",

        rate="+13%"

    )

    await communicate.save(
        file_path
    )


# ============================================================
# TTS
# ============================================================

def TTS(
    Text,
    func=lambda r=None: True
):

    try:

        if not Text:
            return False


        voice = GetVoice(
            Text
        )


        print(
            "TTS Voice:",
            voice
        )


        asyncio.run(
            TextToAudioFile(
                Text,
                voice
            )
        )


        file_path = os.path.join(
            DATA_DIR,
            "speech.mp3"
        )


        if not os.path.exists(
            file_path
        ):

            print(
                "Error: speech.mp3 was not created."
            )

            return False


        pygame.mixer.init()

        pygame.mixer.music.load(
            file_path
        )

        pygame.mixer.music.play()


        while pygame.mixer.music.get_busy():

            if func() == False:
                break

            pygame.time.Clock().tick(
                10
            )


        return True


    except Exception as e:

        print(
            f"Error in TTS: {e}"
        )

        return False


    finally:

        if pygame.mixer.get_init():

            try:

                pygame.mixer.music.stop()

                pygame.mixer.quit()

            except Exception as e:

                print(
                    f"Error while closing audio: {e}"
                )


# ============================================================
# TEXT TO SPEECH
# ============================================================

def TextToSpeech(
    Text,
    func=lambda r=None: True
):

    if not Text:
        return


    Data = str(Text).split(
        ","
    )


    responses = [

        "The rest of the result has been printed to the chat screen, kindly check it out sir.",

        "The rest of the text is now on the chat screen, sir, please check it.",

        "You can see the rest of the text on the chat screen, sir.",

        "The remaining part of the text is now on the chat screen, sir.",

        "Sir, you'll find more text on the chat screen, sir.",

        "The rest of the answer is now on the chat screen, sir.",

        "Sir, please look at the chat screen, the rest of the answer is there.",

        "You'll find the complete answer on the chat screen, sir."

    ]


    if (
        len(Data) > 4
        and
        len(Text) > 250
    ):

        first_part = (
            Text.split(".")[0]
        )

        TTS(

            first_part
            +
            ". "
            +
            random.choice(
                responses
            ),

            func

        )

    else:

        TTS(
            Text,
            func
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    while True:

        Text = input(
            "Enter the text: "
        )

        if Text.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            break

        TextToSpeech(
            Text
        )


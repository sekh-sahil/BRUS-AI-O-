import os
import asyncio
import threading
import traceback
from dotenv import dotenv_values

from Backend.Model import FirstLayerDMM
from Backend.Automation import Automation
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.SpeechToText import SpeechRecognition, SetLanguage
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageGeneration import GenerateImage

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    GetMicrophoneStatus
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

os.chdir(BASE_DIR)


# ============================================================
# ENV
# ============================================================

env_vars = dotenv_values(
    os.path.join(BASE_DIR, ".env")
)

ASSISTANT_NAME = env_vars.get(
    "Assistantname",
    "Assistant"
)


# ============================================================
# STARTUP
# ============================================================

print("=" * 60)
print(f"Assistant: {ASSISTANT_NAME}")
print(f"Project: {BASE_DIR}")
print("=" * 60)


# ============================================================
# FILES
# ============================================================

def InitializeFiles():

    data_folder = os.path.join(
        BASE_DIR,
        "Data"
    )

    frontend_folder = os.path.join(
        BASE_DIR,
        "Frontend",
        "Files"
    )

    generated_folder = os.path.join(
        frontend_folder,
        "GeneratedImages"
    )

    os.makedirs(
        data_folder,
        exist_ok=True
    )

    os.makedirs(
        frontend_folder,
        exist_ok=True
    )

    os.makedirs(
        generated_folder,
        exist_ok=True
    )

    files = {

        os.path.join(
            frontend_folder,
            "Mic.data"
        ): "False",

        os.path.join(
            frontend_folder,
            "Status.data"
        ): "",

        os.path.join(
            frontend_folder,
            "Responses.data"
        ): ""

    }

    for path, value in files.items():

        if not os.path.exists(path):

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(value)


InitializeFiles()


# ============================================================
# GLOBAL
# ============================================================

RUNNING = True
STARTUP_GREETING_DONE = False


# ============================================================
# STATUS
# ============================================================

def SetStatus(status):

    try:

        SetAssistantStatus(status)

    except Exception as e:

        print(
            "Status Error:",
            e
        )


# ============================================================
# GUI MESSAGE
# ============================================================

def ShowMessage(message):

    try:

        ShowTextToScreen(message)

    except Exception as e:

        print(
            "GUI Message Error:",
            e
        )


# ============================================================
# MICROPHONE
# ============================================================

def MicrophoneEnabled():

    try:

        status = GetMicrophoneStatus()

        if isinstance(status, bool):

            return status

        return (
            str(status)
            .strip()
            .lower()
            == "true"
        )

    except Exception as e:

        print(
            "Microphone Status Error:",
            e
        )

        return False


# ============================================================
# SPEAK
# ============================================================

def Speak(text):

    if not text:

        return

    try:

        print(
            f"{ASSISTANT_NAME}: {text}"
        )

        TextToSpeech(text)

    except Exception as e:

        print(
            "TTS Error:",
            e
        )


# ============================================================
# STARTUP GREETING
# ============================================================

async def StartupGreeting():

    global STARTUP_GREETING_DONE

    if STARTUP_GREETING_DONE:

        return

    STARTUP_GREETING_DONE = True

    greeting = (
        "How can I assist you today, sir?"
    )

    await asyncio.sleep(1)

    ShowMessage(
        f"{ASSISTANT_NAME}: {greeting}"
    )

    SetStatus(
        "Speaking..."
    )

    await asyncio.to_thread(
        Speak,
        greeting
    )

    SetStatus(
        "Ready"
    )


# ============================================================
# LANGUAGE CHANGE
# ============================================================

async def HandleLanguageChange(query):

    text = query.lower().strip()

    language_map = {

        "english": "english",
        "hindi": "hindi",
        "telugu": "telugu",
        "tamil": "tamil",
        "kannada": "kannada",
        "malayalam": "malayalam",
        "bengali": "bengali",
        "marathi": "marathi",
        "gujarati": "gujarati",
        "punjabi": "punjabi",
        "urdu": "urdu"

    }

    change_phrases = [

        "change language to ",
        "switch language to ",
        "set language to "

    ]

    for phrase in change_phrases:

        if text.startswith(phrase):

            language = text[
                len(phrase):
            ].strip()

            if language not in language_map:

                message = (
                    "Sorry, that language is not supported yet."
                )

                ShowMessage(
                    f"{ASSISTANT_NAME}: {message}"
                )

                SetStatus(
                    "Speaking..."
                )

                await asyncio.to_thread(
                    Speak,
                    message
                )

                SetStatus(
                    "Ready"
                )

                return True

            selected_language = language_map[
                language
            ]

            try:

                success = SetLanguage(
                    selected_language
                )

                if not success:

                    message = (
                        "Sorry, I could not change "
                        "the language."
                    )

                    ShowMessage(
                        f"{ASSISTANT_NAME}: {message}"
                    )

                    await asyncio.to_thread(
                        Speak,
                        message
                    )

                    SetStatus(
                        "Ready"
                    )

                    return True

                message = (
                    f"Language changed to "
                    f"{language.title()}."
                )

                print(
                    f"Language changed to: "
                    f"{language.title()}"
                )

                ShowMessage(
                    f"{ASSISTANT_NAME}: {message}"
                )

                SetStatus(
                    "Speaking..."
                )

                await asyncio.to_thread(
                    Speak,
                    message
                )

                SetStatus(
                    "Ready"
                )

                return True

            except Exception as e:

                print(
                    "Language Change Error:",
                    repr(e)
                )

                traceback.print_exc()

                return True

    return False


# ============================================================
# IMAGE COMMAND DETECTION
# ============================================================

def IsImageCommand(query):

    text = query.lower().strip()

    image_words = [

        "generate an image",
        "generate a image",
        "generate image",
        "create an image",
        "create a image",
        "create image",
        "make an image",
        "make a image",
        "make image"

    ]

    for word in image_words:

        if text.startswith(word):

            return True

    return False


# ============================================================
# REALTIME DETECTION
# ============================================================

def IsRealtimeQuery(query):

    text = query.lower()

    words = [

        "latest",
        "current",
        "today",
        "right now",
        "recent",
        "news",
        "weather",
        "temperature",
        "live score",
        "current price",
        "stock price"

    ]

    for word in words:

        if word in text:

            return True

    return False


# ============================================================
# FAST COMMAND DETECTION
# ============================================================

def FastCommandDetection(query):

    text = query.strip().lower()


    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    if IsImageCommand(text):

        return [
            text
        ]


    # --------------------------------------------------------
    # OPEN
    # --------------------------------------------------------

    if text.startswith("open "):

        return [
            text
        ]


    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    if text.startswith("close "):

        return [
            text
        ]


    # --------------------------------------------------------
    # PLAY
    # --------------------------------------------------------

    if text.startswith("play "):

        return [
            text
        ]


    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    if text.startswith(
        "google search "
    ):

        return [
            text
        ]

    if text.startswith(
        "search google for "
    ):

        value = text.replace(
            "search google for ",
            "",
            1
        ).strip()

        return [
            f"google search {value}"
        ]


    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    if text.startswith(
        "youtube search "
    ):

        return [
            text
        ]

    if text.startswith(
        "search youtube for "
    ):

        value = text.replace(
            "search youtube for ",
            "",
            1
        ).strip()

        return [
            f"youtube search {value}"
        ]


    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    system_commands = {

        "mute":
            "system mute",

        "unmute":
            "system unmute",

        "volume up":
            "system volume up",

        "increase volume":
            "system volume up",

        "volume down":
            "system volume down",

        "decrease volume":
            "system volume down"

    }

    if text in system_commands:

        return [
            system_commands[text]
        ]


    return None


# ============================================================
# IMAGE GENERATION
# ============================================================

async def HandleImageGeneration(query):

    print()
    print("=" * 60)
    print("IMAGE GENERATION REQUEST")
    print("Query:", query)
    print("=" * 60)

    SetStatus(
        "Generating image..."
    )

    try:

        result = await asyncio.to_thread(
            GenerateImage,
            query
        )

        print(
            "GenerateImage result:",
            result
        )

        if result is True:

            message = (
                "Image generated successfully."
            )

            ShowMessage(
                f"{ASSISTANT_NAME}: {message}"
            )

            SetStatus(
                "Ready"
            )

            return

        message = (
            "Sorry, I couldn't generate the image."
        )

        ShowMessage(
            f"{ASSISTANT_NAME}: {message}"
        )

        print(
            "Image generation returned False."
        )

    except Exception as e:

        print()
        print(
            "IMAGE GENERATION ERROR"
        )

        print(
            repr(e)
        )

        traceback.print_exc()

        ShowMessage(
            f"{ASSISTANT_NAME}: "
            "Image generation failed."
        )

    finally:

        SetStatus(
            "Ready"
        )


# ============================================================
# GENERAL
# ============================================================

async def HandleGeneralQuery(query):

    if not query:

        return

    print(
        "GENERAL:",
        query
    )

    SetStatus(
        "Thinking..."
    )

    try:

        answer = await asyncio.to_thread(
            ChatBot,
            query
        )

        if answer:

            print(
                f"{ASSISTANT_NAME}:",
                answer
            )

            ShowMessage(
                f"{ASSISTANT_NAME}: {answer}"
            )

            SetStatus(
                "Speaking..."
            )

            await asyncio.to_thread(
                Speak,
                answer
            )

    except Exception as e:

        print(
            "ChatBot Error:",
            repr(e)
        )

        traceback.print_exc()

    finally:

        SetStatus(
            "Ready"
        )


# ============================================================
# REALTIME
# ============================================================

async def HandleRealtimeQuery(query):

    if not query:

        return

    print(
        "REALTIME:",
        query
    )

    SetStatus(
        "Searching..."
    )

    try:

        answer = await asyncio.to_thread(
            RealtimeSearchEngine,
            query
        )

        if answer:

            print(
                f"{ASSISTANT_NAME}:",
                answer
            )

            ShowMessage(
                f"{ASSISTANT_NAME}: {answer}"
            )

            SetStatus(
                "Speaking..."
            )

            await asyncio.to_thread(
                Speak,
                answer
            )

    except Exception as e:

        print(
            "Realtime Error:",
            repr(e)
        )

        traceback.print_exc()

    finally:

        SetStatus(
            "Ready"
        )


# ============================================================
# AUTOMATION
# ============================================================

async def HandleAutomation(tasks):

    if not tasks:

        return

    print()
    print("=" * 60)

    print(
        "AUTOMATION TASKS:",
        tasks
    )

    print("=" * 60)

    SetStatus(
        "Working..."
    )

    try:

        # Automation() is already async.
        result = await Automation(
            tasks
        )

        print(
            "Automation Result:",
            result
        )

    except Exception as e:

        print(
            "Automation Error:",
            repr(e)
        )

        traceback.print_exc()

    finally:

        SetStatus(
            "Ready"
        )


# ============================================================
# PROCESS MODEL TASKS
# ============================================================

async def ProcessTasks(tasks):

    if not tasks:

        print(
            "No tasks received."
        )

        return

    print()
    print(
        "MODEL TASKS:",
        tasks
    )

    automation_tasks = []


    for task in tasks:

        if not task:

            continue

        task = task.strip()

        task_lower = task.lower()


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        if IsImageCommand(task):

            await HandleImageGeneration(
                task
            )

            continue


        # ----------------------------------------------------
        # AUTOMATION
        # ----------------------------------------------------

        if task_lower.startswith(
            (
                "open ",
                "close ",
                "play ",
                "content ",
                "google search ",
                "youtube search ",
                "system "
            )
        ):

            automation_tasks.append(
                task
            )

            continue


        # ----------------------------------------------------
        # GENERAL
        # ----------------------------------------------------

        if task_lower.startswith(
            "general "
        ):

            query = task[
                len("general "):
            ].strip()

            await HandleGeneralQuery(
                query
            )

            continue


        # ----------------------------------------------------
        # REALTIME
        # ----------------------------------------------------

        if task_lower.startswith(
            "realtime "
        ):

            query = task[
                len("realtime "):
            ].strip()

            await HandleRealtimeQuery(
                query
            )

            continue


        # ----------------------------------------------------
        # REMINDER
        # ----------------------------------------------------

        if task_lower.startswith(
            "reminder "
        ):

            print(
                "Reminder is not implemented yet."
            )

            continue


        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        print(
            "Unknown task:",
            task
        )

        await HandleGeneralQuery(
            task
        )


    # --------------------------------------------------------
    # RUN AUTOMATION
    # --------------------------------------------------------

    if automation_tasks:

        await HandleAutomation(
            automation_tasks
        )


# ============================================================
# PROCESS USER QUERY
# ============================================================

async def ProcessQuery(query):

    if not query:

        return

    query = query.strip()

    if not query:

        return


    # ========================================================
    # LANGUAGE CHANGE
    # ========================================================

    language_changed = await HandleLanguageChange(
        query
    )

    if language_changed:

        return


    print()
    print("=" * 60)

    print(
        "USER:",
        query
    )

    print("=" * 60)


    ShowMessage(
        f"You: {query}"
    )


    # ========================================================
    # 1. IMAGE DIRECT
    # ========================================================

    if IsImageCommand(query):

        print(
            "DIRECT IMAGE COMMAND"
        )

        await HandleImageGeneration(
            query
        )

        return


    # ========================================================
    # 2. FAST COMMANDS
    # ========================================================

    fast_tasks = FastCommandDetection(
        query
    )

    if fast_tasks:

        print(
            "FAST TASK:",
            fast_tasks
        )

        await ProcessTasks(
            fast_tasks
        )

        return


    # ========================================================
    # 3. REALTIME
    # ========================================================

    if IsRealtimeQuery(query):

        print(
            "DIRECT REALTIME COMMAND"
        )

        await HandleRealtimeQuery(
            query
        )

        return


    # ========================================================
    # 4. DECISION MODEL
    # ========================================================

    print(
        "Sending to Decision Model..."
    )

    SetStatus(
        "Understanding..."
    )

    try:

        tasks = await asyncio.to_thread(
            FirstLayerDMM,
            query
        )

        print(
            "Decision Model Output:",
            tasks
        )

    except Exception as e:

        print(
            "Decision Model Error:",
            repr(e)
        )

        traceback.print_exc()

        await HandleGeneralQuery(
            query
        )

        return


    # ========================================================
    # 5. PROCESS MODEL RESULT
    # ========================================================

    if tasks:

        await ProcessTasks(
            tasks
        )

    else:

        print(
            "Model returned no task."
        )

        await HandleGeneralQuery(
            query
        )


# ============================================================
# BACKEND LOOP
# ============================================================

async def BackendLoop():

    global RUNNING

    print()
    print(
        "Assistant backend started."
    )

    print(
        "Waiting for microphone..."
    )


    await StartupGreeting()


    while RUNNING:

        try:


            # ------------------------------------------------
            # MICROPHONE OFF
            # ------------------------------------------------

            if not MicrophoneEnabled():

                await asyncio.sleep(
                    0.2
                )

                continue


            # ------------------------------------------------
            # LISTEN
            # ------------------------------------------------

            print()
            print("=" * 60)

            print(
                "LISTENING..."
            )

            print("=" * 60)

            SetStatus(
                "Listening..."
            )


            query = await asyncio.to_thread(
                SpeechRecognition
            )


            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            if query:

                print(
                    "RECOGNIZED:",
                    query
                )

                SetStatus(
                    "Processing..."
                )

                await ProcessQuery(
                    query
                )

            else:

                print(
                    "No speech detected."
                )

                SetStatus(
                    "Ready"
                )


            await asyncio.sleep(
                0.1
            )


        except Exception as e:

            print()
            print(
                "BACKEND ERROR:"
            )

            print(
                repr(e)
            )

            traceback.print_exc()

            SetStatus(
                "Ready"
            )

            await asyncio.sleep(
                0.5
            )


# ============================================================
# START BACKEND
# ============================================================

def StartBackend():

    try:

        asyncio.run(
            BackendLoop()
        )

    except Exception as e:

        print(
            "Backend stopped:",
            repr(e)
        )

        traceback.print_exc()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "Starting Assistant..."
    )


    backend_thread = threading.Thread(
        target=StartBackend,
        daemon=True
    )

    backend_thread.start()


    try:

        GraphicalUserInterface()

    except KeyboardInterrupt:

        print(
            "\nAssistant stopped."
        )

    except Exception as e:

        print(
            "\nGUI ERROR:"
        )

        print(
            repr(e)
        )

        traceback.print_exc()

    finally:

        RUNNING = False

        print(
            "\nAssistant closed."
        )
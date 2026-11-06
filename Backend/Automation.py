from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import playonyt
from dotenv import dotenv_values
from rich import print
from groq import Groq
import webbrowser
import subprocess
import keyboard
import asyncio
import os
import re
import time


# ============================================================
# ENVIRONMENT
# ============================================================

env_vars = dotenv_values(".env")

GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")

client = Groq(api_key=GroqAPIKey)

messages = []

SystemChatBot = [
    {
        "role": "system",
        "content": (
            f"Hello, I am {Username}. "
            "You are a content writer. "
            "Write letters, applications, notes, explanations "
            "and other requested content."
        )
    }
]


# ============================================================
# PROJECT DIRECTORIES
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

LETTERS_DIR = os.path.join(
    BASE_DIR,
    "Letters"
)

PROJECTS_DIR = os.path.join(
    BASE_DIR,
    "Projects"
)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LETTERS_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)


# ============================================================
# HELPER - CLEAN COMMAND
# ============================================================

def CleanCommand(command):

    command = str(command).strip()

    # Remove final punctuation from voice recognition
    command = command.rstrip(".,!?;:")

    # Remove extra spaces
    command = re.sub(
        r"\s+",
        " ",
        command
    )

    return command.strip()


# ============================================================
# HELPER - CLEAN FILE NAME
# ============================================================

def CleanFileName(filename):

    filename = str(filename).strip()

    # Remove Windows-invalid characters
    filename = re.sub(
        r'[<>:"/\\|?*]',
        "",
        filename
    )

    filename = filename.rstrip("., ")

    if not filename:
        filename = "untitled"

    return filename


# ============================================================
# FIND VS CODE
# ============================================================

def GetVSCodePath():

    possible_paths = [

        # Current Windows user installation
        os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
        ),

        # System installation
        r"C:\Program Files\Microsoft VS Code\Code.exe",

        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",

        # Old path from your system
        r"C:\Users\rahul\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    ]

    for path in possible_paths:

        if os.path.exists(path):
            return path

    return None


# ============================================================
# GOOGLE SEARCH
# ============================================================

def GoogleSearch(Topic):

    Topic = CleanCommand(Topic)

    print(
        f"Google Search: {Topic}"
    )

    url = (
        "https://www.google.com/search?q="
        + Topic.replace(" ", "+")
    )

    webbrowser.open(url)

    return True


# ============================================================
# CONTENT GENERATOR
# ============================================================

def GenerateContent(Topic):

    Topic = CleanCommand(Topic)

    # --------------------------------------------------------
    # SHORT NOTE
    # --------------------------------------------------------

    if "short note" in Topic.lower():

        prompt = (
            f"Write a short, point-wise note on {Topic}. "
            "Use numbered points and clean alignment. "
            "Do not include Date, To, From, or Subject."
        )

    # --------------------------------------------------------
    # LETTER
    # --------------------------------------------------------

    elif "letter" in Topic.lower():

        prompt = (
            f"Write a formal letter on {Topic}. "
            "Include Date, To, From, Subject, greeting, "
            "body, and closing."
        )

    # --------------------------------------------------------
    # NORMAL CONTENT
    # --------------------------------------------------------

    else:

        prompt = (
            f"Write a clear explanation on {Topic} "
            "in simple essay style."
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=SystemChatBot + messages,
        max_tokens=800,
        temperature=0.7,
        top_p=1,
        stream=True
    )

    Answer = ""

    for chunk in completion:

        if chunk.choices[0].delta.content:

            Answer += (
                chunk.choices[0].delta.content
            )

    Answer = (
        Answer
        .replace("</s>", "")
        .strip()
    )

    messages.append(
        {
            "role": "assistant",
            "content": Answer
        }
    )

    return Answer


# ============================================================
# CONTENT
# ============================================================

def Content(Topic, open_file=True):

    Topic = CleanCommand(Topic)

    print(
        f"Generating content: {Topic}"
    )

    ContentByAI = GenerateContent(
        Topic
    )

    filename = CleanFileName(
        Topic.lower().replace(
            " ",
            "_"
        )
    )

    if not filename.endswith(".txt"):

        filename += ".txt"

    file_path = os.path.join(
        DATA_DIR,
        filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            ContentByAI
        )

    print(
        f"Saved: {file_path}"
    )

    if open_file:

        subprocess.Popen(
            [
                "notepad.exe",
                file_path
            ]
        )

    return ContentByAI


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def YoutubeSearch(Topic):

    Topic = CleanCommand(Topic)

    print(
        f"YouTube Search: {Topic}"
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + Topic.replace(" ", "+")
    )

    webbrowser.open(url)

    return True


# ============================================================
# PLAY YOUTUBE
# ============================================================

def PlayYoutube(query):

    query = CleanCommand(query)

    print(
        f"Playing YouTube: {query}"
    )

    playonyt(query)

    return True


# ============================================================
# OPEN CHATGPT
# ============================================================

def OpenChatGPT():

    print(
        "Opening ChatGPT..."
    )

    webopen(
        "https://chatgpt.com/"
    )

    return True


# ============================================================
# OPEN INSTAGRAM
# ============================================================

def OpenInstagram():

    print(
        "Opening Instagram..."
    )

    webopen(
        "https://www.instagram.com/"
    )

    return True


# ============================================================
# OPEN INSTAGRAM REELS
# ============================================================

def OpenInstagramReels():

    print(
        "Opening Instagram Reels..."
    )

    webopen(
        "https://www.instagram.com/reels/"
    )

    return True


# ============================================================
# OPEN WHATSAPP WEB
# ============================================================

def OpenWhatsApp():

    print(
        "Opening WhatsApp Web..."
    )

    webopen(
        "https://web.whatsapp.com/"
    )

    return True


# ============================================================
# OPEN VS CODE AND CREATE FILE
# ============================================================

def OpenVSCodeAndWriteFile(
    filename: str,
    code: str = ""
):

    filename = CleanFileName(
        filename
    )

    if not filename:

        filename = "main.py"

    file_path = os.path.join(
        PROJECTS_DIR,
        filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(code)

    vscode_path = GetVSCodePath()

    # --------------------------------------------------------
    # NORMAL VS CODE PATH
    # --------------------------------------------------------

    if vscode_path:

        print(
            f"Opening VS Code: {file_path}"
        )

        subprocess.Popen(
            [
                vscode_path,
                file_path
            ]
        )

        return True

    # --------------------------------------------------------
    # CODE COMMAND FALLBACK
    # --------------------------------------------------------

    try:

        subprocess.Popen(
            [
                "code",
                file_path
            ]
        )

        return True

    except Exception:

        print(
            "VS Code was not found."
        )

        return False


# ============================================================
# OPEN APPLICATION
# ============================================================

def OpenApp(app):

    app = CleanCommand(
        app
    ).lower()

    print(
        f"Opening: {app}"
    )

    # ========================================================
    # CHROME
    # ========================================================

    if app in [
        "chrome",
        "google chrome"
    ]:

        try:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    "chrome"
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return True

        except Exception:

            webopen(
                "https://www.google.com/"
            )

            return True

    # ========================================================
    # VS CODE
    # ========================================================

    if app in [
        "vs code",
        "vscode",
        "visual studio code"
    ]:

        vscode_path = GetVSCodePath()

        if vscode_path:

            subprocess.Popen(
                [
                    vscode_path
                ]
            )

            return True

        try:

            subprocess.Popen(
                [
                    "code"
                ]
            )

            return True

        except Exception:

            print(
                "VS Code was not found."
            )

            return False

    # ========================================================
    # CHATGPT
    # ========================================================

    if app in [
        "chatgpt",
        "gpt",
        "chat gpt"
    ]:

        return OpenChatGPT()

    # ========================================================
    # INSTAGRAM
    # ========================================================

    if app in [
        "instagram",
        "insta"
    ]:

        return OpenInstagram()

    # ========================================================
    # INSTAGRAM REELS
    # ========================================================

    if app in [
        "instagram reels",
        "instagram reel",
        "insta reels",
        "reels"
    ]:

        return OpenInstagramReels()

    # ========================================================
    # WHATSAPP
    # ========================================================

    if app in [
        "whatsapp",
        "whatsapp web"
    ]:

        return OpenWhatsApp()

    # ========================================================
    # NORMAL APP OPENER
    # ========================================================

    try:

        appopen(
            app,
            match_closest=True,
            output=True,
            throw_error=True
        )

        return True

    except Exception as e:

        print(
            f"AppOpener error: {e}"
        )

        # Browser fallback
        webopen(
            "https://www.google.com/search?q="
            + app.replace(" ", "+")
        )

        return True


# ============================================================
# CLOSE APPLICATION
# ============================================================

def CloseApp(app):

    app = CleanCommand(
        app
    ).lower()

    print(
        f"Closing: {app}"
    )

    # ========================================================
    # CHROME
    # ========================================================

    if app in [
        "chrome",
        "google chrome"
    ]:

        try:

            result = subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/IM",
                    "chrome.exe",
                    "/T"
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:

                print(
                    "Chrome closed successfully."
                )

                return True

            output = (
                result.stdout
                + " "
                + result.stderr
            ).lower()

            if (
                "not found" in output
                or "no running instance" in output
            ):

                print(
                    "Chrome is not running."
                )

                return True

            print(
                "Chrome could not be closed:"
            )

            print(
                result.stderr
            )

            return False

        except Exception as e:

            print(
                f"Chrome close error: {e}"
            )

            return False

    # ========================================================
    # EDGE
    # ========================================================

    if app in [
        "edge",
        "microsoft edge"
    ]:

        try:

            result = subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/IM",
                    "msedge.exe",
                    "/T"
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return result.returncode == 0

        except Exception:

            return False

    # ========================================================
    # FIREFOX
    # ========================================================

    if app in [
        "firefox",
        "mozilla firefox"
    ]:

        try:

            result = subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/IM",
                    "firefox.exe",
                    "/T"
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return result.returncode == 0

        except Exception:

            return False

    # ========================================================
    # NORMAL APPS
    # ========================================================

    try:

        close(
            app,
            match_closest=True,
            output=True,
            throw_error=True
        )

        print(
            f"{app} closed successfully."
        )

        return True

    except Exception as e:

        print(
            f"AppOpener could not close {app}: {e}"
        )

    # ========================================================
    # WINDOWS TASKKILL FALLBACK
    # ========================================================

    process_name = (
        app.replace(" ", "")
        + ".exe"
    )

    try:

        result = subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                process_name,
                "/T"
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:

            print(
                f"{app} closed using taskkill."
            )

            return True

    except Exception as e:

        print(
            f"Taskkill error: {e}"
        )

    return False


# ============================================================
# SYSTEM
# ============================================================

def System(command):

    command = CleanCommand(
        command
    ).lower()

    print(
        f"System command: {command}"
    )

    if command == "mute":

        keyboard.press_and_release(
            "volume mute"
        )

    elif command == "unmute":

        keyboard.press_and_release(
            "volume mute"
        )

    elif command == "volume up":

        keyboard.press_and_release(
            "volume up"
        )

    elif command == "volume down":

        keyboard.press_and_release(
            "volume down"
        )

    else:

        print(
            f"Unknown system command: {command}"
        )

        return False

    return True


# ============================================================
# WRITE IN NOTEPAD / LETTER
# ============================================================

def WriteInNotepad(content):

    content = CleanCommand(
        content
    )

    print(
        f"Creating document: {content}"
    )

    # Generate content only once
    ContentByAI = GenerateContent(
        content
    )

    filename = CleanFileName(
        content.lower().replace(
            " ",
            "_"
        )
    )

    if not filename.endswith(".txt"):

        filename += ".txt"

    file_path = os.path.join(
        LETTERS_DIR,
        filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            ContentByAI
        )

    print(
        f"Saved in Letters: {file_path}"
    )

    subprocess.Popen(
        [
            "notepad.exe",
            file_path
        ]
    )

    return True


# ============================================================
# WHATSAPP MONITOR
# ============================================================

def StartWhatsAppMonitor():

    print(
        "Starting WhatsApp monitoring..."
    )

    OpenWhatsApp()

    print(
        "WhatsApp Web opened."
    )

    print(
        "WhatsApp monitoring is ready."
    )

    return True


# ============================================================
# CHATGPT + QUESTION
# ============================================================

def OpenChatGPTAndAsk(question):

    question = CleanCommand(
        question
    )

    print(
        f"Opening ChatGPT and preparing question: {question}"
    )

    # Open ChatGPT
    webopen(
        "https://chatgpt.com/"
    )

    # Give browser a moment to open
    time.sleep(2)

    print(
        "ChatGPT opened."
    )

    print(
        f"Question: {question}"
    )

    # NOTE:
    # Actual typing into ChatGPT requires browser/UI
    # automation. This function currently opens ChatGPT
    # and prepares the requested question.

    return True


# ============================================================
# TRANSLATE AND EXECUTE
# ============================================================

async def TranslateAndExecute(
    commands: list[str]
):

    funcs = []

    for command in commands:

        command = CleanCommand(
            command
        )

        command_lower = command.lower()

        print(
            f"Processing: {command_lower}"
        )

        # ====================================================
        # CHATGPT + QUESTION
        # ====================================================

        if command_lower.startswith(
            "open chatgpt and ask"
        ):

            question = command[
                len("open chatgpt and ask"):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    OpenChatGPTAndAsk,
                    question
                )
            )

        # ====================================================
        # CHATGPT
        # ====================================================

        elif command_lower in [
            "open chatgpt",
            "open chat gpt",
            "open gpt"
        ]:

            funcs.append(
                asyncio.to_thread(
                    OpenChatGPT
                )
            )

        # ====================================================
        # INSTAGRAM REELS
        # ====================================================

        elif command_lower in [
            "open instagram reels",
            "open instagram reel",
            "open insta reels",
            "open reels"
        ]:

            funcs.append(
                asyncio.to_thread(
                    OpenInstagramReels
                )
            )

        # ====================================================
        # INSTAGRAM
        # ====================================================

        elif command_lower in [
            "open instagram",
            "open insta"
        ]:

            funcs.append(
                asyncio.to_thread(
                    OpenInstagram
                )
            )

        # ====================================================
        # WHATSAPP MONITOR
        # ====================================================

        elif (
            "monitor whatsapp" in command_lower
            or "watch whatsapp" in command_lower
            or "keep monitoring whatsapp" in command_lower
            or "monitor my whatsapp" in command_lower
        ):

            funcs.append(
                asyncio.to_thread(
                    StartWhatsAppMonitor
                )
            )

        # ====================================================
        # WHATSAPP
        # ====================================================

        elif command_lower in [
            "open whatsapp",
            "open whatsapp web"
        ]:

            funcs.append(
                asyncio.to_thread(
                    OpenWhatsApp
                )
            )

        # ====================================================
        # VS CODE + CREATE FILE
        # ====================================================

        elif command_lower.startswith(
            "open vs code and create"
        ):

            parts = command.split()

            if "file" in parts:

                file_index = parts.index(
                    "file"
                )

                if file_index + 1 < len(parts):

                    filename = parts[
                        file_index + 1
                    ]

                    code = ""

                    if "write" in parts:

                        write_index = parts.index(
                            "write"
                        )

                        code = " ".join(
                            parts[
                                write_index + 1:
                            ]
                        )

                    funcs.append(
                        asyncio.to_thread(
                            OpenVSCodeAndWriteFile,
                            filename,
                            code
                        )
                    )

        # ====================================================
        # YOUTUBE + PLAY
        # ====================================================

        elif command_lower.startswith(
            "open youtube and play"
        ):

            song = command[
                len(
                    "open youtube and play"
                ):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    PlayYoutube,
                    song
                )
            )

        # ====================================================
        # WRITE IN NOTEPAD
        # ====================================================

        elif (
            command_lower.startswith(
                "write "
            )
            and " in notepad" in command_lower
        ):

            text = command[
                len("write "):
            ]

            text = text.rsplit(
                " in notepad",
                1
            )[0].strip()

            funcs.append(
                asyncio.to_thread(
                    WriteInNotepad,
                    text
                )
            )

        # ====================================================
        # OPEN
        # ====================================================

        elif command_lower.startswith(
            "open "
        ):

            app = command[
                len("open "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    OpenApp,
                    app
                )
            )

        # ====================================================
        # CLOSE
        # ====================================================

        elif command_lower.startswith(
            "close "
        ):

            app = command[
                len("close "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    CloseApp,
                    app
                )
            )

        # ====================================================
        # PLAY
        # ====================================================

        elif command_lower.startswith(
            "play "
        ):

            song = command[
                len("play "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    PlayYoutube,
                    song
                )
            )

        # ====================================================
        # CONTENT
        # ====================================================

        elif command_lower.startswith(
            "content "
        ):

            topic = command[
                len("content "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    Content,
                    topic
                )
            )

        # ====================================================
        # GOOGLE SEARCH
        # ====================================================

        elif command_lower.startswith(
            "google search "
        ):

            topic = command[
                len("google search "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    GoogleSearch,
                    topic
                )
            )

        # ====================================================
        # YOUTUBE SEARCH
        # ====================================================

        elif command_lower.startswith(
            "youtube search "
        ):

            topic = command[
                len("youtube search "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    YoutubeSearch,
                    topic
                )
            )

        # ====================================================
        # SYSTEM
        # ====================================================

        elif command_lower.startswith(
            "system "
        ):

            system_command = command[
                len("system "):
            ].strip()

            funcs.append(
                asyncio.to_thread(
                    System,
                    system_command
                )
            )

        # ====================================================
        # UNKNOWN
        # ====================================================

        else:

            print(
                f"No Function Found For: "
                f"{command}"
            )

    # ========================================================
    # NOTHING TO EXECUTE
    # ========================================================

    if not funcs:

        return False

    # ========================================================
    # RUN ALL TASKS
    # ========================================================

    results = await asyncio.gather(
        *funcs,
        return_exceptions=True
    )

    for result in results:

        if isinstance(
            result,
            Exception
        ):

            print(
                f"Execution Error: {result}"
            )

        else:

            print(
                f"Executed: {result}"
            )

    return True


# ============================================================
# AUTOMATION
# ============================================================

async def Automation(
    commands: list[str]
):

    return await TranslateAndExecute(
        commands
    )


# ============================================================
# DIRECT TESTING
# ============================================================

if __name__ == "__main__":

    print(
        "\n============================================"
    )

    print(
        "        AUTOMATION SYSTEM READY"
    )

    print(
        "============================================\n"
    )

    print(
        "Examples:"
    )

    print(
        "  open chrome"
    )

    print(
        "  close chrome"
    )

    print(
        "  open chatgpt"
    )

    print(
        "  open chatgpt and ask what is Python"
    )

    print(
        "  open instagram reels"
    )

    print(
        "  open whatsapp"
    )

    print(
        "  monitor whatsapp"
    )

    print(
        "  write a leave letter in notepad"
    )

    print(
        "  open vs code and create file test.py "
        "and write print('Hello')"
    )

    print(
        "  play relaxing music"
    )

    print(
        "  google search Python"
    )

    print(
        "\nType 'exit' to quit.\n"
    )

    while True:

        user_input = input(
            "Command: "
        ).strip()

        if user_input.lower() == "exit":

            print(
                "Exiting automation system..."
            )

            break

        commands = [
            cmd.strip()
            for cmd in user_input.split(",")
            if cmd.strip()
        ]

        asyncio.run(
            Automation(commands)
        )
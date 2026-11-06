from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    InvalidSessionIdException,
    WebDriverException
)

from dotenv import dotenv_values
import os
import time
import threading


# ============================================================
# BASE PATHS
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

FRONTEND_FILES_DIR = os.path.join(
    BASE_DIR,
    "Frontend",
    "Files"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

os.makedirs(
    FRONTEND_FILES_DIR,
    exist_ok=True
)


# ============================================================
# DRIVER PATH
# ============================================================

ChromeDriverPath = os.path.join(
    BASE_DIR,
    "drivers",
    "chromedriver-win64",
    "chromedriver.exe"
)


# ============================================================
# VOICE HTML
# ============================================================

VoiceHTMLPath = os.path.join(
    DATA_DIR,
    "Voice.html"
)


# ============================================================
# LANGUAGE FILE
# ============================================================

LanguageFile = os.path.join(
    DATA_DIR,
    "Language.data"
)


# ============================================================
# DEFAULT LANGUAGE
# ============================================================

DEFAULT_LANGUAGE = "en-US"


# ============================================================
# LANGUAGE MAP
# ============================================================

LANGUAGE_MAP = {

    "english": "en-US",
    "en": "en-US",

    "telugu": "te-IN",
    "te": "te-IN",

    "hindi": "hi-IN",
    "hi": "hi-IN",

    "tamil": "ta-IN",
    "ta": "ta-IN",

    "kannada": "kn-IN",
    "kn": "kn-IN",

    "malayalam": "ml-IN",
    "ml": "ml-IN",

    "bengali": "bn-IN",
    "bangla": "bn-IN",
    "bn": "bn-IN",

    "marathi": "mr-IN",
    "mr": "mr-IN",

    "gujarati": "gu-IN",
    "gu": "gu-IN",

    "punjabi": "pa-IN",
    "pa": "pa-IN",

    "urdu": "ur-IN",
    "ur": "ur-IN"

}


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

env_vars = dotenv_values(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

InputLanguage = env_vars.get(
    "InputLanguage"
)

if not InputLanguage:

    InputLanguage = DEFAULT_LANGUAGE


# ============================================================
# DRIVER
# ============================================================

driver = None

driver_lock = threading.Lock()


# ============================================================
# GET CURRENT LANGUAGE
# ============================================================

def GetLanguage():

    try:

        if os.path.exists(
            LanguageFile
        ):

            with open(
                LanguageFile,
                "r",
                encoding="utf-8"
            ) as file:

                language = file.read().strip()

                if language:

                    return language

    except Exception:

        pass

    return InputLanguage


# ============================================================
# GET LANGUAGE CODE
# ============================================================

def GetLanguageCode(language=None):

    if not language:

        language = GetLanguage()

    language = language.strip().lower()

    if "-" in language:

        return language

    return LANGUAGE_MAP.get(
        language,
        DEFAULT_LANGUAGE
    )


# ============================================================
# SET LANGUAGE
# ============================================================

def SetLanguage(language):

    language = language.strip().lower()

    language_code = LANGUAGE_MAP.get(
        language
    )

    if not language_code:

        if "-" in language:

            language_code = language

        else:

            print(
                "Unsupported language:",
                language
            )

            return False


    try:

        with open(
            LanguageFile,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                language_code
            )


        print(
            "Input language changed to:",
            language_code
        )


        # Recreate Voice.html
        CreateVoiceHTML()


        # Reload the Chrome page immediately
        # so the new recognition language is used.

        global driver

        with driver_lock:

            if driver is not None:

                try:

                    file_url = (
                        "file:///"
                        +
                        VoiceHTMLPath.replace(
                            "\\",
                            "/"
                        )
                    )

                    driver.get(
                        file_url
                    )

                    print(
                        "Speech recognition page reloaded."
                    )

                except Exception as e:

                    print(
                        "Could not reload speech page:",
                        e
                    )


        return True


    except Exception as e:

        print(
            "Language change error:",
            e
        )

        return False


# ============================================================
# CREATE VOICE HTML
# ============================================================

def CreateVoiceHTML():

    language_code = GetLanguageCode()


    HtmlCode = f'''<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>Speech Recognition</title>

</head>

<body>

    <button
        id="start"
        onclick="startRecognition()"
    >
        Start Recognition
    </button>

    <button
        id="end"
        onclick="stopRecognition()"
    >
        Stop Recognition
    </button>

    <p id="output"></p>


    <script>

        const output =
            document.getElementById("output");

        let recognition = null;


        function startRecognition() {{

            try {{

                if (recognition) {{

                    try {{

                        recognition.stop();

                    }} catch(e) {{}}

                }}


                recognition =
                    new webkitSpeechRecognition();


                recognition.lang =
                    "{language_code}";


                recognition.continuous =
                    false;


                recognition.interimResults =
                    false;


                recognition.maxAlternatives =
                    1;


                recognition.onresult =
                    function(event) {{

                        const transcript =
                            event.results[0][0].transcript;


                        output.textContent =
                            transcript;

                    }};


                recognition.onerror =
                    function(event) {{

                        console.log(
                            "Speech error:",
                            event.error
                        );

                    }};


                recognition.onend =
                    function() {{

                        console.log(
                            "Recognition ended"
                        );

                    }};


                recognition.start();

            }}

            catch(error) {{

                console.log(
                    "Recognition start error:",
                    error
                );

            }}

        }}


        function stopRecognition() {{

            if (recognition) {{

                try {{

                    recognition.stop();

                }} catch(e) {{}}

            }}

        }}

    </script>

</body>

</html>
'''


    try:

        with open(
            VoiceHTMLPath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                HtmlCode
            )

        return True


    except Exception as e:

        print(
            "Voice HTML error:",
            e
        )

        return False


# ============================================================
# CREATE DRIVER
# ============================================================

def CreateDriver():

    global driver

    with driver_lock:

        if driver is not None:

            try:

                driver.quit()

            except Exception:

                pass

            driver = None


        try:

            chrome_options = Options()


            chrome_options.add_argument(
                "--use-fake-ui-for-media-stream"
            )

            chrome_options.add_argument(
                "--disable-notifications"
            )

            chrome_options.add_argument(
                "--disable-infobars"
            )

            chrome_options.add_argument(
                "--disable-popup-blocking"
            )

            chrome_options.add_argument(
                "--disable-background-networking"
            )

            chrome_options.add_argument(
                "--disable-sync"
            )

            chrome_options.add_argument(
                "--no-first-run"
            )

            chrome_options.add_argument(
                "--no-default-browser-check"
            )


            chrome_options.add_experimental_option(
                "excludeSwitches",
                ["enable-logging"]
            )


            service = Service(
                ChromeDriverPath
            )


            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )


            driver.set_page_load_timeout(
                10
            )


            print(
                "Speech recognition Chrome started."
            )


            return driver


        except Exception as e:

            print(
                "Chrome driver creation error:",
                e
            )

            driver = None

            return None


# ============================================================
# CHECK DRIVER
# ============================================================

def IsDriverAlive():

    global driver

    if driver is None:

        return False


    try:

        driver.current_url

        return True


    except (
        InvalidSessionIdException,
        WebDriverException
    ):

        return False


    except Exception:

        return False


# ============================================================
# GET DRIVER
# ============================================================

def GetDriver():

    global driver

    if not IsDriverAlive():

        print(
            "Speech session is not available."
        )

        print(
            "Restarting speech Chrome..."
        )

        CreateDriver()

    return driver


# ============================================================
# LOAD VOICE PAGE
# ============================================================

def LoadVoicePage():

    global driver

    driver = GetDriver()


    if driver is None:

        return False


    try:

        file_url = (
            "file:///"
            +
            VoiceHTMLPath.replace(
                "\\",
                "/"
            )
        )


        current_url = driver.current_url


        if current_url != file_url:

            driver.get(
                file_url
            )

        return True


    except (
        InvalidSessionIdException,
        WebDriverException
    ):

        print(
            "Speech Chrome session expired."
        )

        CreateDriver()


        if driver is None:

            return False


        try:

            file_url = (
                "file:///"
                +
                VoiceHTMLPath.replace(
                    "\\",
                    "/"
                )
            )

            driver.get(
                file_url
            )

            return True


        except Exception as e:

            print(
                "Could not reload Voice.html:",
                e
            )

            return False


    except Exception as e:

        print(
            "Voice page error:",
            e
        )

        return False


# ============================================================
# ASSISTANT STATUS
# ============================================================

def SetAssistantStatus(Status):

    try:

        StatusFile = os.path.join(
            FRONTEND_FILES_DIR,
            "Status.data"
        )


        with open(
            StatusFile,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                Status
            )


    except Exception:

        pass


# ============================================================
# QUERY MODIFIER
# ============================================================

def QueryModifier(Query):

    if not Query:

        return ""


    # Keep original language and characters.

    new_query = Query.strip()


    if not new_query:

        return ""


    if new_query[-1] not in [
        ".",
        "?",
        "!"
    ]:

        new_query += "."


    return new_query


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def SpeechRecognition():

    global driver


    try:

        # Create/update Voice.html
        CreateVoiceHTML()


        if not LoadVoicePage():

            time.sleep(1)

            return ""


        # Clear old output

        try:

            driver.execute_script(
                """
                document.getElementById('output').textContent = '';
                """
            )

        except Exception:

            pass


        # Start recognition

        try:

            driver.find_element(
                by=By.ID,
                value="start"
            ).click()


        except (
            InvalidSessionIdException,
            WebDriverException
        ):

            print(
                "Speech session lost while starting."
            )

            CreateDriver()

            return ""


        except Exception as e:

            print(
                "Could not start recognition:",
                e
            )

            return ""


        print(
            "Listening..."
        )


        # Wait maximum 15 seconds

        start_time = time.time()

        timeout = 15


        while (
            time.time() - start_time
            <
            timeout
        ):


            try:

                Text = driver.find_element(
                    by=By.ID,
                    value="output"
                ).text.strip()


                if Text:

                    # Stop recognition

                    try:

                        driver.find_element(
                            by=By.ID,
                            value="end"
                        ).click()

                    except Exception:

                        pass


                    print(
                        "Recognized:",
                        Text
                    )


                    # Return original language.

                    return QueryModifier(
                        Text
                    )


            except (
                InvalidSessionIdException,
                WebDriverException
            ):

                print(
                    "Speech Chrome session lost."
                )

                CreateDriver()

                return ""


            except Exception:

                pass


            time.sleep(
                0.05
            )


        # Timeout

        try:

            driver.find_element(
                by=By.ID,
                value="end"
            ).click()

        except Exception:

            pass


        print(
            "Listening timeout."
        )


        return ""


    except (
        InvalidSessionIdException,
        WebDriverException
    ) as e:

        print(
            "Speech session error:",
            e
        )

        CreateDriver()

        return ""


    except Exception as e:

        print(
            "Speech Recognition Error:",
            e
        )

        return ""


# ============================================================
# CLOSE DRIVER
# ============================================================

def CloseSpeechDriver():

    global driver

    with driver_lock:

        if driver is not None:

            try:

                driver.quit()

            except Exception:

                pass

            driver = None

            print(
                "Speech Chrome closed."
            )


# ============================================================
# INITIALIZATION
# ============================================================

CreateVoiceHTML()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Speech Recognition Test"
    )

    print(
        "Current language:",
        GetLanguageCode()
    )


    while True:

        Text = SpeechRecognition()


        if Text:

            print(
                "You said:",
                Text
            )


        time.sleep(
            
            0.2
        )
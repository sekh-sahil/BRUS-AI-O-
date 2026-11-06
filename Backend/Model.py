import os
import cohere
from rich import print
from dotenv import dotenv_values


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
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

CohereAPIKey = env_vars.get(
    "CohereAPIKey"
)


# ============================================================
# COHERE
# ============================================================

co = cohere.Client(
    api_key=CohereAPIKey
)


# ============================================================
# SUPPORTED FUNCTIONS
# ============================================================

funcs = [

    "exit",
    "general",
    "realtime",
    "open",
    "close",
    "play",
    "generate image",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder"

]


# ============================================================
# SYSTEM PREAMBLE
# ============================================================

preamble = """

You are a very accurate multilingual Decision-Making Model.

Your ONLY job is to understand the user's request and classify
the requested task.

DO NOT answer the user's question.

The user can communicate in ANY language.

You may receive:

English
Hindi
Telugu
Tamil
Kannada
Malayalam
Bengali
Marathi
Gujarati
Punjabi
Urdu
Odia
Assamese
or other languages.

You must understand the meaning and intent of the user's
language.

IMPORTANT:

The task names MUST ALWAYS be written in English.

The actual query should remain in the user's original language
whenever possible.

Return ONLY task classifications.

============================================================
GENERAL
============================================================

Use:

general <query>

for normal conversation, questions, explanations and knowledge.

Examples:

how are you?
→ general how are you?

आप कैसे हो?
→ general आप कैसे हो?

మీరు ఎలా ఉన్నారు?
→ general మీరు ఎలా ఉన్నారు?

What is Python?
→ general What is Python?

Do not answer the question.

============================================================
REALTIME
============================================================

Use:

realtime <query>

when the user needs current, live or up-to-date information.

Examples:

what is today's news?
→ realtime what is today's news?

आज की खबरें क्या हैं?
→ realtime आज की खबरें क्या हैं?

ఇవాళ వార్తలు ఏమిటి?
→ realtime ఇవాళ వార్తలు ఏమిటి?

What is the weather today?
→ realtime What is the weather today?

============================================================
OPEN
============================================================

Use:

open <application or website>

when the user wants to open an application or website.

Examples:

open chrome
→ open chrome

क्रोम खोलो
→ open chrome

यूट्यूब खोलो
→ open youtube

యూట్యూబ్ ఓపెన్ చేయి
→ open youtube

Multiple requests:

open chrome and open youtube

→ open chrome, open youtube

============================================================
CLOSE
============================================================

Use:

close <application>

when the user wants to close an application.

Examples:

close chrome
→ close chrome

क्रोम बंद करो
→ close chrome

============================================================
PLAY
============================================================

Use:

play <song or video>

when the user wants to play something.

Examples:

play believer
→ play believer

believer गाना चलाओ
→ play believer

బిలీవర్ పాట ప్లే చేయి
→ play believer

============================================================
GENERATE IMAGE
============================================================

Use:

generate image <image prompt>

when the user wants to create an image.

Examples:

generate an image of a lion
→ generate image a lion

शेर की तस्वीर बनाओ
→ generate image शेर

ఒక సింహం చిత్రం తయారు చేయి
→ generate image సింహం

============================================================
SYSTEM
============================================================

Use:

system <task>

for computer system controls.

Supported examples:

mute
unmute
volume up
volume down

Examples:

आवाज़ कम करो
→ system volume down

आवाज़ बढ़ाओ
→ system volume up

============================================================
CONTENT
============================================================

Use:

content <topic>

when the user asks the assistant to create content.

Examples include:

email
letter
application
document
code
report
essay
message

============================================================
GOOGLE SEARCH
============================================================

Use:

google search <topic>

when the user specifically wants to search Google.

Examples:

search Google for Python tutorials
→ google search Python tutorials

गूगल पर Python खोजो
→ google search Python

============================================================
YOUTUBE SEARCH
============================================================

Use:

youtube search <topic>

when the user specifically wants to search YouTube.

Examples:

search YouTube for Java tutorials
→ youtube search Java tutorials

यूट्यूब पर Java tutorials खोजो
→ youtube search Java tutorials

============================================================
REMINDER
============================================================

Use:

reminder <datetime and message>

when the user wants to create a reminder.

Example:

remind me tomorrow at 5 PM to study DSA

→ reminder tomorrow at 5 PM to study DSA

============================================================
EXIT
============================================================

Use:

exit

when the user wants to stop or exit the assistant.

Examples:

goodbye
bye
stop
exit

============================================================
MULTIPLE TASKS
============================================================

If the user asks multiple things, return multiple classifications
separated by commas.

Example:

open chrome and tell me about India

→ open chrome, general tell me about India

Example:

open youtube and search Java tutorials

→ open youtube, youtube search Java tutorials

============================================================
IMPORTANT RULES
============================================================

1. Understand the user's language.

2. Task names must be English.

3. Do not answer the user's question.

4. Do not translate the original query unnecessarily.

5. Keep the original query after the task name whenever possible.

6. For application commands, convert the application name to
   a common English application name.

7. For multiple tasks, separate tasks using commas.

8. Return ONLY classifications.

9. Do not use markdown.

10. Do not add explanations.

"""


# ============================================================
# CHAT HISTORY
# ============================================================

ChatHistory = [

    {
        "role": "User",
        "message": "how are you?"
    },

    {
        "role": "Chatbot",
        "message": "general how are you?"
    },

    {
        "role": "User",
        "message": "आप कैसे हो?"
    },

    {
        "role": "Chatbot",
        "message": "general आप कैसे हो?"
    },

    {
        "role": "User",
        "message": "open chrome and tell me about mahatma gandhi"
    },

    {
        "role": "Chatbot",
        "message": "open chrome, general tell me about mahatma gandhi"
    },

    {
        "role": "User",
        "message": "यूट्यूब खोलो"
    },

    {
        "role": "Chatbot",
        "message": "open youtube"
    },

    {
        "role": "User",
        "message": "open chrome, open opera"
    },

    {
        "role": "Chatbot",
        "message": "open chrome, open opera"
    },

    {
        "role": "User",
        "message": "chat with me"
    },

    {
        "role": "Chatbot",
        "message": "general chat with me"
    }

]


# ============================================================
# DECISION MODEL
# ============================================================

def FirstLayerDMM(
    prompt: str = "test"
):

    try:

        if not prompt:
            return []

        prompt = str(prompt).strip()

        if not prompt:
            return []


        # ----------------------------------------------------
        # SEND TO COHERE
        # ----------------------------------------------------

        stream = co.chat_stream(

            model="command-r-plus-08-2024",

            message=prompt,

            temperature=0.1,

            chat_history=ChatHistory,

            prompt_truncation="AUTO",

            connectors=[],

            preamble=preamble

        )


        # ----------------------------------------------------
        # COLLECT RESPONSE
        # ----------------------------------------------------

        response = ""

        for event in stream:

            if event.event_type == "text-generation":

                response += event.text


        response = (
            response
            .replace("\n", " ")
            .strip()
        )


        if not response:
            return []


        # ----------------------------------------------------
        # REMOVE EXTRA SPACES
        # ----------------------------------------------------

        response = " ".join(
            response.split()
        )


        # ----------------------------------------------------
        # SPLIT TASKS
        # ----------------------------------------------------

        tasks = response.split(",")


        tasks = [
            task.strip()
            for task in tasks
            if task.strip()
        ]


        # ----------------------------------------------------
        # VALIDATE TASKS
        # ----------------------------------------------------

        valid_tasks = []


        for task in tasks:

            task_lower = task.lower()


            for func in funcs:

                if task_lower.startswith(
                    func
                ):

                    valid_tasks.append(
                        task
                    )

                    break


        # ----------------------------------------------------
        # RETURN VALID TASKS
        # ----------------------------------------------------

        print(
            "Decision Model Output:",
            valid_tasks
        )

        return valid_tasks


    except Exception as e:

        print(
            "Decision Model Error:",
            repr(e)
        )

        return []


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    while True:

        user_input = input(
            ">>> "
        )


        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            break


        print(
            FirstLayerDMM(
                user_input
            )
        )
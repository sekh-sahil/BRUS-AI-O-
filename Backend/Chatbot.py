
from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values


# ============================================================
# BASE PATH
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

Username = env_vars.get(
    "Username",
    "User"
)

Assistantname = env_vars.get(
    "Assistantname",
    "Assistant"
)

GroqAPIKey = env_vars.get(
    "GroqAPIKey"
)


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GroqAPIKey
)


# ============================================================
# CHAT FILE
# ============================================================

ChatLogPath = os.path.join(
    BASE_DIR,
    "Data",
    "ChatLog.json"
)

os.makedirs(
    os.path.dirname(ChatLogPath),
    exist_ok=True
)


# ============================================================
# SYSTEM
# ============================================================

System = f"""

Hello, I am {Username}.

You are a helpful, accurate and concise AI assistant named {Assistantname}.

IMPORTANT LANGUAGE RULE:

Always answer in the SAME LANGUAGE used by the user.

If the user speaks English:
Answer in English.

If the user speaks Hindi:
Answer in Hindi.

If the user speaks Telugu:
Answer in Telugu.

If the user speaks Tamil:
Answer in Tamil.

If the user speaks Kannada:
Answer in Kannada.

If the user speaks Malayalam:
Answer in Malayalam.

If the user speaks Bengali:
Answer in Bengali.

If the user speaks Marathi:
Answer in Marathi.

If the user speaks Gujarati:
Answer in Gujarati.

If the user speaks Punjabi:
Answer in Punjabi.

If the user speaks Urdu:
Answer in Urdu.

If the user mixes languages:
Understand the meaning and respond naturally in the same mixed language when appropriate.

Do not translate the user's question into English unless necessary.

Do not mention this language instruction.

Do not provide unnecessary notes.

Keep answers concise and useful.

Do not tell the current time unless the user asks for it.

"""


SystemChatbot = [
    {
        "role": "system",
        "content": System
    }
]


# ============================================================
# LOAD CHAT LOG
# ============================================================

try:

    with open(
        ChatLogPath,
        "r",
        encoding="utf-8"
    ) as f:

        messages = load(f)

        if not isinstance(
            messages,
            list
        ):

            messages = []


except (
    FileNotFoundError,
    Exception
):

    messages = []

    with open(
        ChatLogPath,
        "w",
        encoding="utf-8"
    ) as f:

        dump(
            [],
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# REALTIME INFORMATION
# ============================================================

def RealtimeInformation():

    current_date_time = datetime.datetime.now()

    day = current_date_time.strftime(
        "%A"
    )

    date = current_date_time.strftime(
        "%d"
    )

    month = current_date_time.strftime(
        "%B"
    )

    year = current_date_time.strftime(
        "%Y"
    )

    hour = current_date_time.strftime(
        "%H"
    )

    minute = current_date_time.strftime(
        "%M"
    )

    second = current_date_time.strftime(
        "%S"
    )

    data = (
        "Current real-time information:\n"
    )

    data += (
        f"Day: {day}\n"
    )

    data += (
        f"Date: {date}\n"
    )

    data += (
        f"Month: {month}\n"
    )

    data += (
        f"Year: {year}\n"
    )

    data += (
        f"Time: {hour}:{minute}:{second}\n"
    )

    return data


# ============================================================
# ANSWER MODIFIER
# ============================================================

def AnswerModifier(Answer):

    if not Answer:
        return ""

    lines = Answer.split(
        "\n"
    )

    non_empty_lines = [
        line
        for line in lines
        if line.strip()
    ]

    return "\n".join(
        non_empty_lines
    ).strip()


# ============================================================
# CHATBOT
# ============================================================

def ChatBot(Query):

    try:

        # ----------------------------------------------------
        # LOAD EXISTING HISTORY
        # ----------------------------------------------------

        try:

            with open(
                ChatLogPath,
                "r",
                encoding="utf-8"
            ) as f:

                all_messages = load(f)

                if not isinstance(
                    all_messages,
                    list
                ):

                    all_messages = []

        except Exception:

            all_messages = []


        # ----------------------------------------------------
        # ADD USER MESSAGE
        # ----------------------------------------------------

        all_messages.append(
            {
                "role": "user",
                "content": str(Query)
            }
        )


        # ----------------------------------------------------
        # LIMIT HISTORY
        #
        # This prevents the Groq TPM error you received.
        # ----------------------------------------------------

        MAX_HISTORY_MESSAGES = 6

        recent_messages = all_messages[
            -MAX_HISTORY_MESSAGES:
        ]


        # ----------------------------------------------------
        # CURRENT REQUEST
        # ----------------------------------------------------

        messages_to_send = (
            SystemChatbot
            +
            [
                {
                    "role": "system",
                    "content": RealtimeInformation()
                }
            ]
            +
            recent_messages
        )


        # ----------------------------------------------------
        # GROQ REQUEST
        # ----------------------------------------------------

        completion = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=messages_to_send,

            max_tokens=700,

            temperature=0.4,

            top_p=1,

            stream=True,

            stop=None

        )


        # ----------------------------------------------------
        # COLLECT RESPONSE
        # ----------------------------------------------------

        Answer = ""

        for chunk in completion:

            if (
                chunk.choices
                and
                chunk.choices[0].delta.content
            ):

                Answer += (
                    chunk.choices[0].delta.content
                )


        Answer = Answer.replace(
            "</s>",
            ""
        ).strip()


        # ----------------------------------------------------
        # SAVE FULL HISTORY LOCALLY
        # ----------------------------------------------------

        all_messages.append(
            {
                "role": "assistant",
                "content": Answer
            }
        )


        # Keep local file manageable too.

        if len(all_messages) > 50:

            all_messages = all_messages[
                -50:
            ]


        with open(
            ChatLogPath,
            "w",
            encoding="utf-8"
        ) as f:

            dump(
                all_messages,
                f,
                indent=4,
                ensure_ascii=False
            )


        return AnswerModifier(
            Answer
        )


    except Exception as e:

        print(
            f"ChatBot Error: {e}"
        )

        return (
            "Sorry, I couldn't process your request."
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    while True:

        user_input = input(
            "Ask something: "
        )

        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print(
                "Goodbye!"
            )

            break

        print(
            ChatBot(
                user_input
            )
        )


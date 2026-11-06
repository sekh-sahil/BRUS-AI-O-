from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


def GoogleSearch(query):

    try:
        results = list(search(query, advanced=True, num_results=5))

        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"

        return Answer

    except Exception as e:
        print("Google Search Error:", e)
        return f"No search results are available for '{query}'."


def AnswerModifier(Answer):

    lines = Answer.split('\n')

    non_empty_lines = [
        line for line in lines if line.strip()
    ]

    modified_answer = '\n'.join(non_empty_lines)

    return modified_answer


SystemChatbot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I assist you today?"}
]


def Information():

    data = ""

    current_date_time = datetime.datetime.now()

    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += f"Use This Real-Time Information if needed.\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour}:{minute}:{second}\n"

    return data


def RealtimeSearchEngine(prompt):

    global SystemChatbot, messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({
        "role": "user",
        "content": prompt
    })

    # Search Google only when needed
    search_keywords = [
        "who",
        "what",
        "when",
        "where",
        "which",
        "how",
        "latest",
        "news",
        "price",
        "weather",
        "current",
        "today"
    ]

    prompt_lower = prompt.lower()

    needs_search = any(
        keyword in prompt_lower
        for keyword in search_keywords
    )

    # Don't search Google for time/date questions
    if "time" in prompt_lower or "date" in prompt_lower:
        needs_search = False

    if needs_search:

        SystemChatbot.append({
            "role": "system",
            "content": GoogleSearch(prompt)
        })

    completion = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=SystemChatbot
        + [{"role": "system", "content": Information()}]
        + messages,

        temperature=0.7,

        max_tokens=2048,

        top_p=1,

        stream=True,

        stop=None
    )

    Answer = ""

    for chunk in completion:

        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")

    messages.append({
        "role": "assistant",
        "content": Answer
    })

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    if needs_search:
        SystemChatbot.pop()

    return AnswerModifier(Answer=Answer)


if __name__ == "__main__":

    while True:

        prompt = input("Ask You Query Sir : ")

        print(RealtimeSearchEngine(prompt))
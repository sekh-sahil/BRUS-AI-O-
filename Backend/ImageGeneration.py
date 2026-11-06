
from huggingface_hub import InferenceClient
from dotenv import dotenv_values
from pathlib import Path
import os
import re


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "Data"

IMAGE_DIR = (
    BASE_DIR
    / "Frontend"
    / "Files"
    / "GeneratedImages"
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

IMAGE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# ENVIRONMENT
# ============================================================

env_vars = dotenv_values(
    BASE_DIR / ".env"
)

HuggingFaceAPIKey = env_vars.get(
    "HuggingFaceAPIKey"
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = (
    "black-forest-labs/FLUX.1-schnell"
)


# ============================================================
# CLIENT
# ============================================================

client = None

if HuggingFaceAPIKey:

    client = InferenceClient(
        provider="auto",
        api_key=HuggingFaceAPIKey
    )


# ============================================================
# FILE NAME CLEANER
# ============================================================

def CleanFileName(text):

    text = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text
    )

    text = text.strip("_")

    if not text:

        text = "generated_image"

    return text[:80]


# ============================================================
# EXTRACT IMAGE PROMPT
# ============================================================

def ExtractPrompt(query):

    query = query.strip()

    patterns = [

        r"please generate an image of (.+)",
        r"please generate a image of (.+)",

        r"generate an image of (.+)",
        r"generate a image of (.+)",

        r"create an image of (.+)",
        r"create a image of (.+)",

        r"make an image of (.+)",
        r"make a image of (.+)",

        r"generate image of (.+)",
        r"create image of (.+)",
        r"make image of (.+)",

        r"generate (.+)",
        r"create (.+)",
        r"make (.+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            query,
            re.IGNORECASE
        )

        if match:

            prompt = (
                match.group(1)
                .strip()
            )

            prompt = prompt.rstrip(
                ".,!?"
            )

            return prompt

    return query


# ============================================================
# GENERATE IMAGE
# ============================================================

def GenerateImage(Query):

    try:

        # ----------------------------------------------------
        # API KEY CHECK
        # ----------------------------------------------------

        if not HuggingFaceAPIKey:

            print()
            print(
                "ERROR: HuggingFaceAPIKey "
                "is missing in .env"
            )

            return False


        # ----------------------------------------------------
        # CLIENT CHECK
        # ----------------------------------------------------

        if client is None:

            print()
            print(
                "ERROR: Hugging Face client "
                "was not created."
            )

            return False


        # ----------------------------------------------------
        # PROMPT
        # ----------------------------------------------------

        prompt = ExtractPrompt(
            Query
        )


        if not prompt:

            print(
                "ERROR: Image prompt is empty."
            )

            return False


        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        print()
        print(
            "=" * 60
        )

        print(
            "IMAGE GENERATION"
        )

        print(
            "Model:",
            MODEL_NAME
        )

        print(
            "Provider: auto"
        )

        print(
            "Prompt:",
            prompt
        )

        print(
            "=" * 60
        )


        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        image = client.text_to_image(

            prompt=prompt,

            model=MODEL_NAME

        )


        # ----------------------------------------------------
        # CHECK RESULT
        # ----------------------------------------------------

        if image is None:

            print(
                "ERROR: Model returned no image."
            )

            return False


        # ----------------------------------------------------
        # FILE NAME
        # ----------------------------------------------------

        file_name = CleanFileName(
            prompt
        )


        output_path = (
            IMAGE_DIR
            / f"{file_name}.png"
        )


        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        image.save(
            output_path
        )


        print()
        print(
            "Image generated successfully."
        )

        print(
            "Saved:",
            output_path
        )


        # ----------------------------------------------------
        # SAVE LATEST IMAGE PATH
        # ----------------------------------------------------

        latest_file = (
            DATA_DIR
            / "GeneratedImage.data"
        )


        with open(
            latest_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                str(output_path)
            )


        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        try:

            os.startfile(
                str(output_path)
            )

            print(
                "Image opened automatically."
            )

        except Exception as e:

            print(
                "Could not open image automatically:",
                e
            )


        return True


    except Exception as e:

        print()
        print(
            "=" * 60
        )

        print(
            "IMAGE GENERATION ERROR"
        )

        print(
            repr(e)
        )

        print(
            "=" * 60
        )

        return False


# ============================================================
# ALIAS
# ============================================================

def generate_image(prompt):

    return GenerateImage(
        prompt
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )

    print(
        "IMAGE GENERATION TEST"
    )

    print(
        "=" * 60
    )

    query = input(
        "Enter image prompt: "
    )

    GenerateImage(
        query
    )

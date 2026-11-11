"""Create the Hugging Face Space if needed and copy the settings stored in GitHub into it."""
import os

from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
space = os.environ.get("SPACE", "hsmcgn19/diwan-htr")

api.create_repo(space, repo_type="space", space_sdk="docker", private=True, exist_ok=True)
print("Space ready:", space)

for key in ("GEMINI_API_KEY", "APP_PASSWORD", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"):
    if os.environ.get(key):
        api.add_space_secret(space, key, os.environ[key])
        print("secret copied:", key)

for key in ("HTR_TRAIN_FOLDER", "HTR_TRAIN_TEXT_FOLDER", "HTR_INBOX_FOLDER", "HTR_OUTPUT_FOLDER", "HTR_MODEL"):
    if os.environ.get(key):
        api.add_space_variable(space, key, os.environ[key])
        print("variable copied:", key)

import os

variables = {
    "TELEGRAM_DB_URI": os.getenv("TELEGRAM_DB_URI", ""),
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN", ""),
    "SHEET_ID": os.getenv("SHEET_ID", "")
}

with open("loaded-env.txt", "w") as f:
    for name in variables:
        f.write(f"{name}={variables[name]}\n")
    f.close()

import os

variables = {
    "TELEGRAM_DB_URI": os.getenv('TELEGRAM_DB_URI', '')
}

with open('loaded-env.txt', 'w') as f:
    for name in variables:
        f.write(f'{name}={variables[name]}\n')
    f.close()
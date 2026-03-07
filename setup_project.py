import os
from pathlib import Path

PROJECT_ROOT = Path("gemini_rag")

def main():
    print(f"🚀 INITIALIZING at: {PROJECT_ROOT}")

    for d in ["vscode", "backend", "frontend/src", "frontend/public", "docker"]:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)

    frontend_files = get_frontend_files()
    files = {
        ".gitignore": get_gitignore(),
        ".env": "GEMINI_API_KEY=replace_with_your_key_here",
        "docker-compose.yml": get_docker_compose(),
        "backend/Dockerfile": get_backend_dockerfile(),
        "backend/requirements.txt": get_backend_requirements(),
        "backend/main.py": get_backend_main(),
        "frontend/Dockerfile": get_frontend_dockerfile(),
    }
    files.update(frontend_files)

    for path, content in files.items():
        try:
            with open(PROJECT_ROOT / path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"   -> Created {path}")
        except Exception as e:
            print(f"   ❌ Error creating {path}: {e}")

    print("\n" + "=" * 50)
    print("✅ SUCCESS!")
    print(f"📂 Project: {PROJECT_ROOT}")
    print("1. Open .env and add your GEMINI_API_KEY")
    print(f"2. cd {PROJECT_ROOT}")
    print("3. docker-compose up --build")
    print("=" * 50)


def get_gitignore():
    return "node_modules\n.env\n"


def get_backend_requirements():
    return "flask\nrequests\n"


def get_docker_compose():
    return """version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - GEMINI_API_KEY=replace_with_your_key_here

  frontend:
    build:
      context: ./frontend
      dockerfile: ./frontend/Dockerfile
    ports:
      - 3000:3000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - backend

networks:
  default:
"""


def get_backend_dockerfile():
    return """FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
"""


def get_backend_main():
    return """from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
"""


def get_frontend_dockerfile():
    return """FROM node:16

WORKDIR /app

COPY package.json ./
RUN npm install

COPY ./

EXPOSE 3000

CMD ["npm", "start"]
"""


def get_frontend_files():
    pkg = """{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@tailwindcss/forms": "^0.5.3",
    "autoprefixer": "^10.4.16",
    "daisyui": "^3.13.0",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.0",
    "tailwindcss-forms": "^1.0.0",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.0",
    "tailwindcss-forms": "^1.0.0",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.4"
  },
  "scripts": {
    "dev": "webpack --watch",
    "build": "webpack"
  },
  "browserslist": ["> 1% (chrome, edge, firefox, safari)"]
}
"""
    return {"frontend/package.json": pkg}


if __name__ == "__main__":
    main()

import os

BASE_PATH = "/Users/mattias/Documents/rag-gamified-learning"

structure = {
    ".vscode": [
        "settings.json",
        "launch.json",
    ],
    "backend": {
        "files": [
            "Dockerfile",
            "requirements.txt",
            ".env.example",
        ],
        "app": {
            "files": [
                "__init__.py",
                "main.py",
            ],
            "core": [
                "__init__.py",
                "config.py",
                "database.py",
            ],
            "api": {
                "files": [
                    "__init__.py",
                    "deps.py",
                ],
                "v1": {
                    "files": [
                        "__init__.py",
                    ],
                    "endpoints": [
                        "__init__.py",
                        "upload.py",
                        "search.py",
                        "quiz.py",
                        "stats.py",
                    ],
                },
            },
            "services": [
                "__init__.py",
                "rag_service.py",
                "embedding_service.py",
                "quiz_service.py",
            ],
            "models": [
                "__init__.py",
                "schemas.py",
            ],
        },
        "data": [".gitkeep"],
        "logs": [".gitkeep"],
    },
    "frontend": {
        "files": [
            "Dockerfile",
            "package.json",
            "vite.config.ts",
            "tailwind.config.js",
            "postcss.config.js",
            "tsconfig.json",
            "tsconfig.node.json",
            ".env.example",
        ],
        "public": [
            "vite.svg",
        ],
        "src": {
            "files": [
                "main.tsx",
                "App.tsx",
                "index.css",
            ],
            "components": {
                "ui": [
                    "Button.tsx",
                    "Card.tsx",
                    "Input.tsx",
                    "Badge.tsx",
                ],
                "layout": [
                    "Header.tsx",
                    "Sidebar.tsx",
                    "Layout.tsx",
                ],
                "features": {
                    "Upload": ["UploadZone.tsx"],
                    "Search": ["SearchBar.tsx"],
                    "Quiz": ["QuizComponent.tsx"],
                    "Dashboard": ["DashboardView.tsx"],
                },
            },
            "hooks": [
                "useUser.ts",
                "useApi.ts",
            ],
            "services": [
                "api.ts",
            ],
            "types": [
                "index.ts",
            ],
            "utils": [
                "helpers.ts",
            ],
        },
    },
    "docker": [".gitkeep"],
    "root_files": [
        ".gitignore",
        "README.md",
        "docker-compose.yml",
        "docker-compose.dev.yml",
    ],
}


def create_structure(base_path, tree):
    for name, content in tree.items():
        if name == "root_files":
            for file in content:
                path = os.path.join(base_path, file)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                open(path, "a").close()
        elif isinstance(content, list):
            folder_path = os.path.join(base_path, name)
            os.makedirs(folder_path, exist_ok=True)
            for file in content:
                file_path = os.path.join(folder_path, file)
                open(file_path, "a").close()
        elif isinstance(content, dict):
            folder_path = os.path.join(base_path, name)
            os.makedirs(folder_path, exist_ok=True)

            if "files" in content:
                for file in content["files"]:
                    file_path = os.path.join(folder_path, file)
                    open(file_path, "a").close()

            nested_content = {
                k: v for k, v in content.items() if k != "files"
            }
            create_structure(folder_path, nested_content)


if __name__ == "__main__":
    os.makedirs(BASE_PATH, exist_ok=True)
    create_structure(BASE_PATH, structure)
    print("✅ Project structure created successfully!")
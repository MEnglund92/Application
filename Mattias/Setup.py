import os

# 🔥 RÄTT PATH
BASE_PATH = "/Users/mattias/Documents/GitHub/Application"

structure = {
    ".vscode": ["settings.json", "launch.json"],

    "backend": {
        "__files__": ["Dockerfile", "requirements.txt", ".env.example"],

        "app": {
            "__files__": ["__init__.py", "main.py"],

            "core": ["__init__.py", "config.py", "database.py"],

            "api": {
                "__files__": ["__init__.py", "deps.py"],

                "v1": {
                    "__files__": ["__init__.py"],

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
        "__files__": [
            "Dockerfile",
            "package.json",
            "vite.config.ts",
            "tailwind.config.js",
            "postcss.config.js",
            "tsconfig.json",
            "tsconfig.node.json",
            ".env.example",
        ],

        "public": ["vite.svg"],

        "src": {
            "__files__": ["main.tsx", "App.tsx", "index.css"],

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

            "hooks": ["useUser.ts", "useApi.ts"],
            "services": ["api.ts"],
            "types": ["index.ts"],
            "utils": ["helpers.ts"],
        },
    },

    "docker": [".gitkeep"],

    "__root_files__": [
        ".gitignore",
        "README.md",
        "docker-compose.yml",
        "docker-compose.dev.yml",
    ],
}


def create_structure(base_path, tree):
    for name, content in tree.items():

        # Root files
        if name == "__root_files__":
            for file in content:
                file_path = os.path.join(base_path, file)
                create_file(file_path)
            continue

        folder_path = os.path.join(base_path, name)
        os.makedirs(folder_path, exist_ok=True)

        if isinstance(content, list):
            for file in content:
                file_path = os.path.join(folder_path, file)
                create_file(file_path)

        elif isinstance(content, dict):

            # Files inside folder
            if "__files__" in content:
                for file in content["__files__"]:
                    file_path = os.path.join(folder_path, file)
                    create_file(file_path)

            # Nested folders
            nested = {k: v for k, v in content.items() if k != "__files__"}
            create_structure(folder_path, nested)


def create_file(path):
    if not os.path.exists(path):
        open(path, "w").close()
        print(f"✅ Created: {path}")
    else:
        print(f"⏭ Skipped (exists): {path}")


if __name__ == "__main__":
    print(f"\n📁 Creating project in:\n{BASE_PATH}\n")
    os.makedirs(BASE_PATH, exist_ok=True)
    create_structure(BASE_PATH, structure)
    print("\n🎉 Project structure ready!\n")
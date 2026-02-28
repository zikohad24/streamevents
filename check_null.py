import os

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "rb") as f:
                if b"\x00" in f.read():
                    print("ARCHIVO CORRUPTO:", path)

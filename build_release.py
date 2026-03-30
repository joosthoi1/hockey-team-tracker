import os
import subprocess
import zipfile
from pathlib import Path
import shutil

FILE = ".submodules"
TARGET_DIR = Path("custom_components/hockey_team_tracker")
OUTPUT_ZIP = "release_with_submodules.zip"


def run_command(cmd, cwd=None):
    try:
        subprocess.check_call(cmd, cwd=cwd)
    except subprocess.CalledProcessError:
        print(f"Command failed: {' '.join(cmd)}")
        return False
    return True


def process_line(line):
    parts = line.strip().split()

    if len(parts) == 2:
        repo = parts[0]
        branch = None
        directory = parts[1]
    elif len(parts) >= 3:
        repo = parts[0]
        branch = parts[1]
        directory = parts[2]
    else:
        print(f"Invalid line: {line}")
        return

    if os.path.exists(directory):
        print(f"Updating {directory}...")
        run_command(["git", "-C", directory, "pull"])
    else:
        print(f"Cloning {repo} into {directory}...")
        if branch:
            run_command(["git", "clone", "-b", branch, repo, directory])
        else:
            run_command(["git", "clone", repo, directory])


def load_submodules():
    if not os.path.isfile(FILE):
        print(f"Error: {FILE} not found!")
        return

    with open(FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            process_line(line)


def create_zip():
    if not TARGET_DIR.exists():
        print(f"Error: {TARGET_DIR} does not exist!")
        return

    print(f"Creating zip: {OUTPUT_ZIP}")

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for file_path in TARGET_DIR.rglob("*"):
            if file_path.is_file():
                # Preserve folder structure inside zip
                arcname = file_path.relative_to(TARGET_DIR.parent)
                z.write(file_path, arcname)

    print("Zip created successfully!")


def main():
    load_submodules()
    create_zip()


if __name__ == "__main__":
    main()

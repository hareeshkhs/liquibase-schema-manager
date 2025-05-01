import re
import sys
import os


def read_version():
    with open("version.py", "r") as file:
        content = file.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    else:
        raise ValueError("Unable to extract version from version.py")


def bump_version(version, part="patch"):
    listitems = version.replace("v", "").split(".")
    major, minor, patch = [None for i in range(3)]
    prerelease = 0
    if len(listitems) == 4:
        major, minor, patch, prerelease = listitems
    else:
        major, minor, patch = listitems
    if part == "major":
        major = int(major) + 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor = int(minor) + 1
        patch = 0
    elif part == "patch":
        if prerelease:
            patch = int(patch.split("-")[0])
        else:
            patch = int(patch) + 1
    elif part == "prerelease":
        if prerelease:
            prerelease = int(prerelease) + 1
        else:
            patch = int(patch) + 1
            patch = str(patch) + "-rc"
        patch = f"{str(patch)}.{str(prerelease)}"
    else:
        raise ValueError(f"Invalid version part: {part}")
    return f"{major}.{minor}.{patch}"


def update_version_py(new_version):
    with open("version.py", "r") as file:
        content = file.read()
    updated_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content,
    )
    with open("version.py", "w") as file:
        file.write(updated_content)


if __name__ == "__main__":
    part = "patch"
    try:
        part = sys.argv[1]
    except IndexError:
        pass  # default to patch

    current_version = read_version()
    print(f"Current version: {current_version}")
    new_version = bump_version(current_version, part)
    print(f"Bumped version: {new_version}")
    update_version_py(new_version)
    os.environ["TAG"] = f"v{new_version}"

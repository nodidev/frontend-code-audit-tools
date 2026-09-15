from pathlib import Path
import re


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# The folder containing this Python script is treated as
# the root of the website.
PROJECT_ROOT = Path(__file__).resolve().parent

# The specific JavaScript file to audit.
# JS_FILE = PROJECT_ROOT / "main.js"
# or below, confirm the directory
# JS_FILE = PROJECT_ROOT / "assets" / "js" / "main.js"


# ---------------------------------------------------------
# Folders to exclude
# ---------------------------------------------------------

EXCLUDED_FOLDERS = {
    "node_modules",
    ".git",
    "dist",
    "build"
}


# ---------------------------------------------------------
# Find all HTML files
# ---------------------------------------------------------

html_files = list(PROJECT_ROOT.rglob("*.html"))

html_files = [
    file for file in html_files
    if not any(
        part in EXCLUDED_FOLDERS
        for part in file.relative_to(PROJECT_ROOT).parts
    )
]


# ---------------------------------------------------------
# Read JavaScript file
# ---------------------------------------------------------

javascript_content = ""

if JS_FILE.is_file():

    try:
        javascript_content = JS_FILE.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except OSError:

        print()
        print("ERROR: Could not read the JavaScript file.")
        print(f"File: {JS_FILE}")
        print()

        raise SystemExit(1)

else:

    print()
    print("ERROR: JavaScript file was not found.")
    print(f"Expected file: {JS_FILE}")
    print()

    raise SystemExit(1)


# ---------------------------------------------------------
# Find JavaScript hooks
# ---------------------------------------------------------

# These patterns look for common ways JavaScript refers
# to elements in HTML.
#
# Examples:
#
# document.getElementById("menuToggle")
# document.getElementById('menuToggle')
#
# document.querySelector("#menuToggle")
# document.querySelector('#menuToggle')
#
# document.querySelectorAll(".menu-item")
# document.querySelectorAll('.menu-item')
#
# document.querySelector("[data-action='delete']")
#
# The script records the hook and its location in main.js.

hook_patterns = [

    # getElementById("example")
    (
        "ID",
        re.compile(
            r'getElementById\s*\(\s*["\']([^"\']+)["\']\s*\)',
            re.IGNORECASE
        )
    ),

    # querySelector("#example")
    # querySelector(".example")
    # querySelector("[data-example]")
    (
        "SELECTOR",
        re.compile(
            r'querySelector\s*\(\s*["\']([^"\']+)["\']\s*\)',
            re.IGNORECASE
        )
    ),

    # querySelectorAll("#example")
    # querySelectorAll(".example")
    # querySelectorAll("[data-example]")
    (
        "SELECTOR",
        re.compile(
            r'querySelectorAll\s*\(\s*["\']([^"\']+)["\']\s*\)',
            re.IGNORECASE
        )
    )
]


# ---------------------------------------------------------
# Extract JavaScript hooks
# ---------------------------------------------------------

js_hooks = []


for hook_type, pattern in hook_patterns:

    for match in pattern.finditer(javascript_content):

        hook = match.group(1).strip()

        if not hook:
            continue

        line_number = (
            javascript_content.count(
                "\n",
                0,
                match.start()
            ) + 1
        )

        js_hooks.append({
            "type": hook_type,
            "hook": hook,
            "line": line_number
        })


# ---------------------------------------------------------
# Remove duplicate JavaScript hooks
# ---------------------------------------------------------

unique_hooks = []
seen_hooks = set()

for item in js_hooks:

    key = (
        item["type"],
        item["hook"]
    )

    if key not in seen_hooks:

        seen_hooks.add(key)
        unique_hooks.append(item)


# ---------------------------------------------------------
# Read all HTML files
# ---------------------------------------------------------

html_content = ""

for html_file in html_files:

    try:

        content = html_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        html_content += "\n" + content

    except OSError:

        continue


# ---------------------------------------------------------
# Check whether JavaScript hooks exist in HTML
# ---------------------------------------------------------

unused_js_hooks = []


for item in unique_hooks:

    hook_type = item["type"]
    hook = item["hook"]

    found_in_html = False

    if hook_type == "ID":

        # Example:
        #
        # JS:
        # document.getElementById("menuToggle")
        #
        # HTML:
        # <button id="menuToggle">

        id_pattern = re.compile(
            rf'\bid\s*=\s*["\']{re.escape(hook)}["\']',
            re.IGNORECASE
        )

        if id_pattern.search(html_content):

            found_in_html = True

    elif hook_type == "SELECTOR":

        # -------------------------------------------------
        # ID selector
        # -------------------------------------------------

        if hook.startswith("#"):

            html_id = hook[1:]

            id_pattern = re.compile(
                rf'\bid\s*=\s*["\']{re.escape(html_id)}["\']',
                re.IGNORECASE
            )

            if id_pattern.search(html_content):

                found_in_html = True

        # -------------------------------------------------
        # Class selector
        # -------------------------------------------------

        elif hook.startswith("."):

            html_class = hook[1:]

            class_pattern = re.compile(
                rf'\bclass\s*=\s*["\'][^"\']*\b'
                rf'{re.escape(html_class)}\b[^"\']*["\']',
                re.IGNORECASE
            )

            if class_pattern.search(html_content):

                found_in_html = True

        # -------------------------------------------------
        # Attribute selector
        # -------------------------------------------------

        elif hook.startswith("["):

            # Extract the attribute name.
            attribute_match = re.match(
                r'\[\s*([a-zA-Z_:][\w:.-]*)',
                hook
            )

            if attribute_match:

                attribute_name = attribute_match.group(1)

                attribute_pattern = re.compile(
                    rf'\b{re.escape(attribute_name)}\s*=',
                    re.IGNORECASE
                )

                if attribute_pattern.search(html_content):

                    found_in_html = True

    # -----------------------------------------------------
    # Report hooks not found in HTML
    # -----------------------------------------------------

    if not found_in_html:

        unused_js_hooks.append(item)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print()

print("=" * 60)
print("POSSIBLY UNUSED JAVASCRIPT HOOKS")
print("=" * 60)

print()

print(f"JS file scanned       : {JS_FILE.relative_to(PROJECT_ROOT)}")
print(f"HTML files scanned    : {len(html_files)}")
print(f"JS hooks found        : {len(unique_hooks)}")
print(
    f"Hooks found in HTML   : "
    f"{len(unique_hooks) - len(unused_js_hooks)}"
)
print(f"Potentially unused    : {len(unused_js_hooks)}")

print()


# ---------------------------------------------------------
# Display unused hooks
# ---------------------------------------------------------

if not unused_js_hooks:

    print("No potentially unused JavaScript hooks were found.")
    print()

else:

    for item in sorted(
        unused_js_hooks,
        key=lambda x: x["line"]
    ):

        print(f"Hook: {item['hook']}")
        print(f"Type: {item['type']}")
        print(f"File: {JS_FILE.relative_to(PROJECT_ROOT)}")
        print(f"Line: {item['line']}")
        print("-" * 60)


# ---------------------------------------------------------
# Important note
# ---------------------------------------------------------

print()

print("NOTE:")

print(
    "These results are only potential unused JavaScript hooks. "
    "The script checks common static JavaScript references "
    "against the HTML files. Dynamic JavaScript references "
    "may not be detected. Review the results before removing "
    "or changing any code."
)

print()

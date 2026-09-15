import re
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

# Folder where this script is located / project root
PROJECT_ROOT = Path(__file__).resolve().parent

# CSS file to check
# CSS_FILE = PROJECT_ROOT / "styles.css"
CSS_FILE = PROJECT_ROOT / "assets" / "css" / "styles.css"

# ---------------------------------------------------------
# FIND CSS CLASS SELECTORS
# ---------------------------------------------------------

def find_css_classes(css_file):
    """
    Find all CSS class selectors in styles.css.

    Example:
        .header { ... }
        .btn-primary { ... }

    Returns:
        {
            "header": line_number,
            "btn-primary": line_number
        }
    """

    css_classes = {}

    try:
        content = css_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = css_file.read_text(encoding="utf-8-sig")

    # Remove CSS comments
    content_without_comments = re.sub(
        r"/\*.*?\*/",
        "",
        content,
        flags=re.DOTALL
    )

    # Find class selectors such as:
    # .container
    # .btn-primary
    # .my_class
    # .col-12
    class_pattern = re.compile(
        r"\.([a-zA-Z_][a-zA-Z0-9_-]*)"
    )

    lines = content_without_comments.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for match in class_pattern.finditer(line):
            class_name = match.group(1)

            if class_name not in css_classes:
                css_classes[class_name] = line_number

    return css_classes


# ---------------------------------------------------------
# FIND CLASSES USED IN HTML FILES
# ---------------------------------------------------------

def find_html_classes(project_root):
    """
    Scan every .html file in the project, including subfolders.

    Looks specifically inside:
        class="..."
        class='...'

    Returns a set containing all classes found in HTML.
    """

    used_classes = set()

    html_files = list(project_root.rglob("*.html"))

    for html_file in html_files:

        try:
            content = html_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            try:
                content = html_file.read_text(
                    encoding="utf-8-sig"
                )
            except Exception:
                print(f"Could not read: {html_file}")
                continue

        # Find:
        # class="container header"
        # class='container header'
        class_attribute_pattern = re.compile(
            r'class\s*=\s*["\']([^"\']*)["\']',
            re.IGNORECASE
        )

        matches = class_attribute_pattern.findall(content)

        for class_value in matches:

            classes = class_value.split()

            for class_name in classes:
                used_classes.add(class_name)

    return used_classes, html_files


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print(" UNUSED CSS CLASS CHECKER")
    print("=" * 60)
    print()

    # Check that styles.css exists
    if not CSS_FILE.exists():
        print(f"ERROR: Could not find:")
        print(f"      {CSS_FILE}")
        print()
        print("Make sure this script is in the same folder")
        print("as styles.css.")
        return

    # Find CSS classes
    css_classes = find_css_classes(CSS_FILE)

    # Find classes used in HTML
    used_classes, html_files = find_html_classes(PROJECT_ROOT)

    # Determine unused classes
    unused_classes = {
        class_name: line_number
        for class_name, line_number in css_classes.items()
        if class_name not in used_classes
    }

    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    print(f"Project folder:")
    print(f"  {PROJECT_ROOT}")
    print()

    print(f"CSS file:")
    print(f"  {CSS_FILE.name}")
    print()

    print(f"HTML files scanned:")
    print(f"  {len(html_files)}")
    print()

    print(f"CSS classes found:")
    print(f"  {len(css_classes)}")
    print()

    print(f"Classes used in HTML:")
    print(f"  {len(used_classes)}")
    print()

    print("-" * 60)
    print("POTENTIALLY UNUSED CSS CLASSES")
    print("-" * 60)

    if not unused_classes:
        print()
        print("No potentially unused CSS classes were found.")
        print()
        return

    # Sort by CSS line number
    sorted_unused = sorted(
        unused_classes.items(),
        key=lambda item: item[1]
    )

    print()

    for class_name, line_number in sorted_unused:
        print(f".{class_name}  ->  styles.css line {line_number}")

    print()
    print("-" * 60)
    print(f"Total potentially unused classes: {len(sorted_unused)}")
    print("-" * 60)

    print()
    print("IMPORTANT:")
    print("These classes are only considered unused if they were")
    print("not found inside an HTML class=\"...\" or class='...'")
    print("attribute.")
    print()
    print("Review the results before deleting anything.")
    print()
    print("This script did NOT modify any files.")


# ---------------------------------------------------------
# RUN SCRIPT
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
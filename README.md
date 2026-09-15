# frontend-code-audit-tools
Python tools for auditing frontend code and identifying potentially unused CSS classes and JavaScript hooks

# How find_unused_javascript_hook.py works
1. Read the js file.
2. Find IDs/selectors being referenced by JavaScript.
3. Read all .html files.
4. Check whether those hooks exist anywhere in the HTML.
5. Report the JS hooks that don't exist in any HTML.
6. Do not modify any files.
7. Give you the JavaScript line number so you can manually inspect it.

# frontend-code-audit-tools
Python tools for auditing frontend code and identifying potentially unused CSS classes and JavaScript hooks

# css (How find_unused_css_classes.py works)
1. Read the css file.
2. Find classes being referenced by css.
3. Read all .html files.
4. Check whether those classes exist anywhere in the HTML.
5. Report the css classes that don't exist in any HTML.
6. Do not modify any files.
7. Give you the css line number so you can manually inspect it.
   
# js (How find_unused_javascript_hook.py works)
1. Read the js file.
2. Find IDs/selectors being referenced by JavaScript.
3. Read all .html files.
4. Check whether those hooks exist anywhere in the HTML.
5. Report the JS hooks that don't exist in any HTML.
6. Do not modify any files.
7. Give you the JavaScript line number so you can manually inspect it.

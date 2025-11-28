import re
import os
import glob

def check_template(filename):
    print(f"Checking {filename}...")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Could not read {filename}: {e}")
        return

    # Regex to find tags
    # We look for if, endif, for, endfor, block, endblock, with, endwith
    tag_re = re.compile(r'{%\s*(if|endif|for|endfor|block|endblock|with|endwith|elif|else)\b.*?%}')
    
    stack = []
    
    lines = content.split('\n')
    
    for match in tag_re.finditer(content):
        tag_full = match.group(0)
        tag_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        # print(f"Found {tag_name} at line {line_num}")
        
        if tag_name in ['if', 'for', 'block', 'with']:
            stack.append((tag_name, line_num))
        elif tag_name in ['elif', 'else']:
            if not stack:
                print(f"Error at line {line_num} in {filename}: Unexpected {tag_name}. Stack is empty.")
                return
            if tag_name == 'elif' and stack[-1][0] != 'if':
                print(f"Error at line {line_num} in {filename}: Unexpected elif. Parent is {stack[-1][0]}")
            if tag_name == 'else' and stack[-1][0] not in ['if', 'for']: # for loops can have else
                print(f"Error at line {line_num} in {filename}: Unexpected else. Parent is {stack[-1][0]}")
                
        elif tag_name == 'endif':
            if not stack or stack[-1][0] != 'if':
                print(f"Error at line {line_num} in {filename}: Unexpected endif. Stack: {stack}")
                return
            stack.pop()
        elif tag_name == 'endfor':
            if not stack or stack[-1][0] != 'for':
                print(f"Error at line {line_num} in {filename}: Unexpected endfor. Stack: {stack}")
                return
            stack.pop()
        elif tag_name == 'endblock':
            if not stack or stack[-1][0] != 'block':
                print(f"Error at line {line_num} in {filename}: Unexpected endblock. Stack: {stack}")
                return
            stack.pop()
        elif tag_name == 'endwith':
            if not stack or stack[-1][0] != 'with':
                print(f"Error at line {line_num} in {filename}: Unexpected endwith. Stack: {stack}")
                return
            stack.pop()

    if stack:
        print(f"Error in {filename}: Unclosed tags at end of file. Stack: {stack}")
    else:
        print(f"OK: {filename}")

# Scan all html files
template_dir = 'd:/antigravity/minor_project/dropoutwatch-app/app/templates'
files = glob.glob(os.path.join(template_dir, '*.html'))

for f in files:
    check_template(f)

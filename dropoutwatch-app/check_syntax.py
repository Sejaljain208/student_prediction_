import re

def check_template(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Regex to find tags
    tag_re = re.compile(r'{%\s*(if|endif|for|endfor|block|endblock)\b.*?%}')
    
    stack = []
    
    for match in tag_re.finditer(content):
        tag = match.group(0)
        tag_name = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        
        if tag_name in ['if', 'for', 'block']:
            stack.append((tag_name, line_num))
        elif tag_name == 'endif':
            if not stack or stack[-1][0] != 'if':
                print(f"Error at line {line_num}: Unexpected endif. Stack: {stack}")
                return
            stack.pop()
        elif tag_name == 'endfor':
            if not stack or stack[-1][0] != 'for':
                print(f"Error at line {line_num}: Unexpected endfor. Stack: {stack}")
                return
            stack.pop()
        elif tag_name == 'endblock':
            if not stack or stack[-1][0] != 'block':
                print(f"Error at line {line_num}: Unexpected endblock. Stack: {stack}")
                return
            stack.pop()

    if stack:
        print(f"Error: Unclosed tags at end of file. Stack: {stack}")
    else:
        print("Template syntax seems correct.")

check_template('d:/antigravity/minor_project/dropoutwatch-app/app/templates/teacher_dashboard.html')

import os

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "testsprite_tests"))

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix double URL
    content = content.replace("http://localhost:3001/http://localhost:3001/", "http://localhost:3001/")

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.startswith("TC") and file.endswith(".py"):
            fix_file(os.path.join(root, file))

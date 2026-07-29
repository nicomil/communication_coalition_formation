import os

directories = [
    'bargaining_tdl_common',
    'bargaining_tdl_intro',
    'bargaining_tdl_survey',
    'bargaining_tdl_main'
]

for d in directories:
    if not os.path.exists(d): continue
    for filename in os.listdir(d):
        if filename.endswith('.html'):
            filepath = os.path.join(d, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            style_block = "<style>\n    .otree-body {\n        max-width: 1000px;\n    }\n</style>"
            if "{{ block content }}" in content and style_block not in content:
                content = content.replace("{{ block content }}", "{{ block content }}\n\n" + style_block)
                
            content = content.replace('<div class="card bg-light m-3">', '<div class="card bg-white mt-4 mb-4 shadow-sm">')
            content = content.replace('<div class="card bg-light m-5">', '<div class="card bg-white mt-4 mb-4 shadow-sm">')
            
            # For specific files that just use <div class="card"> followed immediately by <div class="card-body">
            if '<div class="card">\n    <div class="card-body">' in content:
                content = content.replace('<div class="card">\n    <div class="card-body">', '<div class="card bg-white mt-4 mb-4 shadow-sm">\n    <div class="card-body px-5 py-4">')
            
            content = content.replace('<div class="card-body">', '<div class="card-body px-5 py-4">')
            
            if original_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {filepath}')

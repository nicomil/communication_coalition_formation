import os

directory = 'bargaining_tdl_survey'
pages = [f'SurveyPage{i}.html' for i in range(4, 10)]

for filename in pages:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_button = '<div class="d-flex justify-content-center mt-4 mb-4">\n    {{ next_button }}\n</div>'
        if old_button in content:
            content = content.replace(old_button, '{{ next_button }}')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Reverted button in {filepath}')

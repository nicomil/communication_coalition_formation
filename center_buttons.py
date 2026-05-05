import os

directory = 'bargaining_tdl_survey'
pages = [f'SurveyPage{i}.html' for i in range(4, 10)]

for filename in pages:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{{ next_button }}' in content:
            new_button = '<div class="d-flex justify-content-center mt-4 mb-4">\n    {{ next_button }}\n</div>'
            content = content.replace('{{ next_button }}', new_button)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Centered button in {filepath}')

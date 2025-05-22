import os
import re

TEX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'ru'))
TEXT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'txt'))

os.makedirs(TEXT_DIR, exist_ok=True)

for filename in os.listdir(TEX_DIR):
    if filename.endswith('.tex'):
        tex_path = os.path.join(TEX_DIR, filename)
        with open(tex_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Извлекаем текст между \begin{document} и \end{document}
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
        if match:
            extracted_text = match.group(1).strip()
            text_filename = os.path.splitext(filename)[0] + '.txt'
            text_path = os.path.join(TEXT_DIR, text_filename)
            with open(text_path, 'w', encoding='utf-8') as out_f:
                out_f.write(extracted_text)

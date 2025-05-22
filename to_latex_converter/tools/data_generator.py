import re
import random
import string
from tqdm import tqdm
import jieba
import os

# Function to remove non-English characters from a text file
# Input:
#   input_file_path (str): Path to the input text file
#   output_file_path (str): Path to save the cleaned text file
# Output:
#   None (writes the cleaned content to output_file_path)
def remove_non_english_characters(input_file_path, output_file_path):
    # Keep only Russian characters (Cyrillic), spaces, and basic punctuation
    russian_regex = re.compile(r'[^а-яА-ЯёЁ\s.,?!\'"()]+')
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    cleaned_content = russian_regex.sub('', content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

# Function to extract LaTeX formulas from a .tex file
# Input:
#   tex_file_path (str): Path to the LaTeX (.tex) file
# Output:
#   formula_list (list): List of extracted LaTeX formulas
def extract_latex_formulas(tex_file_path):
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        tex_content = f.read()
    pattern = r'\\\[(.+?)\\\]|\\begin\{align\*\}(.+?)\\end\{align\*\}'
    formulas = re.findall(pattern, tex_content)
    formula_list = [
        re.sub(r'\\eqref\{(.*?)\}', r'', group).strip()
        for tuples in formulas for group in tuples if group
    ]
    # Улучшенная фильтрация: удаляем формулы, которые содержат только спецсимволы, пробелы или пустые
    bad_formulas = {'\\end{align*}', '\\begin{align*}', '', '\\[', '\\]'}
    def is_bad_formula(f):
        f_clean = f.replace('\n', '').replace('\r', '').replace(' ', '')
        return f_clean in {s.replace(' ', '') for s in bad_formulas} or re.fullmatch(r'\\end\{.*?\}|\\begin\{.*?\}', f_clean)
    formula_list = [f for f in formula_list if f and not is_bad_formula(f)]
    return formula_list

# Function to process text by inserting LaTeX formulas randomly
# Input:
#   input_file (str): Path to the input text file
#   output_file (str): Path to save the processed text file
#   formulas (list): List of LaTeX formulas to insert
# Output:
#   None (writes the processed content to output_file)
def process_text(input_file, output_file, formulas):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('\n', '')
    sentences = re.split(r'[.,]', text)
    output = ''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            for char in sentence:
                output += char
                if random.random() < 0.02:
                    formula = random.sample(formulas, 1)[0]
                    if len(formula) < 50:
                        try:
                            output += ' \\(' + re.sub(r'\\tag\{.*?\}', '', formula) + '\\) '
                        except:
                            print(formula)
            if 30 < len(output) < 300:
                f.write(output + '.\n')
                output = ''
            if len(output) > 300:
                output = ''

# Function to remove unwanted symbols from text
# Input:
#   text (str): The input text string
# Output:
#   cleaned_text (str): The text after removing unwanted symbols
def remove_symbols(text):
    pattern = re.compile(r'[^а-яА-ЯёЁ，。！？、： ；"''\'"()\[\]\{\}\<\>\.\,\?\!\:\;\-\s]')
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

# Function to remove empty brackets
# Input:
#   text (str): The input text string
# Output:
#   cleaned_text (str): The text after removing empty brackets
def remove_empty_brackets(text):
    # Удаляет (), {}, [], （）, и скобки с пробелами внутри
    patterns = [
        r'\(\s*\)', r'\{\s*\}', r'\[\s*\]', r'（\s*）', r'«\s*»', r'“\s*”', r'„\s*“'
    ]
    for pat in patterns:
        text = re.sub(pat, '', text)
    return text

# Function to format words with LaTeX commands and randomly insert formulas and numbers
# Input:
#   words (list): List of words to format
#   formulas (list): List of LaTeX formulas to insert
#   lines (list): List of lines from the original text for random insertion
# Output:
#   output (str): The formatted LaTeX string
def format_text_with_latex(words, formulas, lines):
    output = ''
    count = 0
    # Объединяем слова в предложения
    sentences = []
    current_sentence = ''
    for word in words:
        current_sentence += word
        if word in '.,!?':
            sentences.append(current_sentence.strip())
            current_sentence = ''
    # Добавляем последнее предложение, если оно есть
    if current_sentence:
        sentences.append(current_sentence.strip())
    for sentence in tqdm(sentences):
        count += 1
        words_in_sentence = sentence.split()
        formula_inserted = False
        if len(words_in_sentence) > 1 and random.random() < 0.9:
            insert_pos = random.randint(1, len(words_in_sentence)-1)
            for i, word in enumerate(words_in_sentence):
                output += word + ' '
                if i == insert_pos and not formula_inserted:
                    if random.random() < 0.2:
                        formula = random.sample(formulas, 1)[0]
                        if len(formula) > 30 and formula.strip() and '\\' in formula:
                            output += '\n \\begin{align*} \n' + formula + '\n \\end{align*} \n'
                            formula_inserted = True
                    else:
                        formula = random.sample(formulas, 1)[0]
                        if len(formula) < 30 and formula.strip() and '\\' not in formula:
                            output += ' \\( ' + re.sub(r'\\tag\{.*?\}', '', formula) + ' \\) '
                            formula_inserted = True
        else:
            output += sentence + ' '
        if count % 10 == 0:  # Каждые 10 предложений
            output += '\n \\newpage \n'
        if random.random() < 0.0005:
            line = random.sample(lines, 1)[0].replace('\n', '')
            if random.random() < 0.5:
                output += ' \\textbf{' + line + '} '
            else:
                output += ' \\textit{' + line + '} '
    return output

# Function to write LaTeX formatted strings into separate .tex files
# Input:
#   strings (str): The LaTeX formatted string to write
#   group_size (int, optional): Number of characters per file.
#   folder_name (str, optional): Name of the folder to save .tex files.
# Output:
#   None (writes multiple .tex files into the specified folder)
def write_strings_to_files(strings, group_size, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    # Разбиваем по строкам, чтобы не рвать формулы и предложения
    lines = strings.split('\n')
    current_group = []
    file_idx = 1

    for line in lines:
        current_group.append(line)
        # Если набралось group_size строк или это последняя строка — пишем файл
        if len(current_group) >= group_size:
            file_name = f"{folder_name}/{file_idx}.tex"
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(
                    '\\documentclass[preview]{standalone}\n'
                    '\\usepackage[utf8]{inputenc}\n'
                    '\\usepackage[russian]{babel}\n'
                    '\\usepackage{amssymb}\n'
                    '\\usepackage{amsmath}\n'
                    '\\usepackage{stmaryrd}\n'
                    '\\begin{document}\n'
                )
                file.write('\n'.join(current_group))
                file.write('\n\\end{document}\n')
            file_idx += 1
            current_group = []
    # Записываем остаток, если есть
    if current_group:
        file_name = f"{folder_name}/{file_idx}.tex"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(
                '\\documentclass[preview]{standalone}\n'
                '\\usepackage[utf8]{inputenc}\n'
                '\\usepackage[russian]{babel}\n'
                '\\usepackage{amssymb}\n'
                '\\usepackage{amsmath}\n'
                '\\usepackage{stmaryrd}\n'
                '\\begin{document}\n'
            )
            file.write('\n'.join(current_group))
            file.write('\n\\end{document}\n')

# Main function to connect all steps
# Input:
#   input_text_file (str): Path to the input text file
#   input_tex_file (str): Path to the input LaTeX (.tex) file containing formulas
#   output_folder (str): Folder name to save the output .tex files
# Output:
#   None (executes the entire processing pipeline and writes output files)
def main(input_text_file, input_tex_file, output_folder):
    # Step 1: Clean the input text file by removing non-English characters
    cleaned_text_file = 'en_only.txt'
    remove_non_english_characters(input_text_file, cleaned_text_file)

    # Step 2: Extract LaTeX formulas from the input LaTeX file
    formulas = extract_latex_formulas(input_tex_file)

    # Step 3: Process the cleaned text and insert LaTeX formulas randomly
    processed_text_file = 'en_line.txt'
    process_text(cleaned_text_file, processed_text_file, formulas)

    # Step 4: Read in the processed text and further format it with LaTeX commands
    with open(processed_text_file, 'r', encoding='utf-8') as f:
        txt_content = f.read()
    with open(cleaned_text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    txt_content = remove_symbols(txt_content)
    txt_content = remove_empty_brackets(txt_content)
    words = jieba.lcut(txt_content)
    latex_content = format_text_with_latex(words, formulas, lines)

    # Step 5: Write the formatted LaTeX strings into .tex files in the specified folder
    blocks = split_latex_blocks(latex_content)
    write_blocks_to_files(blocks, group_size=3, folder_name=output_folder)

def split_latex_blocks(text):
    # Находим все формульные и текстовые блоки
    pattern = re.compile(
        r'(\\begin\{[a-zA-Z*]+\}.*?\\end\{[a-zA-Z*]+\}|\\\[.*?\\\]|\\\(.*?\\\)|\$\$.*?\$\$|\$.*?\$)',
        re.DOTALL
    )
    blocks = []
    last_end = 0
    for m in pattern.finditer(text):
        # Добавляем текст между формулами как отдельный блок
        if m.start() > last_end:
            blocks.append(text[last_end:m.start()])
        blocks.append(m.group())
        last_end = m.end()
    # Добавляем остаток текста
    if last_end < len(text):
        blocks.append(text[last_end:])
    # Убираем пустые блоки
    return [b for b in blocks if b.strip()]

def fix_unclosed_environments(tex_content):
    # Список окружений, которые нужно проверять
    envs = ['align\\*', 'align', 'array', 'gather\\*', 'gather', 'equation\\*', 'equation']
    for env in envs:
        open_count = len(re.findall(r'\\begin\{' + env + r'\}', tex_content))
        close_count = len(re.findall(r'\\end\{' + env + r'\}', tex_content))
        if open_count > close_count:
            tex_content += '\n' + ('\\end{' + env + '}\n') * (open_count - close_count)
    return tex_content

def check_braces_balance(s):
    stack = []
    i = 0
    while i < len(s):
        if s[i] == '\\':
            # Пропускаем команды LaTeX
            i += 1
            while i < len(s) and s[i].isalpha():
                i += 1
            continue
        elif s[i] == '{':
            stack.append(i)
        elif s[i] == '}':
            if not stack:
                return False  # Лишняя закрывающая скобка
            stack.pop()
        i += 1
    return len(stack) == 0  # True если все скобки закрыты

def check_parentheses_balance(s):
    stack = []
    i = 0
    while i < len(s):
        if s[i] == '\\':
            # Пропускаем команды LaTeX
            i += 1
            while i < len(s) and s[i].isalpha():
                i += 1
            continue
        elif s[i] == '(':
            stack.append(i)
        elif s[i] == ')':
            if not stack:
                return False  # Лишняя закрывающая скобка
            stack.pop()
        i += 1
    return len(stack) == 0  # True если все скобки закрыты

def check_latex_commands_and_braces(s):
    # Проверяем, что все команды LaTeX имеют корректные аргументы
    i = 0
    while i < len(s):
        if s[i] == '\\':
            # Находим конец команды
            cmd_end = i + 1
            while cmd_end < len(s) and s[cmd_end].isalpha():
                cmd_end += 1
            cmd = s[i:cmd_end]
            
            # Проверяем, что после команды идет открывающая скобка
            if cmd_end < len(s) and s[cmd_end] == '{':
                # Ищем закрывающую скобку
                brace_count = 1
                j = cmd_end + 1
                while j < len(s) and brace_count > 0:
                    if s[j] == '{':
                        brace_count += 1
                    elif s[j] == '}':
                        brace_count -= 1
                    j += 1
                if brace_count > 0:
                    return False  # Незакрытая скобка в аргументе команды
            i = cmd_end
        else:
            i += 1
    return True

def check_latex_math_commands(s):
    # Проверяем корректность математических команд
    math_commands = [
        r'\\mathbb\{[a-zA-Z]\}',  # \mathbb{R}
        r'\\mathcal\{[a-zA-Z]\}',  # \mathcal{R}
        r'\\mathfrak\{[a-zA-Z]\}',  # \mathfrak{R}
        r'\\mathrm\{[a-zA-Z]\}',  # \mathrm{R}
        r'\\mathbf\{[a-zA-Z]\}',  # \mathbf{R}
        r'\\mathit\{[a-zA-Z]\}',  # \mathit{R}
        r'\\mathsf\{[a-zA-Z]\}',  # \mathsf{R}
        r'\\mathtt\{[a-zA-Z]\}',  # \mathtt{R}
        r'\\mathnormal\{[a-zA-Z]\}',  # \mathnormal{R}
        r'\\mathscr\{[a-zA-Z]\}',  # \mathscr{R}
        r'\\text\{[^}]*\}',  # \text{...}
        r'\\operatorname\{[^}]*\}',  # \operatorname{...}
        r'\\lim', r'\\sum', r'\\prod', r'\\int',  # операторы
        r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln',  # функции
        r'\\alpha', r'\\beta', r'\\gamma', r'\\delta',  # греческие буквы
        r'\\infty', r'\\partial', r'\\nabla',  # специальные символы
        r'\\left', r'\\right',  # скобки
        r'\\frac\{[^}]*\}\{[^}]*\}',  # дроби
        r'\\sqrt\{[^}]*\}',  # корни
        r'\\overline\{[^}]*\}', r'\\underline\{[^}]*\}',  # черты
        r'\\hat\{[^}]*\}', r'\\bar\{[^}]*\}', r'\\vec\{[^}]*\}',  # акценты
        r'\\dot\{[^}]*\}', r'\\ddot\{[^}]*\}',  # точки
        r'\\prime', r'\\backprime',  # штрихи
        r'\\langle', r'\\rangle',  # угловые скобки
        r'\\lceil', r'\\rceil', r'\\lfloor', r'\\rfloor',  # потолок и пол
        r'\\|', r'\\|',  # двойные вертикальные линии
        r'\\ldots', r'\\cdots', r'\\vdots', r'\\ddots',  # многоточия
        r'\\boxed\{[^}]*\}',  # рамка
        r'\\tag\{[^}]*\}',  # теги
        r'\\label\{[^}]*\}',  # метки
        r'\\ref\{[^}]*\}',  # ссылки
        r'\\eqref\{[^}]*\}'  # ссылки на уравнения
    ]
    
    # Проверяем, что все команды в тексте являются корректными
    for cmd in math_commands:
        if re.search(cmd, s):
            return True
            
    # Если нет ни одной корректной команды, но есть математические символы
    if re.search(r'[\\^_{}]', s):
        return False
        
    return True

def check_latex_math_delimiters(s):
    # Проверяем баланс \( и \)
    inline_math_open = len(re.findall(r'\\\(', s))
    inline_math_close = len(re.findall(r'\\\)', s))
    if inline_math_open != inline_math_close:
        return False
        
    # Проверяем баланс \[ и \]
    display_math_open = len(re.findall(r'\\\[', s))
    display_math_close = len(re.findall(r'\\\]', s))
    if display_math_open != display_math_close:
        return False
        
    # Проверяем, что нет одиночных \( или \)
    if re.search(r'\\\([^\)]*$', s) or re.search(r'^[^\(]*\\\)', s):
        return False
        
    # Проверяем, что нет одиночных \[ или \]
    if re.search(r'\\\[[^\]]*$', s) or re.search(r'^[^\[]*\\\]', s):
        return False
        
    # Проверяем корректность математических команд
    if not check_latex_math_commands(s):
        return False
        
    return True

def write_blocks_to_files(blocks, group_size, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    file_idx = 1
    for i in range(0, len(blocks), group_size):
        content = '\n'.join(blocks[i:i+group_size])
        content = fix_unclosed_environments(content)
        if not check_braces_balance(content) or not check_parentheses_balance(content) or not check_latex_math_delimiters(content):
            print(f"Skip file {file_idx}.tex: unbalanced braces, parentheses, math delimiters or invalid LaTeX commands")
            continue
        file_name = f"{folder_name}/{file_idx}.tex"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(
                '\\documentclass[preview]{standalone}\n'
                '\\usepackage[utf8]{inputenc}\n'
                '\\usepackage[T2A]{fontenc}\n'
                '\\usepackage[russian]{babel}\n'
                '\\usepackage{amssymb}\n'
                '\\usepackage{amsmath}\n'
                '\\usepackage{stmaryrd}\n'
                '\\begin{document}\n'
            )
            file.write(content)
            file.write('\n\\end{document}\n')
        file_idx += 1

# Example usage
if __name__ == "__main__":
    main('to_latex_converter/tools/test.text', 'to_latex_converter/tools/formular.tex', 'data/raw/ru')


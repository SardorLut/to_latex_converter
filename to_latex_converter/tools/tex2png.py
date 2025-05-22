import os
import subprocess

def tex_to_png(tex_dir):
    for filename in os.listdir(tex_dir):
        if filename.endswith('.tex'):
            tex_path = os.path.join(tex_dir, filename)
            base = os.path.splitext(tex_path)[0]
            pdf_path = base + '.pdf'
            png_path = base + '.png'
            # 1. Компиляция в PDF
            try:
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', tex_dir,
                    tex_path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                if result.returncode != 0 or not os.path.exists(pdf_path):
                    # Ошибка — удаляем .tex и мусор
                    for ext in ['.tex', '.pdf', '.aux', '.log']:
                        f = base + ext
                        if os.path.exists(f):
                            os.remove(f)
                    print(f"[ERROR] {filename} — удалён из-за ошибки компиляции.")
                    continue
            except Exception as e:
                # Любая ошибка — удаляем .tex и мусор
                for ext in ['.tex', '.pdf', '.aux', '.log']:
                    f = base + ext
                    if os.path.exists(f):
                        os.remove(f)
                print(f"[EXCEPTION] {filename} — удалён из-за исключения: {e}")
                continue
            # 2. Конвертация PDF в PNG
            try:
                subprocess.run([
                    'convert',
                    '-density', '300',
                    pdf_path,
                    png_path
                ], check=True)
                print(f"[OK] {filename} -> {os.path.basename(png_path)}")
            except Exception as e:
                print(f"[CONVERT ERROR] {filename}: {e}")
            # 3. (Опционально) удаляем PDF и мусор
            for ext in ['.pdf', '.aux', '.log']:
                f = base + ext
                if os.path.exists(f):
                    os.remove(f)

def main():
    tex_to_png('data/raw/ru')

if __name__ == '__main__':
    main() 
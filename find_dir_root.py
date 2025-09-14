import os
import glob

def find_dir_root():
    files = glob.glob('./**/*.py', recursive=True)
    found = False
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if 'DIR_ROOT =' in line:
                        print(f'{file}:{line_num}: {line.strip()}')
                        found = True
        except Exception as e:
            # Skip files that can't be read
            pass
    if not found:
        print('DIR_ROOT not found in any Python files')

if __name__ == "__main__":
    find_dir_root()
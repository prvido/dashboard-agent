import os
from pathspec import PathSpec

def load_gitignore(root_path):
    gitignore_path = os.path.join(root_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            patterns = f.read().splitlines()
        return PathSpec.from_lines('gitwildmatch', patterns)
    return None

def print_tree(start_path='.', prefix='', spec=None, base_path=''):
    items = sorted(os.listdir(start_path))
    for index, name in enumerate(items):
        path = os.path.join(start_path, name)
        relative_path = os.path.relpath(path, base_path)

        # Skip ignored files/folders
        if spec and spec.match_file(relative_path):
            continue

        is_last = index == len(items) - 1
        connector = '└── ' if is_last else '├── '

        print(prefix + connector + name)

        if os.path.isdir(path):
            extension = '    ' if is_last else '│   '
            print_tree(path, prefix + extension, spec=spec, base_path=base_path)

if __name__ == '__main__':
    # Target the parent directory (assuming script is inside /scripts)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ignore_spec = load_gitignore(project_root)

    print(f"Estrutura de diretórios em: {project_root}\n")
    print_tree(project_root, spec=ignore_spec, base_path=project_root)

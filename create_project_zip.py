import os
import zipfile
from pathlib import Path

def create_zip():
    base_dir = Path(__file__).resolve().parent
    zip_path = base_dir / "django_rag_project.zip"
    backend_dir = base_dir / "backend"

    print(f"Creating ZIP archive at: {zip_path}")

    # Exclude patterns
    excluded_dirs = {'__pycache__', '.git', '.pytest_cache', 'node_modules', 'staticfiles'}
    excluded_extensions = {'.pyc', '.pyo', '.pyd', '.log'}

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add root README and batch files
        for root_file in ['README.md', 'run_server.bat', 'setup_env.bat']:
            fpath = base_dir / root_file
            if fpath.exists():
                zipf.write(fpath, arcname=f"django_rag_project/{root_file}")
                print(f"Added: {root_file}")

        # Walk through backend
        for root, dirs, files in os.walk(backend_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
            
            # Skip venv directory inside zip to keep it lightweight (user runs setup_env.bat)
            if 'venv' in Path(root).parts:
                continue

            for file in files:
                if any(file.endswith(ext) for ext in excluded_extensions):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(base_dir)
                archive_name = f"django_rag_project/{rel_path.as_posix()}"
                zipf.write(file_path, arcname=archive_name)

    print(f"[SUCCESS] Archive created: {zip_path} ({os.path.getsize(zip_path) / 1024 / 1024:.2f} MB)")

if __name__ == '__main__':
    create_zip()

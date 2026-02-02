import os
import ast
from pathlib import Path

PROJECT_ROOT = Path("c:/Users/saumy/OneDrive/Desktop/job/job-agent-production")
IGNORE_DIRS = {"venv", "__pycache__", "node_modules", "archive", "frontend"}

def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        from_imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module]
        
        return {
            "functions": functions,
            "classes": classes,
            "loc": len(content.splitlines()),
            "dependencies": imports + from_imports
        }
    except Exception as e:
        return {"error": str(e)}

def audit_directory(root_dir):
    report = {}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                rel_path = path.relative_to(PROJECT_ROOT).as_posix()
                report[rel_path] = analyze_file(path)
    return report

if __name__ == "__main__":
    results = audit_directory(PROJECT_ROOT)
    
    total_files = len(results)
    total_loc = sum(r.get("loc", 0) for r in results.values() if "loc" in r)
    total_funcs = sum(len(r.get("functions", [])) for r in results.values() if "functions" in r)
    
    print(f"=== CYNO CODEBASE AUDIT ===")
    print(f"Total Files: {total_files}")
    print(f"Total Lines of Code: {total_loc}")
    print(f"Total Functions: {total_funcs}")
    print("-" * 30)
    
    for file, data in sorted(results.items()):
        if "error" in data:
            print(f"❌ {file}: {data['error']}")
        else:
            funcs = len(data['functions'])
            classes = len(data['classes'])
            print(f"📄 {file} | LOC: {data['loc']} | Funcs: {funcs} | Classes: {classes}")
            # print(f"    - Funcs: {', '.join(data['functions'][:5])}...")

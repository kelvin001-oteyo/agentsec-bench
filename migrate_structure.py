import os
import re
import subprocess

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(REPO_ROOT, "agentsec_bench")

STRUCTURE = {
    "core": [
        "types", "scenario", "agent", "evaluator",
        "environment", "environment_inbox", "environment_crm",
    ],
    "tools": [
        "tools_expense", "tools_refund", "tools_inbox", "tools_crm",
        "tools_admin", "tools_devops", "tools_workspace", "tools_vendor",
        "tools_reporting",
    ],
    "scenarios": [
        "scenarios_expense", "scenarios_ambiguous", "scenarios_injection",
        "scenarios_exfiltration", "scenarios_privilege", "scenarios_code_execution",
        "scenarios_rogue", "scenarios_memory_poisoning", "scenarios_trust_exploitation",
    ],
    "agents": [
        "fake_agent", "good_agent", "refund_agents", "inbox_agents",
        "crm_agents", "admin_agents", "devops_agents", "workspace_agents",
        "vendor_agents", "reporting_agents",
    ],
}

MODULE_TO_SUBPKG = {}
for subpkg, modules in STRUCTURE.items():
    for m in modules:
        MODULE_TO_SUBPKG[m] = subpkg


def git(*args):
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ! git {' '.join(args)} failed: {result.stderr.strip()}")
        return False
    return True


def move_files():
    for subpkg, modules in STRUCTURE.items():
        subpkg_dir = os.path.join(PKG_DIR, subpkg)
        os.makedirs(subpkg_dir, exist_ok=True)
        init_path = os.path.join(subpkg_dir, "__init__.py")
        if not os.path.exists(init_path):
            open(init_path, "w").close()
            git("add", os.path.relpath(init_path, REPO_ROOT))

        for m in modules:
            src = os.path.join(PKG_DIR, f"{m}.py")
            dst = os.path.join(subpkg_dir, f"{m}.py")
            if os.path.exists(src):
                rel_src = os.path.relpath(src, REPO_ROOT)
                rel_dst = os.path.relpath(dst, REPO_ROOT)
                print(f"  moving {rel_src} -> {rel_dst}")
                if not git("mv", rel_src, rel_dst):
                    os.rename(src, dst)
            elif os.path.exists(dst):
                print(f"  already moved: {m}.py")
            else:
                print(f"  ! not found, skipping: {m}.py")


REL_IMPORT_RE = re.compile(r'^(\s*from\s+)\.([A-Za-z_][A-Za-z0-9_]*)(\s+import\s+.+)$')
ABS_IMPORT_RE = re.compile(r'^(\s*from\s+)agentsec_bench\.([A-Za-z_][A-Za-z0-9_]*)(\s+import\s+.+)$')


def file_subpkg(py_path):
    rel = os.path.relpath(py_path, PKG_DIR)
    parts = rel.split(os.sep)
    if len(parts) >= 2 and parts[0] in STRUCTURE:
        return parts[0]
    return None


def rewrite_imports_in_file(py_path):
    with open(py_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    this_subpkg = file_subpkg(py_path)
    changed = False
    new_lines = []

    for line in lines:
        m = REL_IMPORT_RE.match(line)
        if m and this_subpkg is not None:
            prefix, modname, rest = m.groups()
            target_subpkg = MODULE_TO_SUBPKG.get(modname)
            if target_subpkg is None:
                new_lines.append(line)
                continue
            if target_subpkg == this_subpkg:
                new_line = f"{prefix}.{modname}{rest}\n"
            else:
                new_line = f"{prefix}..{target_subpkg}.{modname}{rest}\n"
            if new_line.strip() != line.strip():
                changed = True
            new_lines.append(new_line)
            continue

        m2 = ABS_IMPORT_RE.match(line)
        if m2:
            prefix, modname, rest = m2.groups()
            target_subpkg = MODULE_TO_SUBPKG.get(modname)
            if target_subpkg is None:
                new_lines.append(line)
                continue
            new_line = f"{prefix}agentsec_bench.{target_subpkg}.{modname}{rest}\n"
            if new_line.strip() != line.strip():
                changed = True
            new_lines.append(new_line)
            continue

        new_lines.append(line)

    if changed:
        with open(py_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"  rewrote imports in {os.path.relpath(py_path, REPO_ROOT)}")


def rewrite_all():
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in (".venv", ".git", "__pycache__")]
        for fname in files:
            if fname.endswith(".py"):
                rewrite_imports_in_file(os.path.join(root, fname))


def main():
    print("Step 1: moving files into subpackages...")
    move_files()
    print("\nStep 2: rewriting import statements...")
    rewrite_all()
    print("\nDone. Now run: uv run pytest -v")


if __name__ == "__main__":
    main()
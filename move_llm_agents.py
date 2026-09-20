"""
Moves agentsec_bench/llm_agent.py and agentsec_bench/llm_agent_anthropic.py
into agentsec_bench/agents/, and rewrites imports accordingly.

Run from the agentsec-bench repo root:
    python move_llm_agents.py

Stdlib only, no uv/deps needed. Uses `git mv` (falls back to os.rename).
"""
import os
import re
import subprocess

REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
PKG_ROOT = os.path.join(REPO_ROOT, "agentsec_bench")

FILES_TO_MOVE = ["llm_agent.py", "llm_agent_anthropic.py"]
TARGET_SUBPKG = "agents"

MODULE_TO_SUBPKG = {
    "types": "core", "scenario": "core", "agent": "core", "evaluator": "core",
    "environment": "core", "environment_inbox": "core", "environment_crm": "core",
    "tools_expense": "tools", "tools_refund": "tools", "tools_inbox": "tools",
    "tools_crm": "tools", "tools_admin": "tools", "tools_devops": "tools",
    "tools_workspace": "tools", "tools_vendor": "tools", "tools_reporting": "tools",
    "scenarios_expense": "scenarios", "scenarios_ambiguous": "scenarios",
    "scenarios_injection": "scenarios", "scenarios_exfiltration": "scenarios",
    "scenarios_privilege": "scenarios", "scenarios_code_execution": "scenarios",
    "scenarios_rogue": "scenarios", "scenarios_memory_poisoning": "scenarios",
    "scenarios_trust_exploitation": "scenarios",
    "fake_agent": "agents", "good_agent": "agents", "refund_agents": "agents",
    "inbox_agents": "agents", "crm_agents": "agents", "admin_agents": "agents",
    "devops_agents": "agents", "workspace_agents": "agents",
    "vendor_agents": "agents", "reporting_agents": "agents",
    "llm_agent": "agents", "llm_agent_anthropic": "agents",
}

REL_IMPORT_RE = re.compile(r'^(\s*from\s+)\.([A-Za-z_][A-Za-z0-9_]*)(\s+import\s+.+)$')
ABS_IMPORT_RE = re.compile(r'^(\s*from\s+)agentsec_bench\.([A-Za-z_][A-Za-z0-9_]*)(\s+import\s+.+)$')


def git_mv(src, dst):
    try:
        subprocess.run(["git", "mv", src, dst], check=True, cwd=REPO_ROOT)
    except Exception:
        os.rename(src, dst)


def rewrite_moved_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    changed = False
    for i, line in enumerate(lines):
        m = REL_IMPORT_RE.match(line)
        if m:
            prefix, modname, suffix = m.groups()
            target_subpkg = MODULE_TO_SUBPKG.get(modname)
            if target_subpkg is None:
                continue
            if target_subpkg == TARGET_SUBPKG:
                lines[i] = f"{prefix}.{modname}{suffix}\n"
            else:
                lines[i] = f"{prefix}..{target_subpkg}.{modname}{suffix}\n"
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"  rewrote relative imports in {os.path.relpath(path, REPO_ROOT)}")


def rewrite_absolute_refs():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".venv", ".git", "__pycache__")]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            changed = False
            for i, line in enumerate(lines):
                m = ABS_IMPORT_RE.match(line)
                if m:
                    prefix, modname, suffix = m.groups()
                    if modname in ("llm_agent", "llm_agent_anthropic"):
                        lines[i] = f"{prefix}agentsec_bench.agents.{modname}{suffix}\n"
                        changed = True
            if changed:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                print(f"  rewrote absolute imports in {os.path.relpath(fpath, REPO_ROOT)}")


def main():
    print("Moving files into agentsec_bench/agents/ ...")
    for fname in FILES_TO_MOVE:
        src = os.path.join(PKG_ROOT, fname)
        dst = os.path.join(PKG_ROOT, TARGET_SUBPKG, fname)
        if not os.path.exists(src):
            print(f"  SKIP: {src} not found (already moved?)")
            continue
        git_mv(src, dst)
        print(f"  moved {fname} -> agentsec_bench/{TARGET_SUBPKG}/{fname}")
        rewrite_moved_file(dst)

    print("\nRewriting absolute references across the repo ...")
    rewrite_absolute_refs()

    print("\nDone. Now:")
    print("  1. uv sync")
    print("  2. uv run pytest -v")
    print("  3. uv run python check_scenarios.py")
    print("  4. uv run python run_test.py")
    print("  5. findstr /s /n \"agentsec_bench.llm_agent\" *.py   (should show nothing outside agents/)")


if __name__ == "__main__":
    main()
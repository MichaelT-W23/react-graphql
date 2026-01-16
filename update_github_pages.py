import os
import subprocess
import sys
import time
import uuid
import shutil
import atexit
from termcolor import colored as c

# ====== CONFIG ======
VERSION = "1.0.0"
CNAME_DOMAIN = "react.bookql.com"

# Base names (actual paths become unique per run)
BUILD_TREE_BASE = "~/.build-temp-react"
DEPLOY_TREE_BASE = "~/.gh-pages-temp-react"

DEBUG = False
# ====================


def abspath(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))


def sh(cmd: str, critical: bool = False, quiet: bool = True):
    """
    Shell runner:
    - quiet=True: suppress stdout/stderr
    - quiet=False: show command + stream output
    """
    if DEBUG:
        quiet = False

    if not quiet:
        print(c(f"> {cmd}", "cyan"))
        code = os.system(cmd)
    else:
        code = os.system(f"{cmd} > /dev/null 2>&1")

    if critical and code != 0:
        print(c(f"❌ Failed: {cmd}", "red"))
        if quiet:
            print(c("↳ Showing command output:", "yellow"))
            os.system(cmd)
        sys.exit(1)


def run_capture(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def get_branch() -> str:
    return run_capture("git branch --show-current").stdout.strip()


def repo_root() -> str:
    return run_capture("git rev-parse --show-toplevel").stdout.strip()


def assert_outside_repo(repo: str, candidate: str, label: str):
    repo = abspath(repo)
    candidate = abspath(candidate)

    if candidate == repo or candidate.startswith(repo + os.sep):
        print(c(f"❌ {label} must be OUTSIDE the repo.", "red"))
        print(c(f"   Repo:     {repo}", "red"))
        print(c(f"   {label}: {candidate}", "red"))
        sys.exit(1)


def ensure(path: str, label: str):
    if not os.path.exists(path):
        print(c(f"❌ Missing {label}: {path}", "red"))
        sys.exit(1)


def rm_rf(path: str):
    """
    Aggressive, cross-platform-ish delete with verification.
    Uses shutil.rmtree to avoid shell weirdness; falls back to rm -rf if needed.
    """
    path = abspath(path)

    if not os.path.exists(path):
        return

    try:
        shutil.rmtree(path)
    except Exception:
        sh(f"rm -rf '{path}'", critical=False, quiet=False)

    if os.path.exists(path):
        print(c(f"❌ Could not delete: {path}", "red"))
        print(c("   Something is holding it open (Finder / VSCode / Spotlight / iCloud).", "red"))
        print(c("   Try:", "yellow"))
        print(c(f"   lsof +D '{path}'", "yellow"))
        print(c(f"   sudo rm -rf '{path}'", "yellow"))
        sys.exit(1)


def worktree_prune():
    sh("git worktree prune", critical=False)


def force_clean_worktree(path: str):
    """
    Removes worktree registration (if any) AND deletes directory on disk,
    then verifies it's gone.
    """
    path = abspath(path)

    sh(f"git worktree remove '{path}' --force", critical=False)
    worktree_prune()
    rm_rf(path)


def unique_temp_dir(base: str) -> str:
    """
    Create a unique per-run temp directory path (NOT created yet).
    """
    base = abspath(base)
    suffix = f"{os.getpid()}-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    return f"{base}-{suffix}"


def git_has_remote_branch(branch: str) -> bool:
    r = run_capture(f"git ls-remote --heads origin {branch}")
    return bool(r.stdout.strip())


def git_has_local_branch(branch: str) -> bool:
    r = run_capture(f"git show-ref --verify --quiet refs/heads/{branch}; echo $?")
    return r.stdout.strip() == "0"


def ensure_deploy_worktree(dep: str):
    """
    Creates a deploy worktree at `dep` on gh-pages.
    """
    dep = abspath(dep)

    if os.path.exists(dep):
        print(c(f"❌ Deploy path already exists (unexpected): {dep}", "red"))
        sys.exit(1)

    if git_has_remote_branch("gh-pages"):
        sh(f"git worktree add '{dep}' origin/gh-pages", critical=True)
        return

    if git_has_local_branch("gh-pages"):
        sh(f"git worktree add '{dep}' gh-pages", critical=True)
        return

    # First-ever deploy: orphan gh-pages
    sh(f"git worktree add --detach '{dep}'", critical=True)
    sh(f"cd '{dep}' && git switch --orphan gh-pages", critical=True)
    sh(f"cd '{dep}' && git rm -rf .", critical=False)


def main():

    # ---- Safety: must run from main branch ----
    branch = get_branch()
    if branch != "main":
        print(c(f"❌ You are on '{branch}'. Switch to 'main' before deploying.", "red"))
        sys.exit(1)

    root = repo_root()
    if not root:
        print(c("❌ Not in a git repo.", "red"))
        sys.exit(1)

    # Unique per-run paths
    BUILD = unique_temp_dir(BUILD_TREE_BASE)
    DEPLOY = unique_temp_dir(DEPLOY_TREE_BASE)

    # Hard safety: worktrees must be outside repo
    assert_outside_repo(root, BUILD, "BUILD_TREE")
    assert_outside_repo(root, DEPLOY, "DEPLOY_TREE")

    # Best-effort cleanup on exit
    def _cleanup():
        for label, p in [("BUILD", BUILD), ("DEPLOY", DEPLOY)]:
            try:
                force_clean_worktree(p)
            except Exception as e:
                if DEBUG:
                    print(c(f"⚠️ atexit cleanup failed for {label}: {p} ({e})", "yellow"))

    atexit.register(_cleanup)

    msg = input("Commit message (main): ").strip() or "Update"

    # ---- Commit source ----
    print(c("• Committing source…", "cyan"))
    sh("git add .", critical=True)
    sh(f'git commit -m "{msg}" || true', critical=False)
    sh("git push origin main", critical=True)

    # ---- Build ----
    print(c("• Preparing isolated build tree…", "cyan"))
    force_clean_worktree(BUILD)
    sh(f"git worktree add --detach '{BUILD}'", critical=True)

    print(c("• Installing deps in build tree…", "cyan"))
    sh(f"cd '{BUILD}' && npm ci || npm install", critical=True)

    print(c("• Building…", "cyan"))
    sh(f"cd '{BUILD}' && npm run build", critical=True, quiet=False)

    # ---- Verify ----
    print(c("• Verifying build…", "cyan"))
    ensure(f"{BUILD}/dist", "dist directory")
    ensure(f"{BUILD}/dist/index.html", "dist/index.html")
    ensure(f"{BUILD}/dist/assets", "dist/assets directory")

    assets = os.listdir(f"{BUILD}/dist/assets")
    js_files = [f for f in assets if f.endswith(".js")]
    if not js_files:
        print(c("❌ Build verification failed: no JS bundle found", "red"))
        sys.exit(1)

    # SPA fallback + CNAME
    sh(f"cp '{BUILD}/dist/index.html' '{BUILD}/dist/404.html'", critical=True)
    sh(f'echo "{CNAME_DOMAIN}" > "{BUILD}/dist/CNAME"', critical=True)

    # ---- Deploy ----
    print(c("• Preparing deploy tree…", "cyan"))
    force_clean_worktree(DEPLOY)
    ensure_deploy_worktree(DEPLOY)

    git_marker = os.path.join(DEPLOY, ".git")
    if not os.path.exists(git_marker):
        print(c("❌ Deploy tree is not a git repo. Aborting.", "red"))
        sys.exit(1)

    print(c("• Deploying to gh-pages…", "cyan"))

    if git_has_remote_branch("gh-pages"):
        sh(f"cd '{DEPLOY}' && git fetch origin gh-pages", critical=False)
        sh(f"cd '{DEPLOY}' && git reset --hard origin/gh-pages", critical=False)

    # Safe wipe (preserve .git)
    sh(f"find '{DEPLOY}' -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {{}} +", critical=True)
    sh(f"cp -R '{BUILD}/dist/.' '{DEPLOY}/'", critical=True)

    sh(f"cd '{DEPLOY}' && git add .", critical=True)
    sh(f"cd '{DEPLOY}' && git commit -m 'Deploy' || true", critical=False)
    sh(f"cd '{DEPLOY}' && git push origin gh-pages", critical=True)

    # ---- Cleanup ----
    print(c("• Cleaning up temp dirs…", "cyan"))
    force_clean_worktree(BUILD)
    force_clean_worktree(DEPLOY)

    print(c("✅ Deploy complete. Main branch untouched.", "green"))


if __name__ == "__main__":
    main()

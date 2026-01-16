import os
import subprocess
import sys
import time
import uuid
import shutil
import atexit
from termcolor import colored as c

# ====== CONFIG ======
VERSION = "1.2.0"
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
    Aggressive delete with verification.
    Uses shutil.rmtree; falls back to rm -rf if needed.
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
    Removes worktree registration (if any) AND deletes directory on disk.
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


def ensure_local_branch_from_remote(branch: str):
    """
    Ensure a local branch exists that tracks origin/<branch>.
    """
    if git_has_local_branch(branch):
        return
    if not git_has_remote_branch(branch):
        return
    sh(f"git fetch origin {branch}", critical=True)
    sh(f"git branch {branch} origin/{branch}", critical=False)


def ensure_deploy_worktree(dep: str):
    """
    Creates a deploy worktree at `dep` on gh-pages.

    IMPORTANT:
    - Always ends with DEPLOY checked out to local branch 'gh-pages' (not detached).
    - This guarantees commits advance the gh-pages branch tip.
    """
    dep = abspath(dep)

    if os.path.exists(dep):
        print(c(f"❌ Deploy path already exists (unexpected): {dep}", "red"))
        sys.exit(1)

    if git_has_remote_branch("gh-pages"):
        ensure_local_branch_from_remote("gh-pages")
        sh(f"git worktree add '{dep}' gh-pages", critical=True)
        return

    if git_has_local_branch("gh-pages"):
        sh(f"git worktree add '{dep}' gh-pages", critical=True)
        return

    # First-ever deploy: create orphan gh-pages inside a detached worktree,
    # but immediately create the actual gh-pages branch there.
    sh(f"git worktree add --detach '{dep}'", critical=True)
    sh(f"cd '{dep}' && git switch --orphan gh-pages", critical=True)
    sh(f"cd '{dep}' && git rm -rf .", critical=False)


def read_text_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return ""


def write_text_file(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


def normalize_domain(s: str) -> str:
    return (s or "").strip()


def enforce_cname(deploy_dir: str, desired_domain: str):
    """
    Hard guarantee:
    - CNAME exists
    - CNAME is NOT empty
    - CNAME equals desired domain (normalized)
    """
    desired = normalize_domain(desired_domain)
    if not desired:
        print(c("❌ CNAME_DOMAIN is empty. Refusing to deploy.", "red"))
        sys.exit(1)

    cname_path = os.path.join(deploy_dir, "CNAME")
    write_text_file(cname_path, desired + "\n")

    actual = normalize_domain(read_text_file(cname_path))
    if actual != desired:
        print(c("❌ CNAME write/verify failed.", "red"))
        print(c(f"   Expected: {desired}", "red"))
        print(c(f"   Actual:   {actual}", "red"))
        sys.exit(1)


def deploy_verify_root(deploy_dir: str):
    """
    Verify publish root is valid BEFORE committing/pushing.
    """
    required = [
        (os.path.join(deploy_dir, "index.html"), "index.html"),
        (os.path.join(deploy_dir, "assets"), "assets/"),
        (os.path.join(deploy_dir, "CNAME"), "CNAME"),
        (os.path.join(deploy_dir, ".nojekyll"), ".nojekyll"),
    ]
    for p, label in required:
        if not os.path.exists(p):
            print(c(f"❌ Deploy verification failed: missing {label}", "red"))
            print(c(f"   Path: {p}", "red"))
            sys.exit(1)

    # CNAME must be non-empty
    cname_val = normalize_domain(read_text_file(os.path.join(deploy_dir, "CNAME")))
    if not cname_val:
        print(c("❌ Deploy verification failed: CNAME is empty.", "red"))
        sys.exit(1)


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

    # ---- Verify build output ----
    print(c("• Verifying build…", "cyan"))
    ensure(f"{BUILD}/dist", "dist directory")
    ensure(f"{BUILD}/dist/index.html", "dist/index.html")
    ensure(f"{BUILD}/dist/assets", "dist/assets directory")

    assets = os.listdir(f"{BUILD}/dist/assets")
    js_files = [f for f in assets if f.endswith(".js")]
    if not js_files:
        print(c("❌ Build verification failed: no JS bundle found", "red"))
        sys.exit(1)

    # SPA fallback (always)
    sh(f"cp '{BUILD}/dist/index.html' '{BUILD}/dist/404.html'", critical=True)

    # NOTE: We intentionally DO NOT rely on dist/CNAME anymore.
    # We will enforce CNAME directly in the deploy tree after the wipe.

    # ---- Deploy ----
    print(c("• Preparing deploy tree…", "cyan"))
    force_clean_worktree(DEPLOY)
    ensure_deploy_worktree(DEPLOY)

    git_marker = os.path.join(DEPLOY, ".git")
    if not os.path.exists(git_marker):
        print(c("❌ Deploy tree is not a git repo. Aborting.", "red"))
        sys.exit(1)

    # HARD GUARANTEE: deploy worktree must be on gh-pages branch (not detached)
    head_state = run_capture(
        f"cd '{DEPLOY}' && git symbolic-ref --quiet --short HEAD || echo DETACHED"
    ).stdout.strip()
    if head_state == "DETACHED":
        print(c("❌ Deploy worktree is DETACHED. Refusing to deploy.", "red"))
        print(c("   This would create commits that do not advance gh-pages.", "red"))
        sys.exit(1)
    if head_state != "gh-pages":
        sh(f"cd '{DEPLOY}' && git switch gh-pages", critical=True)

    print(c("• Deploying to gh-pages…", "cyan"))

    # Sync to remote gh-pages if it exists
    if git_has_remote_branch("gh-pages"):
        sh(f"cd '{DEPLOY}' && git fetch origin gh-pages", critical=True)
        sh(f"cd '{DEPLOY}' && git reset --hard origin/gh-pages", critical=True)

    # Wipe publish root (preserve .git)
    sh(f"find '{DEPLOY}' -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {{}} +", critical=True)

    # Copy dist output into deploy dir
    sh(f"cp -R '{BUILD}/dist/.' '{DEPLOY}/'", critical=True)

    # Always prevent Jekyll interference
    sh(f"touch '{DEPLOY}/.nojekyll'", critical=True)

    # HARD CNAME LOCK (write AFTER wipe + copy, verify non-empty)
    enforce_cname(DEPLOY, CNAME_DOMAIN)

    # Verify publish root contents before committing/pushing
    deploy_verify_root(DEPLOY)

    sh(f"cd '{DEPLOY}' && git add .", critical=True)
    sh(f"cd '{DEPLOY}' && git status --porcelain", critical=False, quiet=False)
    sh(f"cd '{DEPLOY}' && git commit -m 'Deploy' || true", critical=False)

    # Push the branch tip (not detached)
    sh(f"cd '{DEPLOY}' && git push origin gh-pages:gh-pages", critical=True)

    # ---- Cleanup ----
    print(c("• Cleaning up temp dirs…", "cyan"))
    force_clean_worktree(BUILD)
    force_clean_worktree(DEPLOY)

    print(c("✅ Deploy complete. Main branch untouched.", "green"))
    print(c(f"🔗 Custom domain enforced via CNAME: {CNAME_DOMAIN}", "cyan"))


if __name__ == "__main__":
    main()

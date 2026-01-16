import os
import subprocess
import sys
from termcolor import colored as c

# ====== CONFIG ======
CNAME_DOMAIN = "react.bookql.com"

# Worktrees MUST be outside repo
BUILD_TREE = "../.build-temp-react"
DEPLOY_TREE = "../.gh-pages-temp-react"

DEBUG = False
# ====================


def sh(cmd: str, critical: bool = False, quiet: bool = True):
    """
    Runs a shell command.
    - If DEBUG=True, always prints and never suppresses output.
    - If a critical command fails, prints command and exits.
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
        # Re-run once without quiet to show the real error output:
        if quiet:
            print(c("↳ Showing command output:", "yellow"))
            os.system(cmd)
        sys.exit(1)


def get_branch() -> str:
    return subprocess.run(
        "git branch --show-current",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()


def repo_root() -> str:
    out = subprocess.run(
        "git rev-parse --show-toplevel",
        shell=True,
        capture_output=True,
        text=True
    )
    return out.stdout.strip()


def abspath(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))


def assert_outside_repo(repo: str, candidate: str, label: str):
    repo = abspath(repo)
    candidate = abspath(candidate)

    # Candidate must NOT be repo itself, and must NOT live under repo/
    if candidate == repo or candidate.startswith(repo + os.sep):
        print(c(f"❌ {label} must be OUTSIDE the repo.", "red"))
        print(c(f"   Repo:     {repo}", "red"))
        print(c(f"   {label}: {candidate}", "red"))
        sys.exit(1)


def ensure(path: str, label: str):
    if not os.path.exists(path):
        print(c(f"❌ Missing {label}: {path}", "red"))
        sys.exit(1)


def force_clean_worktree(path: str):
    # Remove from git's worktree list (if it is one)
    sh(f"git worktree remove {path} --force || true")
    sh("git worktree prune || true")
    # Remove filesystem path no matter what it is
    sh(f"rm -rf {path}")
    if os.path.exists(path):
        print(c(f"❌ Could not remove {path}. Aborting.", "red"))
        sys.exit(1)


def ensure_deploy_worktree(dep: str):
    """
    Deterministically create a deploy worktree.
    Handles:
      - gh-pages exists locally
      - gh-pages exists only remotely
      - gh-pages doesn't exist anywhere yet
    """
    # Try to fetch remote gh-pages (ok if it doesn't exist)
    sh("git fetch origin gh-pages || true", critical=False)

    # Try to attach to local gh-pages (works if branch exists locally)
    sh(f"git worktree add {dep} gh-pages", critical=False)

    if os.path.isdir(dep):
        return

    # If branch exists remotely but not locally, create local tracking branch
    # (This is safe even if it already exists.)
    sh("git show-ref --verify --quiet refs/remotes/origin/gh-pages && "
       "git branch -f gh-pages origin/gh-pages || true", critical=False)

    # Try again
    sh(f"git worktree add {dep} gh-pages", critical=False)

    if os.path.isdir(dep):
        return

    # Last resort: create orphan gh-pages
    sh(f"git worktree add {dep} --orphan gh-pages", critical=True)


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

    # Hard safety: ensure worktrees are outside repo
    assert_outside_repo(root, BUILD_TREE, "BUILD_TREE")
    assert_outside_repo(root, DEPLOY_TREE, "DEPLOY_TREE")

    msg = input("Commit message (main): ").strip() or "Update"

    # ---- Commit source ----
    print(c("• Committing source…", "cyan"))
    sh("git add .", critical=True)
    sh(f'git commit -m "{msg}" || true', critical=False)
    sh("git push origin main", critical=True)

    # ---- Build in isolated detached worktree ----
    print(c("• Preparing isolated build tree…", "cyan"))
    force_clean_worktree(BUILD_TREE)
    sh(f"git worktree add --detach {BUILD_TREE}", critical=True)

    print(c("• Installing deps in build tree…", "cyan"))
    sh(f"cd {BUILD_TREE} && npm ci || npm install", critical=True)

    print(c("• Building…", "cyan"))
    sh(f"cd {BUILD_TREE} && npm run build", critical=True, quiet=False)

    # ---- Verify build ----
    print(c("• Verifying build…", "cyan"))
    ensure(f"{BUILD_TREE}/dist", "dist directory")
    ensure(f"{BUILD_TREE}/dist/index.html", "dist/index.html")
    ensure(f"{BUILD_TREE}/dist/assets", "dist/assets directory")

    assets = os.listdir(f"{BUILD_TREE}/dist/assets")
    js_files = [f for f in assets if f.endswith(".js")]
    if not js_files:
        print(c("❌ Build verification failed: no .js bundle in dist/assets", "red"))
        sys.exit(1)

    # SPA fallback + CNAME
    sh(f"cp {BUILD_TREE}/dist/index.html {BUILD_TREE}/dist/404.html", critical=True)
    sh(f'echo "{CNAME_DOMAIN}" > {BUILD_TREE}/dist/CNAME', critical=True)

    # ---- Deploy via gh-pages worktree ----
    print(c("• Preparing deploy tree…", "cyan"))
    force_clean_worktree(DEPLOY_TREE)
    ensure_deploy_worktree(DEPLOY_TREE)

    print(c("• Deploying to gh-pages…", "cyan"))

    # Sync to remote state (no history rewrite; clean base)
    sh(f"cd {DEPLOY_TREE} && git fetch origin gh-pages", critical=True)
    sh(f"cd {DEPLOY_TREE} && git reset --hard origin/gh-pages", critical=True)

    # Replace contents safely (includes dotfiles)
    sh(f"find {DEPLOY_TREE} -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +", critical=True)
    sh(f"cp -R {BUILD_TREE}/dist/. {DEPLOY_TREE}/", critical=True)

    sh(f"cd {DEPLOY_TREE} && git add .", critical=True)
    sh(f'cd {DEPLOY_TREE} && git commit -m "Deploy" || true', critical=False)
    sh(f"cd {DEPLOY_TREE} && git push origin gh-pages", critical=True)

    # ---- Cleanup ----
    force_clean_worktree(BUILD_TREE)
    force_clean_worktree(DEPLOY_TREE)

    print(c("✅ Deploy complete. Main branch untouched.", "green"))


if __name__ == "__main__":
    main()

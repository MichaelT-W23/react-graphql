import os
import subprocess
import sys
from termcolor import colored as c

CNAME_DOMAIN = "react.bookql.com"

# These MUST be outside the repo directory
BUILD_TREE = "../.build-temp-react"
DEPLOY_TREE = "../.gh-pages-temp-react"

def sh(cmd: str, critical: bool = False, quiet: bool = True):
    if not quiet:
        print(c(f"> {cmd}", "cyan"))
        code = os.system(cmd)
    else:
        code = os.system(f"{cmd} > /dev/null 2>&1")

    if critical and code != 0:
        print(c(f"❌ Failed: {cmd}", "red"))
        sys.exit(1)

def get_branch() -> str:
    return subprocess.run(
        "git branch --show-current",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

def ensure(path: str, label: str):
    if not os.path.exists(path):
        print(c(f"❌ Missing {label}: {path}", "red"))
        sys.exit(1)

def force_clean_worktree(path: str):
    sh(f"git worktree remove {path} --force || true")
    sh("git worktree prune || true")
    sh(f"rm -rf {path}")

    if os.path.exists(path):
        print(c(f"❌ Could not remove {path}. Aborting.", "red"))
        sys.exit(1)

def main():
    # --- Safety: must be on main ---
    branch = get_branch()
    if branch != "main":
        print(c(f"❌ You are on '{branch}'. Switch to 'main' before deploying.", "red"))
        sys.exit(1)

    msg = input("Commit message (main): ").strip() or "Update"

    # --- Commit source ---
    print(c("• Committing source…", "cyan"))
    sh("git add .", critical=True)
    sh(f'git commit -m "{msg}" || true', critical=True)
    sh("git push origin main", critical=True)

    # --- Prepare isolated build worktree ---
    print(c("• Preparing isolated build tree…", "cyan"))
    force_clean_worktree(BUILD_TREE)
    sh(f"git worktree add --detach {BUILD_TREE}", critical=True)

    # --- Build inside the temp tree ---
    print(c("• Building…", "cyan"))
    sh(f"cd {BUILD_TREE} && npm run build", critical=True, quiet=False)

    # --- Verify build ---
    print(c("• Verifying build…", "cyan"))
    ensure(f"{BUILD_TREE}/dist", "dist directory")
    ensure(f"{BUILD_TREE}/dist/index.html", "index.html")
    ensure(f"{BUILD_TREE}/dist/assets", "assets directory")

    assets = os.listdir(f"{BUILD_TREE}/dist/assets")
    js_files = [f for f in assets if f.endswith(".js")]

    if not js_files:
        print(c("❌ No JS bundle found in dist/assets", "red"))
        sys.exit(1)

    # --- SPA + CNAME ---
    sh(f"cp {BUILD_TREE}/dist/index.html {BUILD_TREE}/dist/404.html", critical=True)
    sh(f'echo "{CNAME_DOMAIN}" > {BUILD_TREE}/dist/CNAME', critical=True)

    # --- Prepare deploy tree ---
    print(c("• Preparing deploy tree…", "cyan"))
    force_clean_worktree(DEPLOY_TREE)

    sh(f"git worktree add {DEPLOY_TREE} gh-pages", critical=False)

    if not os.path.isdir(DEPLOY_TREE):
        sh(f"git worktree add {DEPLOY_TREE} --orphan gh-pages", critical=True)

    # --- Replace contents ---
    sh(f"rm -rf {DEPLOY_TREE}/*", critical=True)
    sh(f"cp -r {BUILD_TREE}/dist/* {DEPLOY_TREE}/", critical=True)

    # --- Commit + push ---
    sh(f"cd {DEPLOY_TREE} && git add .", critical=True)
    sh(f'cd {DEPLOY_TREE} && git commit -m "Deploy"', critical=False)
    sh(f"cd {DEPLOY_TREE} && git push -f origin HEAD:gh-pages", critical=True)

    # --- Cleanup ---
    force_clean_worktree(BUILD_TREE)
    force_clean_worktree(DEPLOY_TREE)

    print(c("✅ Deploy complete. Main branch untouched.", "green"))

if __name__ == "__main__":
    main()

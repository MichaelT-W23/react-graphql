import os
import subprocess
import sys
from termcolor import colored as c

CNAME_DOMAIN = "react.bookql.com"
TEMP_DIR = ".gh-pages-temp"

def sh(cmd: str, critical: bool = False, quiet: bool = True) -> None:
    """
    Run a shell command.
    - quiet=True suppresses stdout/stderr (unless it fails and critical=False you'd still not see it).
    """
    if not quiet:
        print(c(f"> {cmd}", "cyan"))
        code = os.system(cmd)
    else:
        # suppress output; still preserve exit code
        code = os.system(f"{cmd} > /dev/null 2>&1")

    if critical and code != 0:
        print(c(f"❌ Failed: {cmd}", "red"))
        sys.exit(1)

def get_branch() -> str:
    p = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def ensure_file_exists(path: str, label: str) -> None:
    if not os.path.exists(path):
        print(c(f"❌ Missing {label}: {path}", "red"))
        sys.exit(1)

def main() -> None:
    branch = get_branch()
    if branch != "main":
        print(c(f"❌ You are on '{branch}'. Switch to 'main' before deploying.", "red"))
        sys.exit(1)

    commit_msg = input("Commit message (main): ").strip() or "Update"

    # --- Commit source (main) ---
    print(c("• Committing source (main)…", "cyan"))
    sh("git add .", critical=True)
    sh(f'git commit -m "{commit_msg}" || true', critical=True)  # 'true' to avoid failing on "nothing to commit"
    sh("git push origin main", critical=True)

    # --- Build ---
    print(c("• Building…", "cyan"))
    sh("npm run build", critical=True, quiet=False)  # show build output (useful)

    # --- Verify build output ---
    print(c("• Verifying build…", "cyan"))
    ensure_file_exists("dist", "dist directory")
    ensure_file_exists("dist/index.html", "dist/index.html")
    ensure_file_exists("dist/assets", "dist/assets directory")

    assets = os.listdir("dist/assets")
    js_files = [f for f in assets if f.endswith(".js")]
    if not js_files:
        print(c("❌ Build verification failed: no .js bundle in dist/assets", "red"))
        sys.exit(1)

    # SPA fallback + CNAME
    sh("cp dist/index.html dist/404.html", critical=True)
    sh(f'echo "{CNAME_DOMAIN}" > dist/CNAME', critical=True)

    # --- Deploy using worktree (does NOT touch node_modules or working tree) ---
    print(c("• Deploying to gh-pages…", "cyan"))
    sh(f"git worktree remove {TEMP_DIR} --force || true", critical=True)
    # If gh-pages exists, check it out; otherwise create orphan worktree
    sh(f"git worktree add {TEMP_DIR} gh-pages", critical=False)
    if not os.path.isdir(TEMP_DIR):
        sh(f"git worktree add {TEMP_DIR} --orphan gh-pages", critical=True)

    # Replace contents
    sh(f"rm -rf {TEMP_DIR}/*", critical=True)
    sh(f"cp -r dist/* {TEMP_DIR}/", critical=True)

    # Commit + push
    sh(f'cd {TEMP_DIR} && git add .', critical=True)
    sh(f'cd {TEMP_DIR} && git commit -m "Deploy"', critical=False)  # allow "nothing to commit"
    sh(f"cd {TEMP_DIR} && git push -f origin HEAD:gh-pages", critical=True)

    # Cleanup worktree
    sh(f"git worktree remove {TEMP_DIR} --force", critical=True)

    print(c("✅ Done. Site deployed.", "green"))

if __name__ == "__main__":
    main()

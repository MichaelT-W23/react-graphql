import os
import subprocess
from termcolor import colored as c
import sys

def run(cmd, critical=False):
    print(c(f"> {cmd}", "cyan"))
    code = os.system(cmd)
    if critical and code != 0:
        print(c("\n❌ Command failed, aborting deploy.\n", "red"))
        sys.exit(1)

# Ensure on main
branch = subprocess.run('git branch --show-current', shell=True, capture_output=True, text=True).stdout.strip()
print("On branch", branch)

if branch != "main":
    print(c("Switch to main before deploying.", "red"))
    sys.exit(1)

commit_msg = input("Enter your commit message: ")

# Commit source
run('git add .', critical=True)
run(f'git commit -m "{commit_msg}" || true')
run('git push origin main', critical=True)

# Build
run('npm run build', critical=True)

# Verify build
if not os.path.exists('dist/assets'):
    print(c("❌ Build failed: dist/assets missing", "red"))
    sys.exit(1)

assets = os.listdir('dist/assets')
js_files = [f for f in assets if f.endswith('.js')]
if not js_files:
    print(c("❌ Build failed: JS bundle missing", "red"))
    sys.exit(1)

print(c(f"✔ JS bundle found: {js_files[0]}", "green"))

# SPA fallback
run('cp dist/index.html dist/404.html', critical=True)

# CNAME
run('echo "react.bookql.com" > dist/CNAME', critical=True)

# Deploy using worktree
temp_dir = ".gh-pages-temp"
run(f'git worktree remove {temp_dir} --force || true')
run(f'git worktree add {temp_dir} gh-pages || git worktree add {temp_dir} --orphan', critical=True)

run(f'rm -rf {temp_dir}/*', critical=True)
run(f'cp -r dist/* {temp_dir}/', critical=True)

run(f'cd {temp_dir} && git add .', critical=True)
run(f'cd {temp_dir} && git commit -m "Deploy"', critical=True)
run(f'cd {temp_dir} && git push -f origin HEAD:gh-pages', critical=True)

run(f'git worktree remove {temp_dir} --force', critical=True)

print(c("\n🚀 React deployment complete and SAFE", "green"))

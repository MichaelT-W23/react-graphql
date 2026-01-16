import os
import subprocess
from termcolor import colored as c

def run(cmd):
    print(c(f"> {cmd}", "cyan"))
    os.system(cmd)

process = subprocess.run('git status', shell=True, capture_output=True, text=True)
output = process.stdout

branch = repr(output).split("\\n")[0].replace("'On branch ", "").strip()

print('On branch ', end="")

if branch == 'main':
    print(c(branch, 'green'))
else:
    print(c(branch, 'red'))
    print('Move changes to the main branch, then switch to the main branch.')
    print('git stash')
    print('git checkout main')
    print('git pull origin main')
    print(f'git merge {branch}')
    print('git stash apply')
    print('git push origin main')
    exit(0)

commit_msg = input("Enter your commit message: ")

# Commit source
run('git add .')
run(f'git commit -m "{commit_msg}" || true')
run('git push origin main')

# Build
run('npm run build')

# SPA fallback
run('cp dist/index.html dist/404.html')

# Deploy using split + force
run('git subtree split --prefix dist -b temp-gh-pages')
run('git push -f origin temp-gh-pages:gh-pages')
run('git branch -D temp-gh-pages')

print(c("\nDeployment complete 🚀", "green"))

import os
import subprocess
from termcolor import colored as c

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

os.system('git add .')
os.system(f'git commit -m "{commit_msg}"')
os.system('git push origin main')
os.system('npm run build')
os.system('cp dist/index.html dist/404.html')
os.system('git add dist -f')
os.system(f'git commit -m "{commit_msg}"')
os.system('git subtree push --prefix dist origin gh-pages')

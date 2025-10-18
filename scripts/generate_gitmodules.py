#!/usr/bin/env python3
import os, subprocess, sys, time
repo = os.path.abspath(os.getcwd())
print('repo:', repo)
try:
    out = subprocess.check_output(['git','ls-files','-s'], text=True)
except subprocess.CalledProcessError as e:
    print('git ls-files failed:', e)
    sys.exit(1)
paths = []
for line in out.splitlines():
    if line.startswith('160000'):
        parts = line.split()
        if len(parts) >= 4:
            paths.append(parts[3])
print(f'Found {len(paths)} gitlink paths')
if not paths:
    sys.exit(0)
# backup existing .gitmodules
if os.path.exists('.gitmodules'):
    bak = f'.gitmodules.bak.{int(time.time())}'
    os.rename('.gitmodules', bak)
    print('Backed up existing .gitmodules ->', bak)
entries = []
for p in paths:
    print('Processing', p)
    gp = os.path.join(repo, p)
    if os.path.isdir(gp) and (os.path.isdir(os.path.join(gp, '.git')) or os.path.isfile(os.path.join(gp, '.git'))):
        url = None
        try:
            url = subprocess.check_output(['git','-C',gp,'remote','get-url','origin'], text=True).strip()
        except subprocess.CalledProcessError:
            try:
                rv = subprocess.check_output(['git','-C',gp,'remote','-v'], text=True).strip()
                if rv:
                    url = rv.splitlines()[0].split()[1]
            except Exception:
                url = None
        sha = None
        try:
            sha = subprocess.check_output(['git','-C',gp,'rev-parse','HEAD'], text=True).strip()
        except Exception:
            sha = None
        print('  url=', url or '<no-remote>', ' sha=', sha or '<no-head>')
        if url:
            entries.append((p, url))
    else:
        print('  -> not a git repo, skipping')
# write .gitmodules
with open('.gitmodules', 'w') as f:
    f.write('# Generated .gitmodules\n')
    for p, url in entries:
        f.write(f'[submodule "{p}"]\n')
        f.write(f'\tpath = {p}\n')
        f.write(f'\turl = {url}\n')
        f.write('\n')
print('Wrote .gitmodules with', len(entries), 'entries')
# commit .gitmodules
try:
    subprocess.check_call(['git','add','.gitmodules'])
    subprocess.check_call(['git','commit','-m','Add .gitmodules registering nested repos as submodules'])
    print('Committed .gitmodules')
except subprocess.CalledProcessError:
    print('Nothing to commit for .gitmodules or commit failed')
# init submodules
subprocess.call(['git','submodule','init','--recursive'])
subprocess.call(['git','submodule','status','--recursive'])
print('Done')

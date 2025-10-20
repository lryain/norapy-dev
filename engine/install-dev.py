#!/usr/bin/env python3
"""
Development environment installer for OVOS

This script hand# Define installation order based on dependencies
# Each tuple: (path, description)
# (This will be auto-discovered in main())

def log_info(msg):tion of the OVOS development environment with
proper handling of local package editable installs. 

Key features:
- Reads both requirements.txt and commented-out -e paths
- Installs packages in dependency order
- Uses --no-build-isolation to allow setuptools to access already-installed packages
- Automatically detects local dependencies from setup.py files

Example commented dependencies in requirements files:
    # -e ../../../engine-utils/ovos-utils
    # -e ../../ovos-config
"""
import subprocess
import sys
import os
import re
import argparse
import site
import sysconfig
from pathlib import Path

# Colors for output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def log_info(msg):
    print(f"{BLUE}ℹ{NC} {msg}")

def log_success(msg):
    print(f"{GREEN}✓{NC} {msg}")

def log_error(msg):
    print(f"{RED}✗{NC} {msg}")

def log_warn(msg):
    print(f"{YELLOW}⚠{NC} {msg}")

def run_pip(args, desc=None):
    """Run pip install with error handling"""
    if desc:
        log_info(desc)
    
    cmd = [sys.executable, "-m", "pip", "install", "--no-build-isolation", "-q"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode == 0

def extract_commented_local_deps(req_file):
    """
    Extract commented-out -e paths from requirements files.
    
    Example:
        # -e ../../../engine-utils/ovos-utils
        # -e ../../ovos-config
    """
    local_deps = []
    if not req_file.exists():
        return local_deps
    
    with open(req_file) as f:
        for line in f:
            line = line.strip()
            # Match: # -e path/to/package
            match = re.match(r'^#+\s*-e\s+(.+)$', line)
            if match:
                dep_path = match.group(1).strip()
                local_deps.append(dep_path)
    
    return local_deps

def resolve_relative_path(base_dir, relative_path):
    """
    Resolve a relative path from base_dir.
    
    Example:
        base_dir = /path/to/engine/engine-core/ovos-core
        relative_path = ../../../engine-utils/ovos-utils
        result = /path/to/engine/engine-utils/ovos-utils
    """
    return (base_dir / relative_path).resolve()

# Define installation order based on dependencies
# Each tuple: (path, description)
INSTALL_ORDER = [
    ("./engine-utils/ovos-utils", "ovos-utils (utilities)"),
    ("./engine-core/ovos-config", "ovos-config (configuration)"),
    ("./engine-core/ovos-plugin-manager", "ovos-plugin-manager"),
    ("./engine-core/ovos-workshop", "ovos-workshop (skill framework)"),
    ("./engine-core/ovos-messagebus", "ovos-messagebus (IPC server)"),
    ("./engine-core/ovos-core", "ovos-core (main system)"),
    ("./engine-plugin/ovos-ocp-pipeline-plugin", "ovos-ocp-pipeline-plugin (OCP pipeline)")
]

def main():
    """Install development environment"""
    engine_dir = Path(__file__).parent.absolute()
    os.chdir(engine_dir)
    
    parser = argparse.ArgumentParser(description='Install OVOS packages for development')
    parser.add_argument('--skip-installed', action='store_true',
                        help='Skip packages that are already installed (pip show)')
    parser.add_argument('--skip-if-editable', action='store_true',
                        help='Skip packages that are installed in editable mode pointing to the same path')
    args = parser.parse_args()

    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}OVOS Development Environment Installer{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")
    
    log_info("Installing OVOS packages in dependency order...")
    log_info("Using --no-build-isolation for editable installs")
    print()
    
    # Keep track of all packages to install
    all_packages = []
    packages_seen = set()
    
    def add_package_and_deps(path, desc, is_local=False):
        """Add a package and its local dependencies to install queue"""
        pkg_path = engine_dir / path
        
        if not pkg_path.exists():
            log_warn(f"Skipping {desc}: {path} not found")
            return
        
        if str(pkg_path) in packages_seen:
            return  # Already added
        
        packages_seen.add(str(pkg_path))
        
        # First add local dependencies (they must be installed first)
        setup_py = pkg_path / "setup.py"
        if setup_py.exists():
            # Try to extract local deps from commented sections
            local_deps = extract_commented_local_deps(setup_py)
            for local_dep_rel in local_deps:
                local_dep_path = resolve_relative_path(pkg_path, local_dep_rel)
                if local_dep_path.exists():
                    local_desc = local_dep_path.name
                    add_package_and_deps(
                        str(local_dep_path.relative_to(engine_dir)),
                        local_desc,
                        is_local=True
                    )
        
        # Then add the package itself
        all_packages.append({
            'path': str(pkg_path.relative_to(engine_dir)),
            'full_path': str(pkg_path),
            'desc': desc
        })
    
    # Start with core packages (in dependency order)
    core_packages = [
        ("./engine-utils/ovos-utils", "ovos-utils (utilities)"),
        ("./engine-core/ovos-config", "ovos-config (configuration)"),
        ("./engine-core/ovos-plugin-manager", "ovos-plugin-manager"),
        ("./engine-core/ovos-workshop", "ovos-workshop (skill framework)"),
        ("./engine-core/ovos-messagebus", "ovos-messagebus (IPC server)"),
        ("./engine-core/ovos-core", "ovos-core (main system)"),
        ("./engine-plugin/ovos-ocp-pipeline-plugin", "ovos-ocp-pipeline-plugin (OCP pipeline)"),
    ]
    
    for path, desc in core_packages:
        add_package_and_deps(path, desc)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_packages = []
    for pkg in all_packages:
        if pkg['full_path'] not in seen:
            seen.add(pkg['full_path'])
            unique_packages.append(pkg)
    
    print(f"Will install {len(unique_packages)} package(s):\n")
    for pkg in unique_packages:
        print(f"  • {pkg['desc']} ({pkg['path']})")
    print()
    
    failed = []
    skipped = []

    # helper: check pip show
    def pip_show(pkg_name):
        p = subprocess.run([sys.executable, '-m', 'pip', 'show', pkg_name], capture_output=True, text=True)
        return p.returncode == 0, p.stdout

    # helper: find egg-link for a package name in site-packages dirs
    def find_egg_link(pkg_name):
        sp_dirs = []
        try:
            sp_dirs.extend(site.getsitepackages())
        except Exception:
            pass
        try:
            sp_dirs.append(sysconfig.get_paths().get('purelib'))
        except Exception:
            pass
        for sp in filter(None, sp_dirs):
            egg = Path(sp) / (pkg_name + '.egg-link')
            if egg.exists():
                try:
                    with egg.open() as f:
                        target = f.readline().strip()
                        return target
                except Exception:
                    continue
        return None
    for pkg in unique_packages:
        pkg_name = Path(pkg['full_path']).name

        # Optionally skip if package already installed
        if args.skip_installed:
            installed, info = pip_show(pkg_name)
            if installed:
                log_warn(f"Skipping {pkg['desc']}: {pkg_name} already installed (pip show)")
                skipped.append(pkg['desc'])
                continue

        # Optionally skip if editable install already points to same path
        if args.skip_if_editable:
            egg_target = find_egg_link(pkg_name)
            if egg_target:
                try:
                    egg_res = Path(egg_target).resolve()
                    pkg_res = Path(pkg['full_path']).resolve()
                    if egg_res == pkg_res:
                        log_warn(f"Skipping {pkg['desc']}: editable install already points to {pkg_res}")
                        skipped.append(pkg['desc'])
                        continue
                except Exception:
                    pass

        print(f"  Installing {pkg['desc']}...")
        if run_pip(["-e", pkg['full_path']]):
            log_success(f"Installed {pkg['desc']}")
        else:
            log_error(f"Failed to install {pkg['desc']}")
            failed.append(pkg['desc'])
        print()
    
    if failed or skipped:
        print(f"\n{RED}{'='*60}{NC}")
        if failed:
            log_error(f"Failed to install {len(failed)} package(s):")
            for pkg in failed:
                print(f"  - {pkg}")
        if skipped:
            log_warn(f"Skipped {len(skipped)} package(s):")
            for pkg in skipped:
                print(f"  - {pkg}")
        print(f"{RED}{'='*60}{NC}\n")
        return 1
    else:
        print(f"\n{GREEN}{'='*60}{NC}")
        log_success("All packages installed successfully!")
        log_success("Development mode enabled - code changes take effect immediately")
        print(f"{GREEN}{'='*60}{NC}\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())

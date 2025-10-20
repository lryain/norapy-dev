import os
import re

ENGINE_ROOT = "/home/pi/dev/norapy-dev/engine"

def find_ovos_packages(root):
    mapping = {}
    # 只遍历 engine 下一级目录（engine-core, engine-plugins, ...），避免进入包内部
    for group in os.listdir(root):
        group_path = os.path.join(root, group)
        if not os.path.isdir(group_path):
            continue
        try:
            for item in os.listdir(group_path):
                if item.startswith('ovos-') or item.startswith('ovos_'):
                    # item 是顶层包目录，记录其绝对路径
                    mapping[item.replace('_', '-')] = os.path.abspath(os.path.join(group_path, item))
        except PermissionError:
            continue
    return mapping

def extract_ovos_deps(reqfile):
    ovos_deps = set()
    with open(reqfile, "r") as f:
        for line in f:
            m = re.match(r"(ovos[-_][\w\-]+)", line.strip())
            if m:
                ovos_deps.add(m.group(1).replace('_', '-'))
    return ovos_deps

def process_one_package(pkg_dir, ovos_mapping):
    req_paths = []
    # 根目录 requirements.txt
    reqfile = os.path.join(pkg_dir, "requirements.txt")
    if os.path.isfile(reqfile):
        req_paths.append(reqfile)
    # requirements/*.txt
    reqdir = os.path.join(pkg_dir, "requirements")
    if os.path.isdir(reqdir):
        for f in os.listdir(reqdir):
            if f.endswith(".txt"):
                req_paths.append(os.path.join(reqdir, f))
    # 收集所有 ovos依赖
    ovos_deps = set()
    for req in req_paths:
        ovos_deps |= extract_ovos_deps(req)
    # 写 constraints.txt
    if ovos_deps:
        with open(os.path.join(pkg_dir, "constraints.txt"), "w") as f:
            for dep in sorted(ovos_deps):
                if dep in ovos_mapping:
                    # 只到包目录，不拼接包名子目录
                    pkg_path = ovos_mapping[dep]
                    f.write(f"{dep} @ file://{pkg_path}\n")

if __name__ == "__main__":
    ovos_mapping = find_ovos_packages(ENGINE_ROOT)
    for subdir, dirs, files in os.walk(ENGINE_ROOT):
        if "setup.py" in files or "pyproject.toml" in files:
            process_one_package(subdir, ovos_mapping)

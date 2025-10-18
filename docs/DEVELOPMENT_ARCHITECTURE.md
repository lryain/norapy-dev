# 大型多包系统的开发架构

## 问题背景

当你有像 OpenVoiceOS 这样的几百个库组成的系统时，需要解决的核心问题是：

1. **生产环境**：用户安装 `pip install ovos-core`，应该自动安装所有 PyPI 上的依赖
2. **开发环境**：开发者需要快速修改代码，改动立即生效，同时维护多个本地包的依赖关系

## 业界标准架构

### 1. 包的结构分层

```
Core Layer (必需)
  ├── ovos-utils          # 基础工具库
  ├── ovos-config         # 配置管理
  ├── ovos-messagebus     # 进程间通信
  └── ovos-core          # 核心系统

Framework Layer (可选)
  ├── ovos-workshop       # 技能框架
  ├── ovos-plugin-manager # 插件系统
  └── ovos-PHAL          # 硬件抽象层

Extension Layer (扩展)
  ├── plugins/           # 音频、STT、TTS 等插件
  ├── skills/            # 技能
  └── services/          # 服务
```

### 2. 两套 Requirements 文件策略

#### 生产环境 (requirements.txt)

```txt
# requirements.txt - 仅包含 PyPI 包名
requests>=2.26,<3.0
python-dateutil>=2.6,<3.0
watchdog>=2.1,<3.0
combo-lock>=0.2.2,<0.4
ovos-utils>=0.3.5,<1.0.0     # ← PyPI 上的版本
ovos-config>=0.0.12,<2.0.0   # ← PyPI 上的版本
```

**优点**：
- setuptools 可以正常解析
- `pip install -e .` 可以正常工作
- 用户安装时自动获取最新版本

#### 开发环境 (requirements-dev.txt 或 .dev-requirements)

```txt
# .dev-requirements - 包含本地路径
-e ../../../engine-utils/ovos-utils
-e ../../ovos-config
```

**用途**：
- 由 `install-dev.py` 读取和处理
- 不被 setuptools 直接解析
- 允许本地开发覆盖 PyPI 版本

### 3. 关键技术：--no-build-isolation

```bash
pip install --no-build-isolation -e ./engine-core/ovos-core
```

这个标志的作用：
- 允许在 build 时访问已安装的包
- 绕过 setuptools 的隔离机制
- 允许动态解析本地依赖

### 4. 智能安装脚本 (install-dev.py)

```python
#!/usr/bin/env python3
"""
The master installer that understands the entire dependency graph
"""

def extract_local_deps(setup_py_path):
    """从 setup.py 中提取 comments 里的本地依赖"""
    # 解析注释掉的 -e 路径
    # 例如: # -e ../../../engine-utils/ovos-utils
    pass

def extract_from_dev_requirements(pkg_dir):
    """从 requirements-dev.txt 中提取本地依赖"""
    pass

def resolve_dependency_order(all_packages):
    """
    解析依赖图，按正确顺序安装
    例如：utils → config → messagebus → core
    """
    pass

def install_with_local_overrides(pkg_path, local_deps):
    """
    安装包，但先确保所有本地依赖已安装
    使用 --no-build-isolation 绕过 setuptools 限制
    """
    pass
```

## OVOS 应该采用的方案

### 方案 1：改进型（推荐）

**修改 install-dev.py，使其自动检测本地依赖**：

```python
#!/usr/bin/env python3
import re
from pathlib import Path

def extract_commented_local_deps(setup_py_path):
    """从 setup.py 中的注释里提取本地依赖"""
    with open(setup_py_path) as f:
        content = f.read()
    
    # 查找注释掉的 -e 行
    # 例如: # -e ../../../engine-utils/ovos-utils
    pattern = r'#\s*-e\s+([^\s]+)'
    matches = re.findall(pattern, content)
    return matches

# 更新 INSTALL_ORDER
# 或者自动从所有 setup.py 中检测
```

### 方案 2：标准化型（业界最佳实践）

每个包都有 `requirements-dev.txt`：

```
# engine-core/ovos-messagebus/requirements-dev.txt
-e ../../../engine-utils/ovos-utils
-e ../../ovos-config
```

install-dev.py 读取这些文件：

```python
def discover_packages_and_deps():
    """自动发现所有包和它们的本地依赖"""
    packages = []
    for setup_py in Path(engine_dir).rglob('setup.py'):
        if 'test' in str(setup_py):
            continue
        
        pkg_dir = setup_py.parent
        dev_reqs = pkg_dir / 'requirements-dev.txt'
        
        local_deps = []
        if dev_reqs.exists():
            with open(dev_reqs) as f:
                for line in f:
                    if line.startswith('-e '):
                        local_deps.append(line.strip())
        
        packages.append({
            'path': pkg_dir,
            'name': setup_py.parent.name,
            'local_deps': local_deps
        })
    
    return topologically_sort(packages)
```

### 方案 3：更激进型（完全 monorepo 风格）

使用 `pyproject.toml` 的 `[tool.poetry.path-dependencies]`：

```toml
# engine-core/ovos-messagebus/pyproject.toml
[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.26"
ovos-utils = { path = "../../../engine-utils/ovos-utils" }
ovos-config = { path = "../../ovos-config" }
```

然后统一使用 poetry：

```bash
cd engine
poetry install  # 自动处理所有本地路径
```

## 对于有几百个库的系统怎么办？

### 1. **分层克隆策略**

```bash
# 只克隆 core
git clone https://github.com/openvoiceos/ovos-core.git
cd ovos-core
python install-dev.py  # 只安装 core

# 需要技能时再克隆
git clone https://github.com/openvoiceos/ovos-skill-weather.git skills/weather
pip install -e skills/weather  # 即时生效
```

### 2. **工作空间管理**

创建 `workspace.json` 或 `projects.yaml`：

```yaml
projects:
  core:
    - engine-utils/ovos-utils
    - engine-core/ovos-config
    - engine-core/ovos-core
  
  audio:
    - engine-plugins/ovos-audio-plugin-*
  
  skills:
    - engine-skills/ovos-skill-*
```

然后：

```bash
# 安装整个 core
ovos install-workspace core

# 安装特定技能
ovos install-workspace skills:weather,news

# 开发特定模块时
cd engine-skills/ovos-skill-weather
pip install -e .
```

### 3. **CI/CD 分离**

- **开发阶段**：使用本地 `-e` 安装，快速迭代
- **测试阶段**：使用 PyPI 版本进行集成测试
- **发布阶段**：自动发布到 PyPI

```bash
# .github/workflows/dev.yml
- name: Install development environment
  run: python engine/install-dev.py

# .github/workflows/test.yml  
- name: Install from PyPI
  run: pip install ovos-core
  
# .github/workflows/publish.yml
- name: Publish to PyPI
  run: python -m build && twine upload dist/*
```

## 实现建议

对于你的 norapy-dev 项目，我建议：

### 步骤 1：为每个核心包添加 requirements-dev.txt

```bash
# engine-core/ovos-messagebus/requirements-dev.txt
-e ../../../engine-utils/ovos-utils
-e ../../ovos-config

# engine-core/ovos-core/requirements-dev.txt
-e ../../../engine-utils/ovos-utils
-e ../../ovos-config
-e ../../ovos-messagebus
-e ../../ovos-workshop
```

### 步骤 2：改进 install-dev.py

```python
def discover_and_install():
    """自动发现和安装所有本地包"""
    
    # 硬编码的核心包顺序（防止循环依赖）
    core_packages = [
        "./engine-utils/ovos-utils",
        "./engine-core/ovos-config",
        "./engine-core/ovos-plugin-manager",
        "./engine-core/ovos-workshop",
        "./engine-core/ovos-messagebus",
        "./engine-core/ovos-core",
    ]
    
    # 可选：扫描和安装其他包
    for pkg in discover_packages_in_engine():
        if pkg not in core_packages:
            install_if_requested(pkg)
```

### 步骤 3：文档化开发流程

```markdown
## 快速开发指南

### 开发单个技能
```bash
cd engine-skills/ovos-skill-weather
pip install -e .  # 立即生效
```

### 修改 core 代码
```bash
# 代码改动在 engine-core/ovos-core/ 中
# 自动生效（因为使用了 -e 安装）
```

### 发布新版本
```bash
cd engine-core/ovos-core
# 1. 更新 version.py
# 2. git commit && git push
# 3. GitHub Actions 自动测试和发布到 PyPI
```
```

## 总结

| 维度 | 生产环境 | 开发环境 |
|-----|--------|--------|
| **Requirements** | requirements.txt (仅 PyPI) | requirements-dev.txt (本地 + PyPI) |
| **安装命令** | `pip install ovos-core` | `python install-dev.py` |
| **Build Isolation** | 启用（默认） | 禁用 (`--no-build-isolation`) |
| **代码改动** | 不生效，需要重新安装 | 立即生效 (pip -e) |
| **Pip 版本** | 固定在 PyPI | 本地版本覆盖 PyPI |
| **速度** | 中等（下载 wheels） | 快速（已安装）|

这就是业界标准，也是大型 monorepo 系统（如 Babel, React, TypeScript 等）采用的方案。

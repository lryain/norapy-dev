import os
import re

def build_package_mapping(root_dir):
    package_to_subdir = {}
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path) and subdir.startswith('engine-'):
            for item in os.listdir(subdir_path):
                item_path = os.path.join(subdir_path, item)
                if os.path.isdir(item_path) and (item.startswith('ovos-') or item.startswith('ovos_')):
                    package_to_subdir[item] = subdir
    return package_to_subdir

def get_relative_path(current_subdir, target_subdir, target_package):
    if current_subdir == target_subdir:
        return f'../../{target_package}'
    else:
        return f'../../../{target_subdir}/{target_package}'

def update_requirements(root_dir):
    package_to_subdir = build_package_mapping(root_dir)
    print("Package mapping:", package_to_subdir)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == 'requirements':
            req_dir = dirpath
            # Get current subdir
            parts = req_dir.split(os.sep)
            try:
                engine_index = parts.index('engine')
                current_subdir = parts[engine_index + 1]
            except (ValueError, IndexError):
                continue
            for filename in os.listdir(req_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(req_dir, filename)
                    print(f"Processing {filepath}")
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    new_lines = []
                    changed = False
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith('-e ../') or stripped.startswith('-e ../../'):
                            # Extract the path after -e 
                            match = re.match(r'-e\s+(.+)', stripped)
                            if match:
                                path = match.group(1)
                                # Check if it's ovos- or ovos_
                                if path.startswith('../') or path.startswith('../../'):
                                    # Extract the package name
                                    parts = path.split('/')
                                    if len(parts) >= 2:
                                        package_part = parts[-1]
                                        # Handle [extras] syntax
                                        if '[' in package_part and package_part.endswith(']'):
                                            base_package = package_part.split('[')[0]
                                        else:
                                            base_package = package_part
                                        
                                        if base_package.startswith('ovos-') or base_package.startswith('ovos_'):
                                            ovos_name = base_package.replace('_', '-')
                                            if ovos_name in package_to_subdir:
                                                target_subdir = package_to_subdir[ovos_name]
                                                # Preserve [extras] syntax in the new path
                                                extras_suffix = '[extras]' if '[' in package_part and package_part.endswith(']') else ''
                                                rel_path = get_relative_path(current_subdir, target_subdir, ovos_name) + extras_suffix
                                                new_line = f'-e {rel_path}\n'
                                                new_lines.append(new_line)
                                                if new_line != line:
                                                    changed = True
                                                print(f"  Updated path: {stripped} -> -e {rel_path}")
                                            else:
                                                new_lines.append(line)
                                        else:
                                            new_lines.append(line)
                                else:
                                    new_lines.append(line)
                            else:
                                new_lines.append(line)
                        elif stripped.startswith('ovos-') or stripped.startswith('ovos_'):
                            # Original logic for non-editable
                            match = re.match(r'(ovos[-_][^>=<\s]+)', stripped)
                            if match:
                                ovos_name = match.group(1)
                                if ovos_name in package_to_subdir:
                                    target_subdir = package_to_subdir[ovos_name]
                                    rel_path = get_relative_path(current_subdir, target_subdir, ovos_name)
                                    new_line = f'-e {rel_path}\n'
                                    new_lines.append(new_line)
                                    if new_line != line:
                                        changed = True
                                    print(f"  Updated path: {stripped} -> -e {rel_path}")
                                else:
                                    # Try alternative names
                                    alt_names = [
                                        ovos_name.replace('-plugin-', '-server-'),
                                        ovos_name.replace('-server-', '-plugin-'),
                                        ovos_name.replace('_plugin_', '_server_'),
                                        ovos_name.replace('_server_', '_plugin_'),
                                    ]
                                    for alt in alt_names:
                                        if alt in package_to_subdir:
                                            target_subdir = package_to_subdir[alt]
                                            rel_path = get_relative_path(current_subdir, target_subdir, alt)
                                            new_line = f'-e {rel_path}\n'
                                            new_lines.append(new_line)
                                            if new_line != line:
                                                changed = True
                                            print(f"  Updated path (alt): {stripped} -> -e {rel_path}")
                                            break
                                    else:
                                        new_lines.append(line)
                                        print(f"  Skipped: {ovos_name} not in mapping")
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    if changed:
                        with open(filepath, 'w') as f:
                            f.writelines(new_lines)
                        print(f"  Updated {filepath}")

if __name__ == '__main__':
    update_requirements('/home/pi/dev/norapy-dev/engine')
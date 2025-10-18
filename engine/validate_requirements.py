import os
import re
from collections import defaultdict

def validate_requirements(root_dir, output_file='validation_errors.txt'):
    errors = []
    missing_packages = defaultdict(list)  # package_name -> list of (filepath, line_num, path)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == 'requirements':
            req_dir = dirpath
            for filename in os.listdir(req_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(req_dir, filename)
                    print(f"Validating {filepath}")
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith('-e '):
                            match = re.match(r'-e\s+(.+)', stripped)
                            if match:
                                path = match.group(1)
                                
                                # Handle [extras] syntax - check base package path
                                if '[' in path and path.endswith(']'):
                                    # Extract base path without extras
                                    base_path = path.split('[')[0]
                                    abs_path = os.path.abspath(os.path.join(req_dir, base_path))
                                    check_path = base_path
                                else:
                                    abs_path = os.path.abspath(os.path.join(req_dir, path))
                                    check_path = path
                                
                                if not os.path.exists(abs_path):
                                    error_msg = f"{filepath}:{line_num}: Path {check_path} does not exist (abs: {abs_path})"
                                    errors.append(error_msg)
                                    
                                    # Extract package name from path
                                    if '/' in check_path:
                                        package_name = check_path.split('/')[-1]
                                    else:
                                        package_name = check_path
                                    
                                    # Skip backup files with ~ suffix
                                    if not package_name.endswith('~'):
                                        missing_packages[package_name].append((filepath, line_num, check_path))
                                else:
                                    print(f"  OK: {check_path}")
    
    # Write detailed errors to file
    with open(output_file, 'w') as f:
        f.write("OVOS Requirements Validation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated on: {os.popen('date').read().strip()}\n\n")
        
        if errors:
            f.write("DETAILED ERRORS:\n")
            f.write("-" * 20 + "\n")
            for error in errors:
                f.write(f"{error}\n")
            f.write("\n")
            
            # Add statistics to file
            f.write("STATISTICS SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total errors: {len(errors)}\n")
            
            # Statistics by file
            errors_by_file = defaultdict(int)
            for error in errors:
                filepath = error.split(':')[0]
                errors_by_file[filepath] += 1
            
            f.write(f"Files with errors: {len(errors_by_file)}\n")
            f.write("Top 10 files by error count:\n")
            sorted_files = sorted(errors_by_file.items(), key=lambda x: x[1], reverse=True)
            for filepath, count in sorted_files[:10]:
                f.write(f"  - {filepath}: {count} errors\n")
            f.write("\n")
            
            # Statistics by subdirectory
            errors_by_subdir = defaultdict(int)
            for filepath in errors_by_file.keys():
                parts = filepath.split('/')
                if 'engine-' in filepath:
                    engine_index = next((i for i, part in enumerate(parts) if part.startswith('engine-')), -1)
                    if engine_index >= 0 and engine_index + 1 < len(parts):
                        subdir = parts[engine_index + 1]
                        errors_by_subdir[subdir] += errors_by_file[filepath]
            
            f.write("Errors by subdirectory:\n")
            for subdir in sorted(errors_by_subdir.keys()):
                count = errors_by_subdir[subdir]
                percentage = (count / len(errors)) * 100
                f.write(f"  - {subdir}: {count} errors ({percentage:.1f}%)\n")
            f.write("\n")
            
            f.write("MISSING PACKAGES SUMMARY:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Total missing packages: {len(missing_packages)}\n\n")
            
            for package, locations in sorted(missing_packages.items()):
                f.write(f"Package: {package}\n")
                f.write(f"  Referenced in {len(locations)} location(s):\n")
                for filepath, line_num, path in locations:
                    f.write(f"    - {filepath}:{line_num} ({path})\n")
                f.write("\n")
        else:
            f.write("All paths are valid! No errors found.\n")
    
    # Console output
    print(f"\nValidation complete. Results written to {output_file}")
    
    if errors:
        # Statistics by file
        errors_by_file = defaultdict(int)
        for error in errors:
            filepath = error.split(':')[0]
            errors_by_file[filepath] += 1
        
        # Statistics by subdirectory
        errors_by_subdir = defaultdict(int)
        for filepath in errors_by_file.keys():
            parts = filepath.split('/')
            if 'engine-' in filepath:
                engine_index = next((i for i, part in enumerate(parts) if part.startswith('engine-')), -1)
                if engine_index >= 0 and engine_index + 1 < len(parts):
                    subdir = parts[engine_index + 1]
                    errors_by_subdir[subdir] += errors_by_file[filepath]
        
        # Statistics by error type (backup files vs missing packages)
        backup_errors = sum(1 for error in errors if '~' in error)
        missing_package_errors = len(errors) - backup_errors
        
        print(f"\n{'='*60}")
        print("VALIDATION STATISTICS SUMMARY")
        print(f"{'='*60}")
        print(f"Total errors: {len(errors)}")
        print(f"  - Backup file errors: {backup_errors}")
        print(f"  - Missing package errors: {missing_package_errors}")
        print(f"Unique missing packages: {len(missing_packages)}")
        print()
        
        print("Errors by subdirectory:")
        for subdir in sorted(errors_by_subdir.keys()):
            count = errors_by_subdir[subdir]
            percentage = (count / len(errors)) * 100
            print(f"  - {subdir}: {count} errors ({percentage:.1f}%)")
        print()
        
        print("Top 10 files with most errors:")
        sorted_files = sorted(errors_by_file.items(), key=lambda x: x[1], reverse=True)
        for filepath, count in sorted_files[:10]:
            print(f"  - {filepath}: {count} errors")
        print()
        
        print("Missing packages by reference count:")
        ref_counts = defaultdict(int)
        for package, locations in missing_packages.items():
            ref_counts[len(locations)] += 1
        
        for ref_count in sorted(ref_counts.keys(), reverse=True):
            packages_with_this_count = [pkg for pkg, locs in missing_packages.items() if len(locs) == ref_count]
            print(f"  - {ref_count} reference(s): {len(packages_with_this_count)} package(s)")
            if ref_count <= 3:  # Show details for packages with few references
                for pkg in sorted(packages_with_this_count):
                    print(f"    * {pkg}")
        
        print(f"\nDetailed report saved to {output_file}")
    else:
        print("\nAll paths are valid!")
        return True

if __name__ == '__main__':
    validate_requirements('/home/pi/dev/norapy-dev/engine', 'validation_errors.txt')
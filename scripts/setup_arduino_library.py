# 
# Creates/Updates the Arduino library from the original source code
#
import os
import shutil
import subprocess

def copy_files(src, dest, exts=None, recursive=True):
    """Copy files from src to dest. If exts is set, only copy files with those extensions. If recursive, copy subdirs."""
    if not os.path.exists(src):
        print(f"Source directory {src} does not exist.")
        return
    if not os.path.exists(dest):
        os.makedirs(dest)
    if recursive:
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            target_dir = os.path.join(dest, rel_path) if rel_path != '.' else dest
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            for file in files:
                if exts is None or any(file.endswith(ext) for ext in exts):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    shutil.copy2(src_file, dst_file)
        print(f"Copied files from {src} to {dest} (recursive, filter={exts})")
    else:
        for file in os.listdir(src):
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dest, file)
            if os.path.isfile(src_file) and (exts is None or any(file.endswith(ext) for ext in exts)):
                shutil.copy2(src_file, dst_file)
        print(f"Copied files from {src} to {dest} (no subdirectories, filter={exts})")


def patch_include_after_guard(input_dir, filename, include_line):
    """Patch the given header file in input_dir to add include_line after the include guard."""
    file_path = os.path.join(input_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if any(include_line in line for line in lines):
            return
        # Find the include guard (first #define after #ifndef)
        guard_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('#ifndef'):
                # Look for next #define
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip().startswith('#define'):
                        guard_idx = j
                        break
                break
        insert_idx = guard_idx + 1 if guard_idx is not None else 0
        lines.insert(insert_idx, include_line + '\n')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Patched {file_path} to add {include_line} after include guard")

def setup_opus():
    # Source directory for includes
    include_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/include'))
    # Destination directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dest_dir = os.path.join(project_root, 'src', 'opus')

    # Ensure dest_dir exists before any file operations
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Source directory for includes
    include_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/include'))
    # Destination directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dest_dir = os.path.join(project_root, 'src', 'opus')


    # Copy only .h files from include_src to dest_dir
    copy_files(include_src, dest_dir, exts=['.h'], recursive=True)
    print("Copy complete.")

    # Copy all files from original/opus/celt to src/opus/celt (no subdirectories)
    celt_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/celt'))
    celt_dest = os.path.join(dest_dir, 'celt')
    copy_files(celt_src, celt_dest, exts=None, recursive=False)

    # Copy all files from original/opus/silk to src/opus/silk (no subdirectories)
    silk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/silk'))
    silk_dest = os.path.join(dest_dir, 'silk')
    copy_files(silk_src, silk_dest, exts=None, recursive=False)

    # Copy all files from original/opus/silk/fixed to src/opus/silk/fixed (no subdirectories)
    silk_fixed_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/silk/fixed'))
    silk_fixed_dest = os.path.join(dest_dir, 'silk', 'fixed')
    copy_files(silk_fixed_src, silk_fixed_dest, exts=None, recursive=False)

    # Copy all .h and .c files from original/opus/src to src/opus
    src_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/src'))
    copy_files(src_src, dest_dir, exts=['.h', '.c'], recursive=True)

    # Replace all '#ifdef HAVE_CONFIG_H' with '#if defined(HAVE_CONFIG_H) || defined(ARDUINO)' in all .c and .h files under src/opus
    for root, dirs, files in os.walk(dest_dir):
        for fname in files:
            if fname.endswith('.c') or fname.endswith('.h'):
                file_path = os.path.join(root, fname)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                new_content = content.replace('#ifdef HAVE_CONFIG_H', '#if defined(HAVE_CONFIG_H) || defined(ARDUINO)')
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Patched HAVE_CONFIG_H in {file_path}")

    patch_include_after_guard(os.path.join(dest_dir, 'celt'), 'kiss_fft.h', '#include "opus/config.h"')
    patch_include_after_guard(os.path.join(dest_dir, 'silk'), 'SigProc_FIX.h', '#include "opus/config.h"')
    patch_include_after_guard(os.path.join(dest_dir), 'opus_types.h', '#include "opus/config.h"')


def patch_includes(dest_dir):
    """Patch #include statements in .c and .h files in dest_dir."""
    # Build a map of all .h file locations (filename -> relative path from src)
    header_locations = {}
    src_root = os.path.dirname(dest_dir)
    for root, dirs, files in os.walk(src_root):
        for file in files:
            if file.endswith('.h'):
                rel_dir = os.path.relpath(root, src_root)
                rel_path = os.path.join(rel_dir, file) if rel_dir != '.' else file
                header_locations[file] = rel_path.replace('\\', '/')

    # Patch all .c and .h files recursively in dest_dir
    for root, dirs, files in os.walk(dest_dir):
        for fname in files:
            if fname.endswith('.c') or fname.endswith('.h'):
                file_path = os.path.join(root, fname)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                new_lines = []
                changed = False
                for line in lines:
                    # Patch #include "config.h" to #include "opus/config.h"
                    if 'include "config.h"' in line:
                        line = line.replace('"config.h"', '"opus/config.h"')
                        changed = True
                    elif line.strip().startswith('#include "'):
                        start = line.find('"') + 1
                        end = line.find('"', start)
                        inc_file = line[start:end]
                        inc_base = os.path.basename(inc_file)
                        # Check if inc_file is in the same directory as the including file
                        inc_path = os.path.join(root, inc_file)
                        if os.path.exists(inc_path):
                            # File exists in current directory, do not patch
                            pass
                        elif inc_base in header_locations:
                            # Always use path from project root (src/opus)
                            new_path = header_locations[inc_base]
                            if inc_file != new_path:
                                line = line.replace(inc_file, new_path)
                                changed = True
                    new_lines.append(line)
                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)

# Cleanup: delete specified files
def cleanup():
    files_to_delete = [
        os.path.join(project_root, 'src', 'opus', 'opus_demo.c'),
        os.path.join(project_root, 'src', 'opus', 'opus_compare.c'),
        os.path.join(project_root, 'src', 'opus', 'test_opus_custom.c'),
        os.path.join(project_root, 'src', 'opus', 'test_opus.c'),
        os.path.join(project_root, 'src', 'opus', 'test_repacketizer.c'),
    ]
    for f in files_to_delete:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted {f}")
        else:
            print(f"File not found for deletion: {f}")

if __name__ == "__main__":

    setup_opus()
    # Patch includes for opus 
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    patch_includes(os.path.join(project_root, 'src', 'opus'))

    cleanup()

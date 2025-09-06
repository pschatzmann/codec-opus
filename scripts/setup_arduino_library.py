# 
# Creates/Updates the Arduino library from the original source code
#
import os
import shutil
import subprocess

def copy_files(src, dest, exts=None, recursive=True, exclude_files=None):
    """Copy files from src to dest. If exts is set, only copy files with those extensions. 
    If recursive, copy subdirs. If exclude_files is set, skip those files."""
    if not os.path.exists(src):
        print(f"Source directory {src} does not exist.")
        return
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    if exclude_files is None:
        exclude_files = set()
    else:
        exclude_files = set(exclude_files)
    
    if recursive:
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            target_dir = os.path.join(dest, rel_path) if rel_path != '.' else dest
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            for file in files:
                if file in exclude_files:
                    print(f"Skipping excluded file: {file}")
                    continue
                if exts is None or any(file.endswith(ext) for ext in exts):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    shutil.copy2(src_file, dst_file)
        print(f"Copied files from {src} to {dest} (recursive, filter={exts}, excluded={len(exclude_files)} files)")
    else:
        for file in os.listdir(src):
            if file in exclude_files:
                print(f"Skipping excluded file: {file}")
                continue
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dest, file)
            if os.path.isfile(src_file) and (exts is None or any(file.endswith(ext) for ext in exts)):
                shutil.copy2(src_file, dst_file)
        print(f"Copied files from {src} to {dest} (no subdirectories, filter={exts}, excluded={len(exclude_files)} files)")


def copy_config_file(dest_dir):
    """Copy config.h from scripts/input to src/opus directory."""
    config_src = os.path.abspath(os.path.join(os.path.dirname(__file__), 'input/config.h'))
    config_dest = os.path.join(dest_dir, 'config.h')
    if os.path.exists(config_src):
        shutil.copy2(config_src, config_dest)
        print(f"Copied config.h from {config_src} to {config_dest}")
    else:
        print(f"Warning: config.h not found at {config_src}")


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

    # Define files to exclude during copy
    demo_and_test_files = {
        'opus_demo.c', 'opus_compare.c', 'test_opus_custom.c', 'test_opus.c', 
        'test_repacketizer.c', 'opus_custom_demo.c', 'repacketizer_demo.c', 'mlp_train.c'
    }
    
    # Silk duplicate files (keep original names without silk_ prefix)
    silk_duplicates = {
        'silk_A2NLSF.c', 'silk_CNG.c', 'silk_HP_variable_cutoff.c',
        'silk_LPC_analysis_filter.c', 'silk_LP_variable_cutoff.c', 'silk_NLSF2A.c',
        'silk_NLSF_VQ.c', 'silk_NLSF_VQ_weights_laroia.c', 'silk_NLSF_decode.c',
        'silk_NLSF_del_dec_quant.c', 'silk_NLSF_encode.c', 'silk_NLSF_stabilize.c',
        'silk_NLSF_unpack.c', 'silk_PLC.c', 'silk_VAD.c', 'silk_ana_filt_bank_1.c',
        'silk_bwexpander.c', 'silk_bwexpander_32.c', 'silk_check_control_input.c',
        'silk_code_signs.c', 'silk_control_SNR.c', 'silk_control_audio_bandwidth.c',
        'silk_control_codec.c', 'silk_create_init_destroy.c', 'silk_dec_API.c',
        'silk_decode_core.c', 'silk_decode_frame.c', 'silk_decode_indices.c',
        'silk_decode_parameters.c', 'silk_decode_pitch.c', 'silk_decode_pulses.c',
        'silk_decoder_set_fs.c', 'silk_enc_API.c', 'silk_encode_indices.c',
        'silk_encode_pulses.c', 'silk_gain_quant.c', 'silk_init_encoder.c',
        'silk_interpolate.c', 'silk_lin2log.c', 'silk_log2lin.c', 
        'silk_pitch_est_tables.c', 'silk_process_NLSFs.c', 'silk_quant_LTP_gains.c', 
        'silk_resampler.c', 'silk_resampler_down2.c', 'silk_resampler_down2_3.c', 
        'silk_resampler_private_AR2.c', 'silk_resampler_private_IIR_FIR.c', 
        'silk_resampler_private_down_FIR.c', 'silk_resampler_private_up2_HQ.c', 
        'silk_resampler_rom.c', 'silk_shell_coder.c', 'silk_sigm_Q15.c', 'silk_sort.c',
        'silk_stereo_LR_to_MS.c', 'silk_stereo_MS_to_LR.c', 'silk_stereo_decode_pred.c',
        'silk_stereo_encode_pred.c', 'silk_stereo_find_predictor.c',
        'silk_stereo_quant_pred.c', 'silk_sum_sqr_shift.c', 'silk_table_LSF_cos.c',
        'silk_tables_LTP.c', 'silk_tables_NLSF_CB_NB_MB.c', 'silk_tables_NLSF_CB_WB.c',
        'silk_tables_gain.c', 'silk_tables_other.c', 'silk_tables_pitch_lag.c',
        'silk_tables_pulses_per_block.c'
    }
    
    # Floating-point versions that conflict with fixed-point implementations
    float_conflicts = {
        'silk_apply_sine_window.c', 'silk_autocorr.c', 'silk_k2a.c',
        'silk_k2a_Q16.c', 'silk_pitch_analysis_core.c', 'silk_scale_copy_vector16.c',
        'silk_scale_vector.c', 'silk_schur.c', 'silk_schur64.c', 'silk_inner_prod_aligned.c'
    }
    
    # Fixed-point silk duplicates
    fixed_duplicates = {
        'silk_LTP_analysis_filter_FIX.c', 'silk_LTP_scale_ctrl_FIX.c',
        'silk_corrMatrix_FIX.c', 'silk_encode_frame_FIX.c', 'silk_find_LPC_FIX.c',
        'silk_find_LTP_FIX.c', 'silk_find_pitch_lags_FIX.c', 'silk_find_pred_coefs_FIX.c',
        'silk_noise_shape_analysis_FIX.c', 'silk_process_gains_FIX.c',
        'silk_regularize_correlations_FIX.c', 'silk_residual_energy16_FIX.c',
        'silk_residual_energy_FIX.c'
    }

    # Copy only .h files from include_src to dest_dir
    copy_files(include_src, dest_dir, exts=['.h'], recursive=True)
    print("Copy complete.")

    # Copy all files from original/opus/celt to src/opus/celt (no subdirectories)
    celt_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/celt'))
    celt_dest = os.path.join(dest_dir, 'celt')
    copy_files(celt_src, celt_dest, exts=None, recursive=False, exclude_files=demo_and_test_files)

    # Copy all files from original/opus/silk to src/opus/silk (no subdirectories)
    silk_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/silk'))
    silk_dest = os.path.join(dest_dir, 'silk')
    silk_excludes = silk_duplicates | float_conflicts
    copy_files(silk_src, silk_dest, exts=None, recursive=False, exclude_files=silk_excludes)

    # Copy all files from original/opus/silk/fixed to src/opus/silk/fixed (no subdirectories)
    silk_fixed_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/silk/fixed'))
    silk_fixed_dest = os.path.join(dest_dir, 'silk', 'fixed')
    copy_files(silk_fixed_src, silk_fixed_dest, exts=None, recursive=False, exclude_files=fixed_duplicates)

    # Copy all .h and .c files from original/opus/src to src/opus
    src_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '../original/opus/src'))
    copy_files(src_src, dest_dir, exts=['.h', '.c'], recursive=True, exclude_files=demo_and_test_files)

    # Copy config.h from scripts/input to src/opus
    copy_config_file(dest_dir)

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

# Cleanup: delete any remaining problematic files that might have been missed
def cleanup():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Just in case any of these files were copied despite exclusions, remove them
    potentially_remaining_files = [
        os.path.join(project_root, 'src', 'opus', 'opus_demo.c'),
        os.path.join(project_root, 'src', 'opus', 'opus_compare.c'),
        os.path.join(project_root, 'src', 'opus', 'test_opus_custom.c'),
        os.path.join(project_root, 'src', 'opus', 'test_opus.c'),
        os.path.join(project_root, 'src', 'opus', 'test_repacketizer.c'),
        os.path.join(project_root, 'src', 'opus','celt', 'opus_custom_demo.c'),
        os.path.join(project_root, 'src', 'opus', 'repacketizer_demo.c'),
        os.path.join(project_root, 'src', 'opus', 'mlp_train.c'),
    ]
    
    removed_count = 0
    for f in potentially_remaining_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted remaining file: {f}")
            removed_count += 1
    
    if removed_count == 0:
        print("No remaining problematic files found - exclusion during copy worked correctly!")
    else:
        print(f"Removed {removed_count} files that were missed during exclusion")

if __name__ == "__main__":

    setup_opus()
    # Patch includes for opus 
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    patch_includes(os.path.join(project_root, 'src', 'opus'))

    cleanup()

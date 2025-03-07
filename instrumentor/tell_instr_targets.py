#!/usr/bin/python3
import os
import re
import argparse
import json
import re

RES_FILE_NAME = 'instr-targets.json'
SUMMARY_FILE_NAME = 'targets-summary.txt'

# Traverse all code files and locate the targets labeled with:
# // INSTRUMENT_BB and // INSTRUMENT_FUNC

def search_content(regex, str):
    match = re.findall(regex, str, re.M)
    if len(match) > 0:
        return True
    return False

def tell_specified_blocks(code_path, res_path):
    total_file = 0
    total_target_file = 0
    total_targets = 0
    targets = []
    for root, dirs, files in os.walk(code_path):
        for file in files:
            # store located target lines in a set
            target_bb_set = set()
            target_func_set = set()
            target_const_dict = dict()
            target_bb_set.clear()
            target_func_set.clear()
            target_const_dict.clear()
            
            # if having targets pending, search for the next code line 
            is_pending_bb = False 
            is_pending_func = False
            is_pending_const = False
            const_value = None
            
            # get code path
            absolute_filename = os.path.join(root, file)
            real_path = os.path.abspath(absolute_filename)
            
            if file.endswith(('.cpp', '.c', '.cc', '.h', '.hh', '.hpp', '.rs')): 
                with open(real_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # record current code line
                    line_num = 0
                    
                    total_file += 1
                    print(f"Scanning {real_path}: ")
                    
                    while True:
                        content = f.readline()
                        if not content:
                            if len(target_bb_set) > 0 or len(target_func_set) > 0 or len(target_const_dict):
                                total_target_file += 1
                                total_targets += len(target_bb_set)
                                total_targets += len(target_func_set)
                                targets.append({
                                    "path": real_path,
                                    "targets_bb": sorted(list(target_bb_set)),
                                    "targets_func": sorted(list(target_func_set)),
                                    "targets_const": target_const_dict
                                })

                            break
                        else:  
                            line_num += 1
                            
                            # For INSTRUMENT_BB/INSTRUMENT_FUNC, locate the following code line
                            if not is_pending_bb and not is_pending_func and not is_pending_const:
                                if search_content(r'INSTRUMENT_BB', content):
                                    is_pending_bb = True
                                elif search_content(r'INSTRUMENT_FUNC', content):
                                    is_pending_func = True
                                elif search_content(r'INSTRUMENT_CONST', content):
                                    match = re.search(r'INSTRUMENT_CONST:\s*"([^"]+)"', content)
                                    if match:
                                        is_pending_const = True
                                        const_value = match.group(1)

                            else:
                                new_content = content.lstrip()
                                is_target = search_content(r'^(([a-zA-z]{1}.*)|\})', new_content) # begin with letter or }
                                if is_target:
                                    if is_pending_bb:
                                        is_pending_bb = False
                                        target_bb_set.add(line_num)
                                        print(f"    locate block targets at line {line_num}")
                                    if is_pending_func:
                                        is_pending_func = False
                                        target_func_set.add(line_num)
                                        print(f"    locate function targets at line {line_num}")
                                    if is_pending_const and const_value:
                                        target_const_dict[line_num] = const_value
                                        print(f'    locate constant targets at line {line_num} with value {const_value}')
                                        is_pending_const = False
                                        const_value = None

    res_file = os.path.join(res_path, RES_FILE_NAME)
    with open(res_file, 'a+') as f:
        json.dump(targets, f, indent=4)
    
    print("================ SUMMARY OF ANALYSIS ================")
    print(f"1. scanned {total_file} files")
    print(f"2. {total_target_file} files contains {total_targets} targets in total")

    summary_file = os.path.join(res_path, SUMMARY_FILE_NAME)
    with open(summary_file, 'w') as f:
        f.write("================ SUMMARY OF ANALYSIS ================")
        f.write("\n")
        f.write(f"1. scanned {total_file} files")
        f.write("\n")
        f.write(f"2. {total_target_file} files contains {total_targets} targets in total")
        f.write("\n")
        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help='code path', type=str)
    parser.add_argument("--output", help='target path', type=str)
    args = parser.parse_args()
    if args.input and args.output:
        code_path = args.input
        res_path = args.output
    else:
        print("Usage: ")
        print(" python3 tell_basicblocks.py --input code_directory --output target_directory")
        exit(0)
    
    res_file = os.path.join(res_path, RES_FILE_NAME)
    if os.path.exists(res_file):
        print(f"!! Overwriting {res_file}!")
        os.remove(res_file)
    
    tell_specified_blocks(code_path, res_path)

import glob
import os
from pathlib import Path
import pandas as pd
import re

from constants import ALL_METHODS, PROJECTS_DIR

project_dict = {1: "scrimage", 2: "mltk", 3: "mallet", 4: "openaudible", 5: "freecol"}
method_dict = {1:["draw", "apply", "reorient", "readHeader", "scale", "summands", "fill", "points"],
                2:["computeBins", "split", "parse", "fitIntercept", "write", "parseDenseInstance", "getStats", "computeGradient"],
                3:["predict", "toString", "induceFeaturesFor", "InvertedIndex", "ensureCapacity", 
                    "plusEquals", "optimize", "improveClustering"],
                4:["find", "accept", "checkBook", "test", "reallyQuit", "urlGetArgs", "connect", "mergeItem"],
                5:["setColors", "initializeCaches", "readId", "getCost", 
                    "changeServerState", "drawRenderingTimeStrings", "updateUnitPath", "compareIds"]}

def is_method_header(body, index):
    stop_punc =["=", "!", "return ", "}", " enum "]

    line = body[index].lstrip()
    
    if "(" not in line:
        return False
    elif ")" not in line:
        index+=1
        while line.count("(") != line.count(")") and not any(p in line for p in stop_punc) and index < len(body):
            line += body[index].lstrip()                
            if "{" in line:
                line = line.split("{")[0] + "{"
                if line.count("(") != line.count(")"):
                    return False
            index+=1
    else:
        index+=1
    if ")," in line:
        return False
    if "{" not in line and ";" not in line:
        while "{" not in body[index] and ";" not in body[index]:
            if len(body[index].lstrip().rstrip()) > 0:
                return False
            index+=1
        stop_char = "{" if "{" in body[index] else ";"
        if body[index].lstrip().index(stop_char) != 0 and \
            any(p in  (line + body[index]).split(stop_char)[0].split(")")[-1] for p in
                list(stop_punc + [","])) and "throws" not in (line + body[index]).split(stop_char)[0].split(")")[-1]:
            return False
    else:
        stop_char = "{" if "{" in line else ";"
        if any(p in line.split(stop_char)[0].split(")")[-1] for p in
                list(stop_punc + [","])) and "throws" not in line.split(stop_char)[0].split(")")[-1]:
            return False
        line = line.split("{")[0]
    
    def is_candidate(line):
        if "." in line and "..." not in line and ("(" not in line or line.index(".") < line.index("(")):
            return False
        return (len([w for w in line.split("(")[0].split() if w[0].isupper()]) > 0 and "new " not in line) \
            or line.startswith(('private ', 'public ', 'protected ', 'static ', 'void ', 'int ',
                               'float ', 'string ', 'boolean ', 'byte ', 'char ',
                               'short ', 'long ', 'double ', 'default '))
    if is_candidate(line):
        if any(p in line for p in stop_punc):
            return False
        if "(" not in line:
            return False
        a = line.index("(")
        if ")" not in line:
            return False
        b = line.index(")")
        vars = line[a+1:b].replace("\n", " ")
        if len(vars) == 0:
            return True
        elif ',' in vars:
            while '<' in vars:
                open = vars.index('<')
                close = vars.index('>')
                uneven_brackets = vars[open+1:close].count('<') - vars[open+1:close].count('>')
                while uneven_brackets > 0:
                    close = vars[close+1:].index('>')+close+1
                    uneven_brackets-=1
                vars = vars[:open] + vars[close+1:]
            return ' ' in vars.split(',')[0]
        else:
            return ' ' in vars or "@Suppress" in vars
        
    return False

# FIX: Added a global cache to prevent os.walk from looping endlessly
file_path_cache = {}

def find_file(filename, directory, xpath):
    cache_key = (filename, directory, xpath)
    if cache_key in file_path_cache:
        return file_path_cache[cache_key]
        
    proj =[x for x in project_dict.values() if x in xpath] if isinstance(xpath, str) else[]
    trunc_xpath = xpath.split("]")[0].split(proj[0])[-1].rsplit("/", 1)[0] if len(proj) > 0 else ''
    for root, dirs, files in os.walk(directory):
        root_proj =[x for x in project_dict.values() if x in root]
        trunc_root = root.split(root_proj[0])[-1] if len(root_proj) > 0 else ''
        if filename in files and (trunc_root == trunc_xpath or len(trunc_xpath) == 0):
            file_path_cache[cache_key] = os.path.join(root, filename)
            return file_path_cache[cache_key]
            
    file_path_cache[cache_key] = None
    return None

def get_method(task, short_path, line_num, xpath):
    path = find_file(short_path, f"{PROJECTS_DIR}/{task}/", xpath)
    if path is None:
        path = find_file(short_path, f"{PROJECTS_DIR}/", xpath)
    if path is None:
        return ''
    # FIX: Added encoding fallback so Windows doesn't choke on special characters in Java files
    f = open(path, 'r', encoding='utf-8', errors='ignore')
    body = f.readlines()

    paren = [0]

    method_names = [""]
    method_start = False
    for index, line in enumerate(body[:line_num]):
        if len(method_names) > 1 and not method_start and paren[-1] == 0:
                method_names.pop()
                paren.pop()
        if ";" in line and method_start:
            method_start = False
        if line.lstrip().startswith("@"):
            i = line.index("@")
            while i < len(line) and line[i] != ' ':
                i+=1
            body[index] = line[i+1:]
            if len(body[index].rstrip()) == 0:
                if index == line_num-1 and is_method_header(body, index+1):
                    index+=1
            line = body[index]
        if is_method_header(body, index):
            if "}" in line:
                paren.append(0)
            elif "{" in line:
                paren.append(line.count("{"))
            else:
                paren.append(0)
                method_start = ";" not in line 
            i = index
            while line.count("(") != line.count(")"):
                if i+1 == len(body):
                    return False
                new_line = body[i+1]
                new_line = new_line.replace("\\\"", " ")
                line = line.rstrip() + " " + new_line.lstrip().rstrip()
                while line.count("\"") > 1: 
                    i0 = line.index("\"")
                    line = line[:i0] + line[line[i0+1:].index("\"")+i0+2:]
                i+=1

            method_name = line.split("(")[0].split()[-1] + line[line.index("("): line.index(")")+1]

            def remove_word(method_name, end_index):
                if method_name[end_index-1] == "(":
                 return method_name
                ind = end_index
                while ind >= 0 and method_name[ind] != " ":
                    ind-=1
                if ind < 0:
                    return method_name.split("(")[0] + "()"
                return method_name[0:ind] + method_name[end_index:]
            
            for i in range(0, method_name.count(",")):
                comma_index = method_name.replace(",", ".", i).find(",")
                method_name = remove_word(method_name, comma_index)
            method_names.append(remove_word(method_name, method_name.find(")")))
        else:
            if "{" in line:
                method_start = False
                paren[-1]+= line.count("{")
            if "}" in line:
                paren[-1]-= line.count("}")
    return method_names[-1]

def add_method_annotations(path, test=False):
    if "processed_" in path:
        return
    
    df = pd.read_csv(path)
    if len(df) > 0:
    
        cached_methods = {}

        def get_method_cached(id, task, file_path, line_num, xpath):
            if isinstance(xpath, str) and "thirdparty" in xpath:
                return ""
            if ".txt" in file_path or ".md" in file_path:
                return ""
                
            # FIX: Only run the heavy function once per unique file/line combo
            if file_path not in cached_methods:
                cached_methods[file_path] = {}
            if line_num not in cached_methods[file_path]:
                cached_methods[file_path][line_num] = get_method(task, file_path, line_num, xpath)

            # FIX: Removed the massive block of dead test-code that was slowing the script down
            return cached_methods[file_path][line_num]

        task = project_dict[int(path.split("/")[-1].split("_")[1][1:])]

        df['method_name'] = df.apply(lambda x: get_method_cached(path.split("/")[-1], task, x['fixation_target'], x['source_file_line'], x['xpath']), axis=1)
        fname = path.split("/")[-1]
        out_path = path.rsplit("/", 1)[0]
        Path(out_path + "/").mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path + "/processed_" + fname)

if __name__ == "__main__":
    for i in range (1, 6):
        for method in [m for m in ALL_METHODS if m in method_dict[i]]:
            # Windows path fix + live print statements
            fnames =[f.replace("\\", "/") for f in glob.glob(f"Processed Data/T{i}/P*/*{method}.csv")]
            for f in fnames:
                if "processed_" not in f:
                    print(f"Processing fast: {f}")
                    add_method_annotations(f)
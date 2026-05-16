from coverage_metrics import *
import glob
import os

from constants import VALID_CALLEE_METHODS, VALID_CALLER_METHODS

if __name__ == "__main__":
    # FIX: Automatically create the required output folders before saving
    for i in range(1, 6):
        os.makedirs(f"output/T{i}", exist_ok=True)

    for m in VALID_CALLEE_METHODS:
        method_name = m.split(":")[1].split("(")[0]
        # Force forward slashes
        fnames =[f.replace("\\", "/") for f in glob.glob(f"Processed Data/T*/P*/processed*{method_name}.csv")]
        calculate_coverage_metrics(fnames, m)

    for m in VALID_CALLER_METHODS:
        method_name = m.split(":")[1].split("(")[0]
        # Force forward slashes
        fnames =[f.replace("\\", "/") for f in glob.glob(f"Processed Data/T*/P*/processed*{method_name}.csv")]
        calculate_coverage_metrics(fnames, m, up=True)
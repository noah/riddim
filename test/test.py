import os
import fnmatch
def files_by_pattern(path,pattern):
    results = []
    for base, dirs, files in os.walk(path):
        matches = fnmatch.filter(files, pattern)
        results.extend(os.path.realpath(os.path.join(base, m)) for m in matches)
    return results

print files_by_pattern('.','*.py')

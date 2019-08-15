import os
import re

pattern = re.compile(
    r'tv_sec:\s([\d]+),\stv_nsec:\s(\d*)\s}\slink_utilization:\s(\d.\d+)\s'
    r'queue:\s(-?\d+)\scwnd:\s(\d+)\srtt:\s(\d+.\d+)'
)
build_dir = "build/"


def format_file(file_in, file_out):
    f_in = open(file_in, "r")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    if os.path.exists(file_out):
        os.remove(file_out)
    for x in f_in:
        matches = pattern.findall(x)
        i = 1
        for m in matches:
            for k in m:
                if i == 1:
                    open(file_out, 'a').write(str(k) + '.')
                    i += 1
                elif i == 2:
                    open(file_out, 'a').write(str(k).zfill(9) + '\t')
                    i += 1
                else:
                    open(file_out, 'a').write(str(k) + '\t')
            open(file_out, 'a').write('\n')
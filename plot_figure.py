import re, os

pattern = re.compile(
    r'tv_sec:\s([\d]+),\stv_nsec:\s(\d*)\s}\slink_utilization:\s(\d.\d+)\squeue:\s(\d+)\scwnd:\s(\d+)'
)

log_file = "/home/lam/Projects/sdccp/remote-generic/log_output.txt"

output_file = "format_log.txt"


def format_file(file_in, file_out):
    f_in = open(file_in, "r")
    os.remove(output_file)
    for x in f_in:
        matches = pattern.findall(x)
        i = 1
        for m in matches:
            for k in m:
                if i == 1:
                    open(file_out, 'a').write(str(k) + '.')
                    i += 1
                else:
                    open(file_out, 'a').write(str(k) + '\t')
            open(file_out, 'a').write('\n')


def plot_figure(f):
    pass


if __name__ == '__main__':
    format_file(log_file, output_file)

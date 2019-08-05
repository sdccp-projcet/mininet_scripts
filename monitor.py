from time import sleep, time
from subprocess import *
import re

default_dir = '.'


def monitor_qlen(interface, interval_sec=0.01, file_name='%s/qlen.txt' % default_dir):
    pat_queued = re.compile(r'backlog\s[^\s]+\s([\d]+)p')
    cmd = "tc -s qdisc show dev %s" % interface
    ret = []
    open(file_name, 'w').write('')
    while 1:
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.stdout.read()
        # Not quite right, but will do for now
        matches = pat_queued.findall(output)
        if matches and len(matches) > 1:
            ret.append(matches[1])
            t = "%f" % time()
            open(file_name, 'a').write(t + ',' + matches[1] + '\n')
        sleep(interval_sec)
    return

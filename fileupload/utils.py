import subprocess

def file_read_from_tail(fname, lines):
    proc = subprocess.Popen(['tail', str(-1*lines), fname], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join((s.decode('utf-8') for s in lines))

def chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

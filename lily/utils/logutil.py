import sys


def print_progress(progress, end):
    """
    Print a progress bar on a single line to monitor `progress` reaching `end`.

    Example output:
        Progress: [ =======                                  ]  280/1594
    """
    if isinstance(progress, int):
        progress = float(progress)

    text_before = 'Progress:'
    text_after = 'Done!'

    status = ''.ljust(len(text_after))
    if progress >= end:
        status = '%s\r\n' % text_after

    line_width = 70
    bar_size = (line_width - 7) - len(text_before) - len(status.rstrip('\r\n')) - (len(str(end)) * 2 + 1)
    blocks = int(round(bar_size * (progress / end)))
    text = "\r%(before)s [ %(bar)s ] %(progress)s/%(end)s %(status)s" % {
        'before': text_before,
        'bar': '=' * blocks + ' ' * (bar_size - blocks),
        'progress': str(int(round(progress))).rjust(len(str(end))),
        'end': end,
        'status': status
    }
    sys.stdout.write(text)
    sys.stdout.flush()

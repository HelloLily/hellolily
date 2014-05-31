from operator import itemgetter

from pympler.asizeof import asizeof
from django.template.defaultfilters import filesizeformat


def meminspect(variables, logger):
    write_func = 'write'
    if not hasattr(logger, 'write'):
        write_func = 'warning'
    getattr(logger, write_func)('*'*70)
    if write_func == 'write':
        getattr(logger, write_func)('\n')

    memsize_data = []
    for name, value in variables.items():
        memsize_data.append((name, type(value), asizeof(value)))

    # Output biggest variables by size (large -> small)
    memsize_data_sorted = reversed(sorted(memsize_data, key=itemgetter(2)))
    for name, vartype, size in memsize_data_sorted:
        getattr(logger, write_func)('%-35s %10s %-10s' % (name, filesizeformat(size), vartype))
        if write_func == 'write':
            getattr(logger, write_func)('\n')
    getattr(logger, write_func)('*'*70)
    if write_func == 'write':
        getattr(logger, write_func)('\n')

    del variables

#!/usr/bin/env python
import os

import sys
import math
import argparse
import numpy as np
import logging as log
from scipy.stats import rankdata, pearsonr

from status import Status

def parse(filename, comment='#'):
    with open(filename) as fid:
        status = Status('parse {}'.format(filename)).fid(fid).start()
        col_names = [c.lower() for c in fid.next().split()[1:]]
        row_names = []
        data = []

        for line in fid:
            status.log()
            if not line[0] == comment:
                tokens = line.split()
                row_names.append(tokens[0])
                data.append([float(d) for d in tokens[1:]])

        log.info('parsed {} is {} x {}'.format(filename, len(row_names), len(col_names)))
        status.stop()

    return row_names, col_names, np.array(data)


def align(common_col_names, col_names, data):
    n = len(col_names)
    i = dict((k, i) for i, k in enumerate(col_names))
    i = [i[k] for k in common_col_names]
    m = len(common_col_names)
    log.info('aligned {} of {} columns ({} removed)'.format(m, n, n - m))
    return data[:, i]


def prune(row_names, data):
    n = len(row_names)
    z = [(row_name, row) for row_name, row in zip(row_names, data) if np.any(row)]
    row_names, data = zip(*z)
    data = np.array(data)
    m = len(row_names)
    log.info('pruned {} of {} rows with all zeros ({} remaining)'.format(n - m, n, m))
    return row_names, data


def correlate(outfile, row_filename, col_filename=None, spearman=True, pvalue_threshold=None, rho_threshold=None):

    row_row_names, row_col_names, row_data = parse(row_filename)

    if col_filename is None:
        col_filename = row_filename

    symmetric = row_filename == col_filename

    if not symmetric:
        col_row_names, col_col_names, col_data = parse(col_filename)

        col_names = set(row_col_names).intersection(col_col_names)

        row_data = align(col_names, row_col_names, row_data)
        col_data = align(col_names, col_col_names, col_data)

        col_row_names, col_data = prune(col_row_names, col_data)
        ncols = len(col_row_names)

    row_row_names, row_data = prune(row_row_names, row_data)
    nrows = len(row_row_names)

    if symmetric:
        col_row_names, col_data, ncols = row_row_names, row_data, nrows

    if nrows == 0 or ncols == 0:
        return

    if spearman:
        status = Status('ranking for spearman correlation').start()
        row_data = np.array([rankdata(r) for r in row_data])
        col_data = row_data if symmetric else np.array([rankdata(c) for c in col_data])
        status.stop()

    if symmetric:
        def complete(r):
            return r * (r - 1) / 2 + r * (nrows - r)
    else:
        def complete(r):
            return r * ncols

    status = Status('writing ' + outfile).n(complete(nrows)).units('correlations').start()

    try:
        os.makedirs(os.path.dirname(outfile))
    except:
        pass

    with open(outfile, 'wt') as fid:
        for r in xrange(nrows):
            for c in xrange(r + 1 if symmetric else 0, ncols):
                (rho, pvalue) = pearsonr(row_data[r], col_data[c])
                if (rho_threshold is None or math.fabs(rho) > rho_threshold) and (pvalue_threshold is None or pvalue < pvalue_threshold):
                    fid.write('%s\t%s\t%0.3e\t%0.3e\n' % (row_row_names[r], col_row_names[c], rho, pvalue))
            status.log(complete(r))

    status.stop()


def main():
    try:
        parser = argparse.ArgumentParser(description='Parser')
        parser.add_argument('--rowfile', help='row file')
        parser.add_argument('--colfile', help='column file', default=None)
        parser.add_argument('--outfile', help='output file')
        parser.add_argument('--pearson', dest='spearman', help='use pearson correlation', action='store_false')
        parser.add_argument('--pvalue', help='p-value threshold', type=float, default=None)
        parser.add_argument('--rho', help='correlation (rho) threshold', type=float, default=None)
        parser.add_argument('--loglevel', help='set log level', default='info')
        parser.add_argument('--logfile', help='set log file', default=None)
        args = parser.parse_args()

        level = args.loglevel.upper()
        try:
            level = getattr(log, level)
        except AttributeError:
            level = log.INFO

        if args.logfile is not None:
            try:
                os.makedirs(os.path.dirname(args.logfile))
            except OSError:
                pass

        log.getLogger().handlers = []
        log.basicConfig(level=level, filename=args.logfile, format='%(asctime)s.%(msecs)d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        log.info('row file is %s', args.rowfile)
        log.info('column file is %s', args.colfile)
        log.info('output file is %s', args.outfile)
        log.info('spearman is %s', args.spearman)
        log.info('p-value threshold is %s', args.pvalue)
        log.info('rho threshold is %s', args.rho)
        log.info('log level is %s (%d)', args.loglevel, level)
        log.info('log file is %s', args.logfile)

        status = Status(name='correlator').start()
        correlate(args.outfile, args.rowfile, args.colfile, spearman=args.spearman, pvalue_threshold=args.pvalue, rho_threshold=args.rho)
        status.stop()

        return 0
    except KeyboardInterrupt:
        return 1
    except Exception, e:
        sys.stderr.write(repr(e) + '\n')
        sys.stderr.write('for help use --help\n')
        return 2


if __name__ == '__main__':
    sys.exit(main())

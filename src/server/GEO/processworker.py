__author__ = 'guorongxu'

import sys
import correlator


if __name__ == "__main__":
    row_filename = sys.argv[1]
    col_filename = sys.argv[1]

    print "The input file name: " + row_filename

    outfile = row_filename.replace(".txt", ".cor")
    correlator.correlate(outfile, row_filename, col_filename, spearman=True, pvalue_threshold=None, rho_threshold = 0.3)
#!/usr/bin/env python3
# MutPlot version 0.0.1

from params import Params


pm = Params('mutplot')
args, config = pm.set_options()


class MutPlot(object):

    def __init__(self, args, config):
        self.out = args.out
        self.vcf = args.vcf
        self.snpEff = args.snpEff
        self.args = args
        self.config = config

    def check_outdir(self):
        if os.path.exists(self.out):
            print(time_stamp(),
                  'output directory already exist.'.format(self.out),
                  flush=True)
        else:
            os.mkdir(self.out)

    def run_snpEff(self):
        cmd = 'snpEff ann -s {0}/snpEff_summary.html \
                          {1} \
                          {2} \
                          1> {0}/mutmap.snpEff.vcf \
                          2> {0}/snpEff.log'.format(self.out,
                                                        self.snpEff,
                                                        self.vcf)
        cmd = clean_cmd(cmd)

        print(time_stamp(), 'start to run SnpEff.', flush=True)
        sbp.run(cmd, stdout=sbp.DEVNULL, stderr=sbp.DEVNULL, shell=True, check=True)
        print(time_stamp(), 'SnpEff successfully finished.', flush=True)

        self.args.vcf = '{}/mutmap.snpEff.vcf'.format(self.out)

    def make_igv_file(self):
        snp_index = pd.read_csv('{}/snp_index.tsv'.format(self.out),
                                sep='\t',
                                names=['CHROM',
                                       'POSI',
                                       'variant',
                                       'depth',
                                       'p99',
                                       'p95',
                                       'SNPindex'])

        snp_index['Start'] = snp_index['POSI'] - 1
        snp_index['End'] = snp_index['POSI']
        snp_index['Feature'] = snp_index['CHROM'].astype('str') \
                               + ':' + snp_index['POSI'].astype('str') \
                               + ':' + snp_index['variant'].astype('str') \
                               + ':' + snp_index['p99'].astype('str') \
                               + ':' + snp_index['p95'].astype('str')

        snp_index = snp_index[['CHROM',
                               'Start',
                               'End',
                               'Feature',
                               'SNPindex']]

        snp_index.to_csv('{}/snp_index.igv'.format(self.out),
                         sep='\t',
                         index=False)

        sliding_window = pd.read_csv('{}/sliding_window.tsv'.format(self.out),
                                     sep='\t',
                                     names=['CHROM',
                                            'POSI',
                                            'mean_p99',
                                            'mean_p95',
                                            'mean_SNPindex'])

        sliding_window['Start'] = sliding_window['POSI'] - 1
        sliding_window['End'] = sliding_window['POSI']
        sliding_window['Feature'] = sliding_window['CHROM'].astype('str') \
                                    + ':' + sliding_window['POSI'].astype('str') \
                                    + ':' + sliding_window['mean_p99'].astype('str') \
                                    + ':' + sliding_window['mean_p95'].astype('str')

        sliding_window = sliding_window[['CHROM',
                                         'Start',
                                         'End',
                                         'Feature',
                                         'mean_SNPindex']]

        sliding_window.to_csv('{}/sliding_window.igv'.format(self.out),
                              sep='\t',
                              index=False)

    def run(self):
        self.check_outdir()

        if self.snpEff is not None:
            self.run_snpEff()

        v2i = Vcf2Index(self.args, self.config)
        v2i.run()
        pt = Plot(self.args, self.config)
        pt.run()

        if self.args.igv:
            self.make_igv_file()


if __name__ == '__main__':

    import os
    import pandas as pd
    import subprocess as sbp
    from vcf2index import Vcf2Index
    from plot import Plot
    from utils import time_stamp
    from utils import clean_cmd

    print(time_stamp(), 'start to run MutPlot.', flush=True)
    mp = MutPlot(args, config)
    mp.run()
    print(time_stamp(), 'MutPlot successfully finished.', flush=True)

import os
import glob as glob
import numpy as np
import argparse
import fitsio
from astropy.table import Table,vstack,join,hstack
import astropy.io.fits as pyfits


parser = argparse.ArgumentParser()
parser.add_argument('--outdir',type=str,help='output directory of the quickquasar run')
parser.add_argument('--idir',type=str,help='directory from where to fetch the input data')
parser.add_argument('--catalog',type=str,default=None)


args = parser.parse_args()

## Check if BAL and DLA catalogs already exist
bal_catfile=args.outdir+'/BAL_cat.fits'
dla_catfile=args.outdir+'/DLA_cat.fits'


    
if (os.path.isfile(bal_catfile)) or (os.path.isfile(dla_catfile)):
    print("catalogs already exist")
    exit()
    
parent_dirs = glob.glob(args.idir+'/*')
DLA = []
BAL = []

for dirs in parent_dirs:
    sub_dirs = glob.glob(dirs+'/*')

    for i in range(len(sub_dirs)):
        
        index = sub_dirs[i].split('/')[-1]
        #print(sub_dirs[i]+'/truth-16-'+index+'.fits')
        #table = fitsio.FITS(sub_dirs[i]+'/truth-16-'+index+'.fits')
        if args.catalog == None:
            #tags = ['DLA_META', 'BAL_META']
            DLA_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='BAL_META')       
            BAL_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='DLA_META')

            DLA.append(DLA_table)
            BAL.append(BAL_table)

        elif args.catalog == 'BAL':
            BAL_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext=4)
            BAL.append(BAL_table)
            DLA = None

        elif args.catalog == 'DLA':
            DLA_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext=3)
            DLA.append(DLA_table)
            BAL = None

if BAL is not None:
    template_meta=fitsio.read('/global/cfs/cdirs/desi/spectro/templates/basis_templates/v3.2/bal_templates_v3.0.fits',columns=['BI_CIV','ERR_BI_CIV'])
    BAL = Table(np.hstack(BAL))
    index=BAL['TEMPLATEID']
    template_meta=Table(template_meta[index])
    BAL=hstack([BAL,template_meta])
    BAL.write(bal_catfile)
    #fitsio.write(bal_catfile,BAL)
    
if DLA is not None:
    DLA = np.hstack(DLA)
    fitsio.write(dla_cat,DLA)

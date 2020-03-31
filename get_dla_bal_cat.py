import os
import glob as glob
import numpy as np
import argparse
import fitsio
from astropy.table import Table,vstack,join,hstack,Column
import astropy.io.fits as pyfits


parser = argparse.ArgumentParser()
parser.add_argument('--outdir',type=str,help='output directory of the quickquasar run')
parser.add_argument('--idir',type=str,help='directory from where to fetch the input data')
parser.add_argument('--catalog',type=str,default=None,help='can be BAL or DLA, if none will try to generate both.')
args = parser.parse_args()

## Check if BAL and DLA catalogs already exist
bal_catfile=args.outdir+'/BALtruth.fits'
dla_catfile=args.outdir+'/DLAtruth.fits'
    
#if (os.path.isfile(bal_catfile)) or (os.path.isfile(dla_catfile)):
#    print("catalogs already exist")
#    exit()
    
parent_dirs = glob.glob(args.idir+'/0')
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
            TRUTH= fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='TRUTH')
            DLA_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='DLA_META')       
            BAL_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='BAL_META')
            DLA.append(DLA_table)
            BAL.append(BAL_table)

        elif args.catalog == 'BAL':
            BAL_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='BAL_META')
            BAL.append(BAL_table)
            DLA = None

        elif args.catalog == 'DLA':
            TRUTH= fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='TRUTH')
            DLA_table = fitsio.read(sub_dirs[i]+'/truth-16-'+index+'.fits',ext='BAL_META')
            DLA.append(DLA_table)
            BAL = None

if BAL is not None:
    #For backwards compatibility with previous versions of mocks. 
    BAL =Table(np.hstack(BAL))
    if 'BI_CIV' in BAL.colnames:
        BAL =Table(np.hstack(BAL))
    else:
        print('complementing BAL catalog')
        template_meta=fitsio.read('/global/cfs/cdirs/desi/spectro/templates/basis_templates/v3.2/bal_templates_v3.0.fits',columns=['BI_CIV',
                'ERR_BI_CIV','NCIV_2000','VMIN_CIV_2000','VMAX_CIV_2000','POSMIN_CIV_2000',
                'FMIN_CIV_2000','AI_CIV','ERR_AI_CIV','NCIV_450','VMIN_CIV_450',
                'VMAX_CIV_450','POSMIN_CIV_450','FMIN_CIV_450'])
        index=BAL['TEMPLATEID']
        template_meta=Table(template_meta[index])
        BAL=hstack([BAL,template_meta])
        balprob = Column(np.ones(len(BAL)), name='BALPROB')
        BAL.add_column(balprob, index=0)
        BAL['REDSHIFT'].name = 'Z'
        BAL['TEMPLATEID'].name='BAL_TEMPLATEID'
        new_order = ['TARGETID','Z','BALPROB','BAL_TEMPLATEID','BI_CIV',
                'ERR_BI_CIV','NCIV_2000','VMIN_CIV_2000','VMAX_CIV_2000','POSMIN_CIV_2000',
                'FMIN_CIV_2000','AI_CIV','ERR_AI_CIV','NCIV_450','VMIN_CIV_450',
                'VMAX_CIV_450','POSMIN_CIV_450','FMIN_CIV_450']  # List or tuple
        BAL=BAL[new_order]
    BAL.write(bal_catfile)
    #fitsio.write(bal_catfile,BAL)
    
if DLA is not None:
    DLA = np.hstack(DLA)
    TRUTH=np.hstack(TRUTH)
    #Read zcatalog to get qso redshift... 
    catfile='./'
    zcat=fitsio.read(catfile)
    data=zcat['ZCATALOG'].data
    print(Table(data))
    fitsio.write(dla_catfile,DLA)

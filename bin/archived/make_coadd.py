from tilec import utils as tutils,fg
import argparse, yaml
import numpy as np
from pixell import enmap,fft,utils
from orphics import maps,io,stats,cosmology

# Parse command line
parser = argparse.ArgumentParser(description='Make ILC maps.')
parser.add_argument("combs", type=str,help='List of combinations.')
args = parser.parse_args()

combs = args.combs.split(',')


def process(kouts,name="default",ellmax=None,y=False,y_ellmin=400):
    ellmax = lmax if ellmax is None else ellmax
    ksilc = enmap.zeros((Ny,Nx),wcs,dtype=np.complex128).reshape(-1)
    ksilc[modlmap.reshape(-1)<lmax] = np.nan_to_num(kouts.copy())
    ksilc = enmap.enmap(ksilc.reshape((Ny,Nx)),wcs)
    ksilc[modlmap>ellmax] = 0
    if y: ksilc[modlmap<y_ellmin] = 0
    msilc = np.nan_to_num(fft.ifft(ksilc,axes=[-2,-1],normalize=True).real * bmask)
    enmap.write_map(proot+"outmap_%s.fits" % name,enmap.enmap(msilc,wcs))
    p2d = fc.f2power(ksilc,ksilc)

    bin_edges = np.arange(100,3000,40)
    binner = stats.bin2D(modlmap,bin_edges)
    cents,p1d = binner.bin(p2d)
    
    try:
        # io.plot_img(np.log10(np.fft.fftshift(p2d)),proot+"ksilc_%s.png" % name,aspect='auto')
        # io.plot_img(msilc,proot+"msilc_%s.png" % name)
        # io.plot_img(msilc,proot+"lmsilc_%s.png" % name,lim=300)
        tmask = maps.mask_kspace(shape,wcs,lmin=300,lmax=5000 if not(y) else 1500)
        fmap = maps.filter_map(msilc,tmask)*bmask
        io.plot_img(fmap,proot+"hmsilc_%s.png" % name,high_res=True)
    except:
        pass

    return cents,p1d
    

# pl1 = io.Plotter(yscale='log',xlabel='$\\ell$',ylabel='$\\ell^2 C_{\\ell}$')
# ells = np.arange(0,6000,1)
# pl1.add(ells,ells**2.*cosmology.noise_func(ells,1.4,10.0,lknee=0.,alpha=1.,dimensionless=False,TCMB=2.7255e6),color='k',ls="-.")

# for comb,col in zip(combs,['C0','C1']):

#     croot = "data/%s/" %comb
#     proot = "data/%s/%s_" %(comb,comb)
#     arrays = [line.rstrip('\n') for line in open("%sarrays.txt"%croot,'r')][0].split(',')
#     config = tutils.Config(arrays)
#     narrays = len(arrays)
#     freqs = []
#     for i in range(narrays):
#         f = config.darrays[arrays[i]]['freq']
#         freqs.append(f)
#     shape,wcs = config.shape,config.wcs
#     Ny,Nx = shape[-2:]
#     fc = config.fc
#     modlmap = config.modlmap
#     lmax = 5000

#     icinv = np.load("%sicinv.npy"%croot)
#     Cinv = np.rollaxis(icinv,0,3)
#     ikmaps,_ = config.get_coadds()
#     ikmaps[:,modlmap>5000] = 0
#     kmaps = ikmaps.reshape((narrays,Ny*Nx))[:,modlmap.reshape(-1)<lmax]
#     bmask = maps.binary_mask(enmap.read_map(config.xmaskfname()))

#     yresponses = fg.gnu(freqs,tcmb=2.7255)
#     cresponses = yresponses*0.+1.
    
#     iksilc = maps.silc(kmaps,Cinv) # ILC HAPPENS HERE
#     cents,psilc_cmb = process(iksilc,"silc_cmb")

#     iksilc = maps.cilc(kmaps,Cinv,cresponses,yresponses) # ILC HAPPENS HERE
#     cents,pcilc_cmb = process(iksilc,"cilc_cmb_deproj_y_lmax_3000",ellmax=3000)
    
#     pl1.add(cents,psilc_cmb*cents**2.,label=comb+" ilc",ls="-",lw=2,color=col)
#     pl1.add(cents,pcilc_cmb*cents**2.,label=comb+" cilc",ls="--",lw=2,color=col)
#     pl1._ax.set_ylim(6e2,1e5)
#     pl1._ax.set_xlim(200,3000)
# pl1.legend(loc='lower left')
# pl1.done("p1d_cmb.png")


pl2 = io.Plotter(yscale='log',xlabel='$\\ell$',ylabel='$\\ell^2 C_{\\ell}$')
ells = np.arange(0,6000,1)

for comb,col in zip(combs,['C0','C1']):
    croot = "data/%s/" %comb
    proot = "data/%s/%s_" %(comb,comb)
    arrays = [line.rstrip('\n') for line in open("%sarrays.txt"%croot,'r')][0].split(',')
    config = tutils.Config(arrays)
    narrays = len(arrays)
    freqs = []
    for i in range(narrays):
        f = config.darrays[arrays[i]]['freq']
        freqs.append(f)
    shape,wcs = config.shape,config.wcs
    Ny,Nx = shape[-2:]
    fc = config.fc
    modlmap = config.modlmap
    lmax = 5000

    icinv = np.load("%sicinv.npy"%croot)
    Cinv = np.rollaxis(icinv,0,3)
    ikmaps,_ = config.get_coadds()
    ikmaps[:,modlmap>5000] = 0
    kmaps = ikmaps.reshape((narrays,Ny*Nx))[:,modlmap.reshape(-1)<lmax]
    bmask = maps.binary_mask(enmap.read_map(config.xmaskfname()))

    yresponses = fg.gnu(freqs,tcmb=2.7255)
    cresponses = yresponses*0.+1.
    
    iksilc = maps.silc(kmaps,Cinv,yresponses) # ILC HAPPENS HERE
    cents,psilc_y = process(iksilc,"silc_y",y=True,ellmax=3000)
    

    iksilc = maps.cilc(kmaps,Cinv,yresponses,cresponses) # ILC HAPPENS HERE
    cents,pcilc_y = process(iksilc,"cilc_y_deproj_cmb_lmax_3000",ellmax=3000,y=True)

    pl2.add(cents,psilc_y*cents**2.,label=comb+" ilc",ls="-",lw=2,color=col)
    pl2.add(cents,pcilc_y*cents**2.,label=comb+" cilc",ls="--",lw=2,color=col)

    pl2._ax.set_ylim(1e2,5e3)

pl2.done("p1d_y.png")

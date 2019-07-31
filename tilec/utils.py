import yaml, numpy, six
from pixell import enmap
import numpy as np
from orphics import maps,io
from soapack import interfaces as sints
from scipy import ndimage
import os,sys
import pandas


def get_save_path(version,region):
    save_path = sints.dconfig['tilec']['save_path']
    savedir = os.path.join(save_path , version + "_" + region)
    return savedir + "/"

def get_scratch_path(version,region):
    scratch_path = sints.dconfig['tilec']['scratch_path']
    return os.path.join(scratch_path , version + "_" + region ) + "/"

def get_temp_split_fname(qid,region,version):
    spath = get_scratch_path(version,region)
    return spath + "split_%s.fits" % (qid)
    

class ASpecs(object):
    def __init__(self):
        cfile = "input/array_specs.csv"
        self.adf = pandas.read_csv(cfile)
        self.aspecs = lambda qid,att : self.adf[self.adf['#qid']==qid][att].item()

    def get_specs(self,aid):
        aspecs = self.aspecs
        lmin = int(aspecs(aid,'lmin'))
        lmax = int(aspecs(aid,'lmax'))
        assert 0 <= lmin < 50000
        assert 0 <= lmax < 50000
        hybrid = aspecs(aid,'hybrid')
        assert type(hybrid)==bool
        radial = aspecs(aid,'radial')
        assert type(radial)==bool
        friend = aspecs(aid,'friends')
        try: friend = friend.split(',')
        except: friend = None
        cfreq = float(aspecs(aid,'cfreq'))
        fgroup = int(aspecs(aid,'fgroup'))
        wrfit = int(aspecs(aid,'wrfit'))
        return lmin,lmax,hybrid,radial,friend,cfreq,fgroup,wrfit


def get_specs(aid):
    aspecs = ASpecs()
    return aspecs.get_specs(aid)

def load_geometries(qids):
    geoms = {}
    for qid in qids:
        dmodel = sints.arrays(qid,'data_model')
        season = sints.arrays(qid,'season')
        region = sints.arrays(qid,'region')
        array = sints.arrays(qid,'array')
        freq = sints.arrays(qid,'freq')
        dm = sints.models[dmodel]()
        print(season,region,array,freq)
        shape,wcs = enmap.read_map_geometry(dm.get_split_fname(season=season,patch=region,array=array+"_"+freq if not(is_planck(qid)) else freq,splitnum=0,srcfree=True))
        geoms[qid] = shape[-2:],wcs 
    return geoms


def get_nside(qid):
    if qid in ['p01','p02','p03']: return 1024
    elif qid in ['p04','p05','p06','p07','p08']: return 2048
    else: raise ValueError
    

def get_kbeam(qid,modlmap,sanitize=False,**kwargs):
    dmodel = sints.arrays(qid,'data_model')
    season = sints.arrays(qid,'season')
    region = sints.arrays(qid,'region')
    array = sints.arrays(qid,'array')
    freq = sints.arrays(qid,'freq')
    dm = sints.models[dmodel]()
    gfreq = array+"_"+freq if not(is_planck(qid)) else freq
    return dm.get_beam(modlmap, season=season,patch=region,array=gfreq, kind='normalized',sanitize=sanitize,**kwargs)


def filter_div(div):
    """Downweight very thin stripes in the div - they tend to be problematic single detectors"""
    res = div.copy()
    for comp in res.preflat: comp[:] = ndimage.minimum_filter(comp, size=2)
    return res

def robust_ref(div,tol=1e-5):
    ref = np.median(div[div>0])
    ref = np.median(div[div>ref*tol])
    return ref


def get_splits_ivar(qid,extracter,ivar_unhit=1e-7, ivar_tol=20):
    dmodel = sints.arrays(qid,'data_model')
    season = sints.arrays(qid,'season')
    region = sints.arrays(qid,'region')
    array = sints.arrays(qid,'array')
    freq = sints.arrays(qid,'freq')
    dm = sints.models[dmodel]()
    ivars = []
    for i in range(dm.get_nsplits(season=season,patch=region,array=array)):
        omap = extracter(dm.get_split_ivar_fname(season=season,patch=region,array=array+"_"+freq if not(is_planck(qid)) else freq,splitnum=i))
        if omap.ndim>2: omap = omap[0]
        if not(np.any(omap>0)): 
            print("Skipping %s as it seems to have an all zero ivar in this tile" % qid)
            return None
        omap[~np.isfinite(omap)] = 0
        omap[omap<ivar_unhit] = 0
        ref_div  = robust_ref(omap)
        omap = np.minimum(omap, ref_div*ivar_tol)
        omap = filter_div(omap)
        eshape,ewcs = omap.shape,omap.wcs
        ivars.append(omap.copy())
    return enmap.enmap(np.stack(ivars),ewcs)


def get_splits(qid,extracter):
    dmodel = sints.arrays(qid,'data_model')
    season = sints.arrays(qid,'season')
    region = sints.arrays(qid,'region')
    array = sints.arrays(qid,'array')
    freq = sints.arrays(qid,'freq')
    dm = sints.models[dmodel]()
    splits = []
    for i in range(dm.get_nsplits(season=season,patch=region,array=array)):
        omap = extracter(dm.get_split_fname(season=season,patch=region,array=array+"_"+freq if not(is_planck(qid)) else freq,splitnum=i,srcfree=True),sel=np.s_[0,...]) # sel
        assert np.all(np.isfinite(omap))
        eshape,ewcs = omap.shape,omap.wcs
        splits.append(omap.copy())
    return enmap.enmap(np.stack(splits),ewcs)

def apodize_zero(imap,width):
    ivar = imap.copy()
    ivar[...,:1,:] = 0; ivar[...,-1:] = 0; ivar[...,:,:1] = 0; ivar[...,:,-1:] = 0
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(ivar>0)
    apod = 0.5*(1-np.cos(np.pi*np.minimum(1,dist/width)))
    return apod

def is_planck(qid):
    dmodel = sints.arrays(qid,'data_model')
    return True if dmodel=='planck_hybrid' else False
    
def coadd(imap,ivar):
    isum = np.sum(ivar,axis=0)
    c = np.sum(imap*ivar,axis=0)/isum
    c[~np.isfinite(c)] = 0
    return c,isum
    


def estimate_separable_pixwin_from_normalized_ps(ps2d):
    """
    Tool from Sigurd to account for MBAC 220 CEA->CAR pixelization

    Sigurd: Then the spectrum is whitened with: ps2d /= ywin[:,None]**2; ps2d /= xwin[None,:]**2
    And the fourier map is whitened by the same, but without the squares

    Mat M [6:11 PM]
    great, and what does normalized ps mean?

    Sigurd [6:12 PM]
    ah. It's a power spectrum that's been normalized so that the white noise level should be 1

    Mat M [6:12 PM]
    mmm, how did you do that exactly

    Sigurd [6:12 PM]
    it's based on div
    
    Mat M [6:12 PM]
    i see
    """
    
    mask = ps2d < 2
    res  = []
    for i in range(2):
        profile  = np.sum(ps2d*mask,1-i)/np.sum(mask,1-i)
        profile /= np.percentile(profile,90)
        profile  = np.fft.fftshift(profile)
        edge     = np.where(profile >= 1)[0]
        if len(edge) == 0:
            res.append(np.full(len(profile),1.0))
            continue
        edge = edge[[0,-1]]
        profile[edge[0]:edge[1]] = 1
        profile  = np.fft.ifftshift(profile)
        # Pixel window is in signal, not power
        profile **= 0.5
        res.append(profile)
    return res


def get_pixwin(shape):
    wy, wx = enmap.calc_window(shape)
    wind   = wy[:,None] * wx[None,:]
    return wind

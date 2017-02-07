"""
A set of functions to perform modifications to matplotlib colourbars,
and colourmaps, beyond the core maplotlib colourbar/colourmap functionality.

Created on Thu Jan 12 14:33:21 2017

    Author: DAV
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as _np
import matplotlib as _mpl
import matplotlib.pyplot as _plt
import matplotlib.gridspec as _gridspec
import matplotlib.colors as _mcolors
import matplotlib.cm as _cm

from matplotlib.colors import LinearSegmentedColormap


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=-1):
    """
    Truncates a standard matplotlib colourmap so
    that you can use part of the colour range in your plots.
    Handy when the colourmap you like has very light values at
    one end of the map that can't be seen easily.

    Arguments:
      cmap (:obj: `Colormap`): A matplotlib Colormap object. Note this is not
         a string name of the colourmap, you must pass the object type.
      minval (int, optional): The lower value to truncate the colour map to. 
         colourmaps range from 0.0 to 1.0. Should be 0.0 to include the full 
         lower end of the colour spectrum.
      maxval (int, optional): The upper value to truncate the colour map to.
         maximum should be 1.0 to include the full upper range of colours.
      n (int): Leave at default. 
    
    Example:
       minColor = 0.00
       maxColor = 0.85
       inferno_t = truncate_colormap(_plt.get_cmap("inferno"), minColor, maxColor) 
    """
    cmap = _plt.get_cmap(cmap)
    
    if n == -1:
        n = cmap.N
    new_cmap = _mcolors.LinearSegmentedColormap.from_list(
         'trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name, a=minval, b=maxval),
         cmap(_np.linspace(minval, maxval, n)))
    return new_cmap
    
def discrete_colourmap(N, base_cmap=None):
    """Creates an N-bin discrete colourmap from the specified input colormap.
    
    Author: github.com/jakevdp adopted by DAV
    
    Note: Modified so you can pass in the string name of a colourmap
        or a Colormap object.

    Arguments: 
        N (int): Number of bins for the discrete colourmap. I.e. the number
            of colours you will get.
        base_cmap (str or Colormap object): Can either be the name of a colourmap
            e.g. "jet" or a matplotlib Colormap object
    """

    print(type(base_cmap))
    if isinstance(base_cmap, _mcolors.Colormap):
        base = base_cmap
    elif isinstance(base_cmap, str):
        base = _plt.cm.get_cmap(base_cmap)
    else:
        print("DrapeName supplied is of type: ", type(base_cmap))
        raise ValueError('DrapeName must either be a string name of a colormap, \
                         or a Colormap. Please try again.')
        
    color_list = base(_np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)
    
def cmap_discretize(N, cmap):
    """Return a discrete colormap from the continuous colormap cmap.
    
    Arguments:
        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example:
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """

    if type(cmap) == str:
        cmap = _plt.get_cmap(cmap)
    colors_i = _np.concatenate((_np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = _np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
                       for i in range(N+1) ]
    # Return colormap object.
    return _mcolors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)
    

def colorbar_index(fig, cax, ncolors, cmap, drape_min_threshold, drape_max):
    """State-machine like function that creates a discrete colormap and plots
       it on a figure that is passed as an argument.

    Arguments:
       fig (matplotlib.Figure): Instance of a matplotlib figure object.
       cax (matplotlib.Axes): Axes instance to create the colourbar from. 
           This must be the Axes containing the data that your colourbar will be
           mapped from.
       ncolors (int): The number of colours in the discrete colourbar map.
       cmap (str or Colormap object): Either the name of a matplotlib colormap, or 
           an object instance of the colormap, e.g. cm.jet
       drape_min_threshold (float): Number setting the threshold level of the drape raster
           This should match any threshold you have set to mask the drape/overlay raster.
       drape_max (float): Similar to above, but for the upper threshold of your drape mask.
    """

    discrete_cmap = discrete_colourmap(ncolors, cmap)
    
    mappable = _cm.ScalarMappable(cmap=discrete_cmap)
    mappable.set_array([])
    #mappable.set_clim(-0.5, ncolors + 0.5)
    mappable.set_clim(drape_min_threshold, drape_max)
    
    print(type(fig))
    print(type(mappable))
    print(type(cax))
    print() 
    cbar = fig.colorbar(mappable, cax=cax)
    print(type(cbar))
    #cbar.set_ticks(_np.linspace(0, ncolors, ncolors))
    cbar.set_ticks(_np.linspace(drape_min_threshold, drape_max, ncolors+1))
    #cbar.set_ticklabels(range(ncolors))
    
    return cbar

def nonlinear_colormap():
    """Creates a non-linear colourmap from an existing colourmap.
    """
    pass

class nonlinear_colourmap(LinearSegmentedColormap):
    """Creates a non-linear colourmap from an existing colourmap.
    
    Creates a superclass based on the LinearSegmentedColormap class
    from matplotlib.
    
    Author: DAV from http://protracted-matter.blogspot.ie/2012/08/nonlinear-colormap-in-matplotlib.html
    
    Todo: This still doesn't appear to work well with negative numbers supplied for levels?
    """
    
    name = 'nlcmap'
        
    def __init__(self, cmap, levels):
        self.cmap = cmap
        self.N = cmap.N
        self.monochrome = self.cmap.monochrome
        self.levels = _np.asarray(levels, dtype='float64')
        self._x = self.levels
        self.levmax = self.levels.max()
        self.levmin = self.levels.min()
        self.transformed_levels = _np.linspace(self.levmin, self.levmax,
             len(self.levels))

    def __call__(self, xi, alpha=1.0, **kw):
        yi = _np.interp(xi, self._x, self.transformed_levels)
        return self.cmap(yi / (self.levmax-self.levmin) + 0.5, alpha)

#    def __call__(self, xi, alpha=1.0, **kw):
#        yi = _np.interp(xi, self._x, self.transformed_levels)
#        return self.cmap(yi / self.levmax, alpha)
    
    def sort_levels(self, levels):
        #levels = levels[levels <= 4.5] # Should check levels are not gt max value in data.
        return levels.sort()


class MidpointNormalize(_mcolors.Normalize):
    """Custom normalise option to normalise data in non-linear ways.
    
    Pass the object returned from this function to the norm= argument in 
    plotting functions like imshow or pcolormesh.
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        _mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return _np.ma.masked_array(_np.interp(value, x, y))    

        
class MetaColours(type):
    """A metclass for colourmaps making them all read-only attributes"""
    
    @property
    def niceterrain(cls):
        """ A terrain colour map that doesn't have the stupid blue colour for
            low lying land...
        """
        return cls._niceterrain

    @property
    def darkearth(cls):
        """ A terrain colour map that doesn't have the stupid blue colour for
            low lying land...
        """
        return cls._darkearth

class UsefulColourmaps(object, metaclass=MetaColours):
    """The interface for accessing usefulcolourmaps attributes"""
    _niceterrain = truncate_colormap("terrain", 0.25, 0.9)
    _darkearth = truncate_colormap("gist_earth", 0.25, 0.9)

#class UsefulColourmaps(object):
#    """A holding class for some useful custom colourmaps"""
#    
#    @property
#    def niceterrain():
#        niceterrain = truncate_colormap("terrain", 0.25, 0.9)
#        return niceterrain
    
    # That's all for now!
    
    
    
    
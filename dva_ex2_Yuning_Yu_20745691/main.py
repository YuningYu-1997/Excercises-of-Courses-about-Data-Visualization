import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, ImageURL
from bokeh.layouts import layout

from bokeh.colors import RGB

# Dependencies
# Make sure to install the additional dependencies noted in the requirements.txt using the following command:
# pip install -r requirements.txt

# You might want to implement a helper function for the update function below or you can do all the calculations in the
# update callback function.

# Only do this once you've followed the rest of the instructions below and you actually reach the part where you have to
# configure the callback of the lasso select tool. The ColumnDataSource containing the data from the dimensionality
# reduction has an on_change callback routine that is triggered when certain parts of it are selected with the lasso
# tool. More specifically, a ColumnDataSource has a property named selected, which has an on_change routine that can be
# set to react to its "indices" attribute and will call a user defined callback function. Connect the on_change routine
# to the "indices" attribute and an update function you implement here. (This is similar to the last exercise but this
# time we use the on_change function of the "selected" attribute of the ColumnDataSource instead of the on_change
# function of the select widget).
# In simpler terms, each time you select a subset of image glyphs with the lasso tool, you want to adjust the source
# of the channel histogram plot based on this selection.
# Useful information:
# https://docs.bokeh.org/en/latest/docs/reference/models/sources.html
# https://docs.bokeh.org/en/latest/docs/reference/models/tools.html
# https://docs.bokeh.org/en/latest/docs/reference/models/selections.html#bokeh.models.selections.Selection


# Fetch the number of images using glob or some other path analyzer
N = len(glob.glob("static/*.jpg"))

# Find the root directory of your app to generate the image URL for the bokeh server
ROOT = os.path.split(os.path.abspath("."))[1] + "/"

# Number of bins per color for the 3D color histograms
N_BINS_COLOR = 16
# Number of bins per channel for the channel histograms
N_BINS_CHANNEL = 50
# Define an array containing the 3D color histograms. We have one histogram per image each having N_BINS_COLOR^3 bins.
# i.e. an N * N_BINS_COLOR^3 array
#color=np.zeros((N,pow(N_BINS_COLOR,3)),dtype=np.int)
color=np.zeros((N,pow(N_BINS_COLOR,3)))
# Define an array containing the channel histograms, there is one per image each having 3 channel and N_BINS_CHANNEL
# bins i.e an N x 3 x N_BINS_CHANNEL array
channel=np.zeros((N,3,N_BINS_CHANNEL))
# initialize an empty list for the image file paths
file_path=[]
# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):
    # open image using PILs Image package
    im=Image.open(f)
    # Convert the image into a numpy array and reshape it such that we have an array with the dimensions (N_Pixel, 3)
    im_ar=np.array(im).reshape(184320,3)
    # Compute a multi dimensional histogram for the pixels, which returns a cube
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogramdd.html
    H,_ = np.histogramdd(im_ar,bins=N_BINS_COLOR,range=[(0,256),(0,256),(0,256)])
    H_reshape=H.reshape(4096)
    # However, later used methods do not accept multi dimensional arrays, so reshape it to only have columns and rows
    # (N_Images, N_BINS^3) and add it to the color_histograms array you defined earlier
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.reshape.html
    color[idx]=H_reshape
    # Append the image url to the list for the server
    url = ROOT + f
    file_path.append(url)
    # Compute a "normal" histogram for each color channel (rgb)
    # reference: https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    r,_=np.histogram(im_ar[:,0],bins=N_BINS_CHANNEL)
    g,_=np.histogram(im_ar[:,1],bins=N_BINS_CHANNEL)
    b,_=np.histogram(im_ar[:,2],bins=N_BINS_CHANNEL)
    # and add them to the channel_histograms
    channel[idx]=np.array([r,g,b],dtype=np.float)
# Calculate the indicated dimensionality reductions
# references:
# https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
# https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
#color_reshape=color.reshape (121,4096)
im_tsne=TSNE(n_components=2).fit_transform(color)
im_pca=PCA(n_components=2).fit_transform(color)
# Construct a data source containing the dimensional reduction result for both the t-SNE and the PCA and the image paths
source = ColumnDataSource( data = dict(
    x_tsne = im_tsne[:,0],
    y_tsne = im_tsne[:,1],
    x_pca = im_pca[:,0],
    y_pca = im_pca[:,1],
    url = file_path
))
image_selection_glyph = ImageURL(global_alpha=1,anchor="center")
image_nonselection_glyph = ImageURL(global_alpha=0.1,anchor="center")
# Create a first figure for the t-SNE data. Add the lasso_select, wheel_zoom, pan and reset tools to it.
p1 = figure(plot_width = 500, plot_height = 500, tools=["lasso_select", "wheel_zoom", "pan", "reset"],
            title="t-SNE", y_axis_label='y',x_axis_label='x')
# And use bokehs image_url to plot the images as glyphs
# reference: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/image_url.html
image1 = ImageURL(url="url", x="x_tsne", y="y_tsne", w=1.4, h=0.85, anchor="center")
p1.add_glyph(source, image1,selection_glyph=image_selection_glyph,nonselection_glyph=image_nonselection_glyph)
# Since the lasso tool isn't working with the image_url glyph you have to add a second renderer (for example a circle
# glyph) and set it to be completely transparent. If you use the same source for this renderer and the image_url,
# the selection will also be reflected in the image_url source and the circle plot will be completely invisible.
p1.circle("x_tsne", "y_tsne",alpha=0 ,source=source,selection_fill_alpha=0,nonselection_fill_color="blue")
# Create a second plot for the PCA result. As before, you need a second glyph renderer for the lasso tool.
# Add the same tools as in figure 1
p2=figure(plot_width = 500, plot_height = 500, tools=["lasso_select", "wheel_zoom", "pan", "reset"],
    title="PCA", y_axis_label='y',x_axis_label='x')
image2 = ImageURL(url="url", x="x_pca", y="y_pca", w=20000, h=10000, anchor="center")
p2.add_glyph(source, image2,selection_glyph=image_selection_glyph,nonselection_glyph=image_nonselection_glyph)
p2.circle("x_pca", "y_pca",alpha=0 ,source=source,selection_fill_alpha=0,nonselection_fill_alpha=0,)
# Construct a datasource containing the channel histogram data. Default value should be the selection of all images.
# Think about how you aggregate the histogram data of all images to construct this data source
channel_sum=np.zeros((3,50))
for i in range(channel.shape[2]):
    for j in range(channel.shape[1]):
        channel_sum[j,i]=sum(channel[:,j,i])
max_=max(map(max,channel_sum))
source2=ColumnDataSource( data = dict(
    x=range(50),
    r=channel_sum[0,:]/max_,
    g=channel_sum[1,:]/max_,
    b=channel_sum[2,:]/max_
))
# Construct a histogram plot with three lines.
# First define a figure and then make three line plots on it, one for each color channel.
# Add the wheel_zoom, pan and reset tools to it.
p3=figure(plot_width = 500, plot_height = 500, tools=["wheel_zoom", "pan", "reset"],
    title="Channel Histogram", y_axis_label='Frequecy',x_axis_label='bin')
p3.line('x','r',color=RGB(255,0,0),line_width=2,source=source2)
p3.line('x','g',color=RGB(0,255,0),line_width=2,source=source2)
p3.line('x','b',color=RGB(0,0,255),line_width=2,source=source2)
# Connect the on_change routine of the selected attribute of the dimensionality reduction ColumnDataSource with a
# callback/update function to recompute the channel histogram. Also read the topmost comment for more information.
def update(attr, old, new):
    selected_points = new
    path=glob.glob("static/*.jpg")
    channel_sum_new=np.zeros((3,50))    
    # we don't want to do anything if nothing is selected 
    if len(selected_points) == 0:
        '''source2.data = dict(
            x=range(50),
            r=channel_sum_new[0,:],
            g=channel_sum_new[1,:],
            b=channel_sum_new[2,:]
        )'''
        return
        
    # Count the occurences of the two classes "did it correctly" and "messed with the dark arts"
    for i in selected_points:
        im=Image.open(path[i])
        im_ar=np.array(im).reshape(184320,3)
        r,_=np.histogram(im_ar[:,0],bins=N_BINS_CHANNEL)
        g,_=np.histogram(im_ar[:,1],bins=N_BINS_CHANNEL)
        b,_=np.histogram(im_ar[:,2],bins=N_BINS_CHANNEL)
        channel_sum_new[0]+=r
        channel_sum_new[1]+=g
        channel_sum_new[2]+=b
    max_new=max(map(max,channel_sum_new))
    source2.data = dict(
        x=range(50),
        r=channel_sum_new[0]/max_new,
        g=channel_sum_new[1]/max_new,
        b=channel_sum_new[2]/max_new
    )
source.selected.on_change("indices", update)
# Construct a layout and use curdoc() to add it to your document.
it=layout([[p1,p2,p3]],sizing_mode="stretch_width")
curdoc().add_root(it)
# You can use the command below in the folder of your python file to start a bokeh directory app.
# Be aware that your python file must be named main.py and that your images have to be in a subfolder name "static"
# bokeh serve --show .
# python -m bokeh serve --show .

# dev option:
# bokeh serve --dev --show .
# python -m bokeh serve --dev --show .'''
# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/Visualization/nwi_wetlands_symbology.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/Visualization/nwi_wetlands_symbology.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://mybinder.org/v2/gh/giswqs/earthengine-py-notebooks/master?filepath=Visualization/nwi_wetlands_symbology.ipynb"><img width=58px src="https://mybinder.org/static/images/logo_social.png" />Run in binder</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/Visualization/nwi_wetlands_symbology.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
"""

# %%
"""
## Install Earth Engine API and geemap
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geemap](https://github.com/giswqs/geemap). The **geemap** Python package is built upon the [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) packages and implements several methods for interacting with Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, and `Map.centerObject()`.
The following script checks if the geemap package has been installed. If not, it will install geemap, which automatically installs its [dependencies](https://github.com/giswqs/geemap#dependencies), including earthengine-api, folium, and ipyleaflet.

**Important note**: A key difference between folium and ipyleaflet is that ipyleaflet is built upon ipywidgets and allows bidirectional communication between the front-end and the backend enabling the use of the map to capture user input, while folium is meant for displaying static data only ([source](https://blog.jupyter.org/interactive-gis-in-jupyter-with-ipyleaflet-52f9657fa7a)). Note that [Google Colab](https://colab.research.google.com/) currently does not support ipyleaflet ([source](https://github.com/googlecolab/colabtools/issues/60#issuecomment-596225619)). Therefore, if you are using geemap with Google Colab, you should use [`import geemap.eefolium`](https://github.com/giswqs/geemap/blob/master/geemap/eefolium.py). If you are using geemap with [binder](https://mybinder.org/) or a local Jupyter notebook server, you can use [`import geemap`](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py), which provides more functionalities for capturing user input (e.g., mouse-clicking and moving).
"""

# %%
# Installs geemap package
import subprocess

try:
    import geemap
except ImportError:
    print('geemap package not installed. Installing ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geemap'])

# Checks whether this notebook is running on Google Colab
try:
    import google.colab
    import geemap.eefolium as emap
except:
    import geemap as emap

# Authenticates and initializes Earth Engine
import ee

try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()  

# %%
"""
## Create an interactive map 
The default basemap is `Google Satellite`. [Additional basemaps](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py#L13) can be added using the `Map.add_basemap()` function. 
"""

# %%
Map = emap.Map(center=[40,-100], zoom=4)
Map.add_basemap('ROADMAP') # Add Google Map
Map

# %%
"""
## Add Earth Engine Python script 
"""

# %%
# Add Earth Engine dataset
# NWI legend: https://www.fws.gov/wetlands/Data/Mapper-Wetlands-Legend.html
def nwi_add_color(fc):
    emergent = ee.FeatureCollection(
        fc.filter(ee.Filter.eq('WETLAND_TY', 'Freshwater Emergent Wetland')))
    emergent = emergent.map(lambda f: f.set(
        'R', 127).set('G', 195).set('B', 28))
    # print(emergent.first())

    forested = fc.filter(ee.Filter.eq(
        'WETLAND_TY', 'Freshwater Forested/Shrub Wetland'))
    forested = forested.map(lambda f: f.set('R', 0).set('G', 136).set('B', 55))

    pond = fc.filter(ee.Filter.eq('WETLAND_TY', 'Freshwater Pond'))
    pond = pond.map(lambda f: f.set('R', 104).set('G', 140).set('B', 192))

    lake = fc.filter(ee.Filter.eq('WETLAND_TY', 'Lake'))
    lake = lake.map(lambda f: f.set('R', 19).set('G', 0).set('B', 124))

    riverine = fc.filter(ee.Filter.eq('WETLAND_TY', 'Riverine'))
    riverine = riverine.map(lambda f: f.set(
        'R', 1).set('G', 144).set('B', 191))

    fc = ee.FeatureCollection(emergent.merge(
        forested).merge(pond).merge(lake).merge(riverine))

    base = ee.Image(0).mask(0).toInt8()
    img = base.paint(fc, 'R') \
        .addBands(base.paint(fc, 'G')
                  .addBands(base.paint(fc, 'B')))
    return img


fromFT = ee.FeatureCollection("users/wqs/Pipestem/Pipestem_HUC10")
Map.addLayer(ee.Image().paint(fromFT, 0, 2), {}, 'Watershed')
huc8_id = '10160002'
nwi_asset_path = 'users/wqs/NWI-HU8/HU8_' + huc8_id + '_Wetlands'    # NWI wetlands for the clicked watershed
clicked_nwi_huc = ee.FeatureCollection(nwi_asset_path)
nwi_color = nwi_add_color(clicked_nwi_huc)
Map.centerObject(clicked_nwi_huc, 10)
Map.addLayer(nwi_color, {'gamma': 0.3, 'opacity': 0.7}, 'NWI Wetlands Color')


# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map
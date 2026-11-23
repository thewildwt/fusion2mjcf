"""
@author: thewildwt
"""


import adsk, re
from xml.etree.ElementTree import Element, SubElement
from ..utils import utils

class Asset:
    def __init__(self, name):
        """
        Parameters
        ----------
        name: str
            name of the link
        content_type:
            explicitly declares a file's Media Type
        file
            path of the models stl file
        scale
            sets the scale of the link
        asset_xml : str
            generated xml describing about the asset
        """
        self.name = name
        self.content_type = "model/stl"
        self.file = "meshes/" + self.name + ".stl"
        self.scale = "0.001 0.001 0.001"

        self.asset_xml = None

    def make_asset_xml(self):
        """
        Generate the asset_xml and hold it by self.asset_xml
        """
        asset = Element('asset')

        #meshes
        mesh = SubElement(asset , 'mesh')
        mesh.attrib = \
                {'name':self.name,
                 'content_type':self.content_type,
                 'file':self.file,
                 'scale':self.scale
                }
        self.asset_xml = "\n".join(utils.prettify(asset).split("\n")[1:])


def make_asset_list(root , msg):
    """      
    Parameters
    ----------
    root: adsk.fusion.Design.cast(product)
        Root component
    msg: str
        Tell the status
        
    Returns
    ----------
    asset_list : ['base_link' , 'component_1' , ---]
    
    msg: str
        Tell the status
    """

# Get component properties.      
    allOccs = root.occurrences
    asset_list = {} 

    for occs in allOccs:
        asset_list.append(re.sub('[ :()]', '_', occs.name))

    return asset_list, msg
"""
@author: thewildwt
"""


import adsk, re
from xml.etree.ElementTree import Element, SubElement
from ..utils import utils


def make_asset_xml(asset_list):
    """
    Generate the asset_xml and return it
    """
    content_type = "model/stl"
    scale = "0.001 0.001 0.001"
    
    asset = Element('asset')

    for name in asset_list:
        file = "meshes/" + name + ".stl"
        mesh = SubElement(asset , 'mesh')
        mesh.attrib = \
                {'name':name,
                    'content_type':content_type,
                    'file':file,
                    'scale':scale
                }
        
    asset_xml = "\n".join(utils.prettify(asset).split("\n")[1:])
    return asset_xml



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
    asset_list = []
    
    for occs in allOccs:
        if occs.component.name == 'base_link':
             asset_list.append("base_link")
        else:
            asset_list.append(re.sub('[ :()]', '_', occs.name))

    return asset_list, msg
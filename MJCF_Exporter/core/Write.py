"""
@author: thewildwt
"""

import adsk, os
from xml.etree.ElementTree import Element, SubElement
from . import Asset, Worldbody
from ..utils import utils


def write_asset_mjcf(asset_list , file_name):
    with open(file_name, mode='a') as f:
        for component in asset_list:
            name = component
            asset = Asset.Asset(name=name)     
            asset.make_asset_xml()
            f.write(asset.asset_xml)
            f.write('\n')


def write_worldbody_mjcf(worldbody_dict, file_name):
    """
    Write joints and transmission information into mjcf "robot_name.xml"
    
    
    Parameters
    ----------
    worldbody_dict: dict
        information of each body and joint
    file_name: str
        urdf full path
    """
    
    with open(file_name, mode='a') as f:
        worldbody_xml = Worldbody.make_body_xml(worldbody_dict)
        f.write(worldbody_xml)
        f.write('\n')


def write_mujocu_endtag(file_name):
    """
    Write the </mujoco> tag at the end of the mjcf
    
    
    Parameters
    ----------
    file_name: str
        mjcf full path
    """
    with open(file_name, mode='a') as f:
        f.write('</mujoco>\n')
        

def write_mjcf(worldbody_dict, asset_list , package_name, robot_name, save_dir):

    file_name = save_dir + '/' + robot_name + '.xml'  # the name of mujoco file
    with open(file_name, mode='w') as f:
        f.write('<mujoco model="{}">\n'.format(robot_name))
        f.write('   <compiler angle="radian"/>\n')

    write_asset_mjcf(asset_list , file_name)
    write_worldbody_mjcf(worldbody_dict, file_name)
    write_mujocu_endtag(file_name)



"""
@author: thewildwt
"""


import adsk, re
from xml.etree.ElementTree import Element, SubElement
from ..utils import utils

class Worldbody:
    def __init__(self, name, xyz, axis, parent, child, joint_type, upper_limit, lower_limit):
        """
        Attributes
        ----------
        name: str
            name of the joint
        type: str
            type of the joint(ex: rev)
        xyz: [x, y, z]
            coordinate of the joint
        axis: [x, y, z]
            coordinate of axis of the joint
        parent: str
            parent link
        child: str
            child link
        joint_xml: str
            generated xml describing about the joint
        tran_xml: str
            generated xml describing about the transmission
        """
        self.name = name
        self.body_pos
        self.pos = -self.body_pos
        
        self.geom_quat = "1 0 0 0"
        self.geom_type = "mesh"
        self.geom_rgba = "0.7 0.7 0.7 1"

        self.inertia_quat = "0.5 0.5 -0.5 0.5"
        self.mass
        self.diaginertia

        self.joint_axis

    def make_worldbody_xml(self):
        pass

    def make_body_xml(self , count):
        pass

def make_worldbody_dict(root, msg):
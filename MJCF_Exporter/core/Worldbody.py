"""
@author: thewildwt
"""


import adsk, re
from xml.etree.ElementTree import Element, SubElement
from ..utils import utils

def make_body_xml(worldbody_dict):
    """
    Generate the body_xml and return it by body_xml
    """

    geom_quat = "1 0 0 0"
    geom_type = "mesh"
    geom_rgba = "0.7 0.7 0.7 1"
    
    worldbody= Element('worldbody')
    geom = SubElement(worldbody , 'geom')
    geom.attrib = \
            {'quat':geom_quat ,
             'type':geom_type ,
             'rgba':geom_rgba ,
             'mesh':'base_link'}
    

    body_tree = {} # to store the subelemnt to access later
    key_count = 0 # index of the element to access


    for key in worldbody_dict:
        
        #setting all the variables
        key_dict = worldbody_dict[key]
        
        body_name = key
        body_pos = ' '.join([str(_) for _ in key_dict['body_pos']])
        
        joint_name = key_dict['joint_name']
        joint_axis = ' '.join([str(_) for _ in key_dict['joint_axis']])
        joint_type = key_dict['joint_type']
        joint_range = ' '.join([str(_) for _ in key_dict['joint_range']])

        inertia_pos =  \
                [ i-j for i, j in zip(key_dict['inertia_pos'],key_dict['world_body_pos'])]
        inertia_pos = ' '.join([str(_) for _ in inertia_pos])
        
        inertia_mass = str(key_dict['inertia_mass'])
        inertia_full = ' '.join([str(_) for _ in key_dict['inertia_full']])

        geom_pos = ' '.join([str(_) for _ in key_dict['geom_pos']])
        geom_mesh = body_name

        if key_count != 0:
            body_tree[key_count] = SubElement(body_tree[key_count-1] , 'body')
        else:
            body_tree[key_count] = SubElement(worldbody , 'body')

        body_tree[key_count].attrib = \
            {'name':body_name,
             'pos':body_pos}

        inertial = SubElement(body_tree[key_count] , 'inertial')
        inertial.attrib = \
            {'pos': inertia_pos,
             'mass': inertia_mass,
             'fullinertia':inertia_full
             }
        
        joint = SubElement(body_tree[key_count] , 'joint')
        joint.attrib = \
            {'name':joint_name ,
            'axis': joint_axis,
            'type': joint_type,
            'range':joint_range
            }
            
        geom = SubElement(body_tree[key_count] , 'geom')
        geom.attrib = \
            {'pos':geom_pos ,
            'quat': geom_quat,
            'type': geom_type,
            'rgba': geom_rgba,
            'mesh': geom_mesh
            }
        key_count += 1
        
   
    worldbody_xml = "\n".join(utils.prettify(worldbody).split("\n")[1:])
    
    return worldbody_xml



def make_worldbody_dict(root, msg):
    """
    worldbody_dict holds parent, axis and xyz informatino of the joints
    
    
    Parameters
    ----------
    root: adsk.fusion.Design.cast(product)
        Root component
    msg: str
        Tell the status
        
    Returns
    ----------
    worldbody_dict: 
        {name: {body_pos , world_body_pos, joint_name , joint_axis , joint_type , joint_range, inertia_pos \
                , inertia_mass , inertia_full , geom_pos}}
    msg: str
        Tell the status
    """
    worldbody_dict = {}
        
    
    #inertial
    # Get component properties.      
    for occs in root.occurrences:
        # Skip the root component.

        if occs.component.name != 'base_link':

            body_dict = {}
            prop = occs.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)

            mass = prop.mass  # kg
            body_dict['inertia_mass'] = mass
            center_of_mass = [_/100.0 for _ in prop.centerOfMass.asArray()] ## cm to m
            body_dict['inertia_pos'] = center_of_mass 

            # https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-ce341ee6-4490-11e5-b25b-f8b156d7cd97
            (_, xx, yy, zz, xy, yz, xz) = prop.getXYZMomentsOfInertia()
            moment_inertia_world = [_ / 10000.0 for _ in [xx, yy, zz, xy, yz, xz] ] ## kg / cm^2 -> kg/m^2
            inertia_tensor = utils.origin2center_of_mass(moment_inertia_world, center_of_mass, mass)
            body_dict['inertia_full'] = inertia_tensor

            worldbody_dict[re.sub('[ :()]', '_', occs.name)] = body_dict

    
    # joint
    
    joint_type_list = [
            'fixed', 'revolute', 'prismatic', 'Cylinderical',
            'PinSlot', 'Planner', 'Ball']  # these are the names in urdf

    body_pos = [[0,0,0]]
    for joint in root.joints:

        #the name is of the child in the joint
        child_name = re.sub('[ :()]', '_', joint.occurrenceOne.name)
        
        body_dict = worldbody_dict[child_name]
        joint_type = joint_type_list[joint.jointMotion.jointType]
        
        # swhich by the type of the joint
        body_dict['joint_axis'] = [0, 0, 0]
        upper_limit = 0.0
        lower_limit = 0.0
        
        # support  "Revolute", "Rigid" and "Slider"
        if joint_type == 'revolute':
            body_dict['joint_type'] = 'hinge'
            body_dict['joint_axis'] = [round(i, 6) for i in \
                joint.jointMotion.rotationAxisVector.asArray()] ## In Fusion, exported axis is normalized.
            max_enabled = joint.jointMotion.rotationLimits.isMaximumValueEnabled
            min_enabled = joint.jointMotion.rotationLimits.isMinimumValueEnabled            
            if max_enabled and min_enabled:  
                upper_limit = round(joint.jointMotion.rotationLimits.maximumValue, 6)
                lower_limit = round(joint.jointMotion.rotationLimits.minimumValue, 6)
            elif max_enabled and not min_enabled:
                msg = joint.name + 'is not set its lower limit. Please set it and try again.'
                break
            elif not max_enabled and min_enabled:
                msg = joint.name + 'is not set its upper limit. Please set it and try again.'
                break
            else:  # if there is no angle limit
                body_dict['joint_range'] = [0,6.2831]
                
        elif joint_type == 'prismatic':
            body_dict['joint_type'] = 'slide'
            body_dict['joint_axis'] = [round(i, 6) for i in \
                joint.jointMotion.slideDirectionVector.asArray()]  # Also normalized
            max_enabled = joint.jointMotion.slideLimits.isMaximumValueEnabled
            min_enabled = joint.jointMotion.slideLimits.isMinimumValueEnabled            
            if max_enabled and min_enabled:  
                upper_limit = round(joint.jointMotion.slideLimits.maximumValue/100, 6)
                lower_limit = round(joint.jointMotion.slideLimits.minimumValue/100, 6)
            elif max_enabled and not min_enabled:
                msg = joint.name + 'is not set its lower limit. Please set it and try again.'
                break
            elif not max_enabled and min_enabled:
                msg = joint.name + 'is not set its upper limit. Please set it and try again.'
                break
        elif joint_type == 'fixed':
            body_dict['joint_type'] = None

        body_dict['joint_range'] = [lower_limit , upper_limit]
        
        
        #There seem to be a problem with geometryOrOriginTwo. To calcualte the correct orogin of the generated stl files following approach was used.
        #https://forums.autodesk.com/t5/fusion-360-api-and-scripts/difference-of-geometryororiginone-and-geometryororiginonetwo/m-p/9837767
        #Thanks to Masaki Yamamoto!
        
        # Coordinate transformation by matrix
        # M: 4x4 transformation matrix
        # a: 3D vector
        def trans(M, a):
            ex = [M[0],M[4],M[8]]
            ey = [M[1],M[5],M[9]]
            ez = [M[2],M[6],M[10]]
            oo = [M[3],M[7],M[11]]
            b = [0, 0, 0]
            for i in range(3):
                b[i] = a[0]*ex[i]+a[1]*ey[i]+a[2]*ez[i]+oo[i]
            return(b)


        # Returns True if two arrays are element-wise equal within a tolerance
        def allclose(v1, v2, tol=1e-6):
            return( max([abs(a-b) for a,b in zip(v1, v2)]) < tol )

        try:
            xyz_from_one_to_joint = joint.geometryOrOriginOne.origin.asArray() # Relative Joint pos
            xyz_from_two_to_joint = joint.geometryOrOriginTwo.origin.asArray() # Relative Joint pos
            xyz_of_one            = joint.occurrenceOne.transform.translation.asArray() # Link origin
            xyz_of_two            = joint.occurrenceTwo.transform.translation.asArray() # Link origin
            M_two = joint.occurrenceTwo.transform.asArray() # Matrix as a 16 element array.

        # Compose joint position
            case1 = allclose(xyz_from_two_to_joint, xyz_from_one_to_joint)
            case2 = allclose(xyz_from_two_to_joint, xyz_of_one)
            if case1 or case2:
                xyz_of_joint = xyz_from_two_to_joint
            else:
                xyz_of_joint = trans(M_two, xyz_from_two_to_joint)


            body_dict['world_body_pos'] = [round(i / 100.0, 6) for i in xyz_of_joint]  # converted to meter

        except:
            try:
                if joint_type(joint.geometryOrOriginTwo)==adsk.fusion.JointOrigin:
                    data = joint.geometryOrOriginTwo.geometry.origin.asArray()
                else:
                    data = joint.geometryOrOriginTwo.origin.asArray()
                body_dict['world_body_pos'] = [round(i / 100.0, 6) for i in data]  # converted to meter
            except:
                msg = joint.name + " doesn't have joint origin. Please set it and run again."
                break

        body_pos.append(body_dict['world_body_pos'])
        body_dict['joint_name'] = joint.name
    
    last_geom_pos = [0,0,0]
    count = 0

    for joint in root.joints:
        #the name is of the child in the joint
        child_name = re.sub('[ :()]', '_', joint.occurrenceOne.name)
        
        body_dict = worldbody_dict[child_name]
        
        
        try:
            body_dict['body_pos'] = [round(c-p, 6) for p, c in \
                zip(body_pos[count], body_pos[count+1])]  # xyz = parent - child
        except KeyError as ke:
            app = adsk.core.Application.get()
            ui = app.userInterface
            ui.messageBox("There seems to be an error with the connection")
            quit()

        
        body_dict['geom_pos'] = [x-y for x ,y in zip(last_geom_pos ,body_dict['body_pos'])]
        last_geom_pos = body_dict['geom_pos']
    
        count += 1
    
    
    return worldbody_dict , msg
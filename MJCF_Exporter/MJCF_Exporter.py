#Author(fork) - thewildwt
#Author(orignal)-syuntoku14
#Description-Generate MJCF file from Fusion 360

#---------------------------------------------------------------------

import adsk, adsk.core, adsk.fusion, traceback
import os
from .utils import utils
from .core import Asset, Worldbody, Write

def run(context):
    ui = None
    success_msg = 'Successfully create MJCF file'
    msg = success_msg
    
    try:
        # --------------------
        # initialize
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        title = 'fusion2mjcf'
        if not design:
            ui.messageBox('No active Fusion design', title)
            return

        root = design.rootComponent  # root component 
        components = design.allComponents

        # set the names        
        robot_name = root.name.split()[0]
        package_name = robot_name + '_description'
        save_dir = utils.file_dialog(ui)
        if save_dir == False:
            ui.messageBox('Fusion2MJCF was canceled', title)
            return 0
        
        save_dir = save_dir + '/' + package_name
        try: os.mkdir(save_dir)
        except: pass     

        package_dir = os.path.abspath(os.path.dirname(__file__)) + '/package/'
        
        # --------------------
        # set dictionaries
        
        # Generate worldbody_dict
        worldbody_dict, msg = Worldbody.make_worldbody_dict(root, msg)
        if msg != success_msg:
            ui.messageBox(msg, title)
            return 0   
        
        # Generate asset dictionary
        asset_list, msg = Asset.make_asset_list(root, msg)
        if msg != success_msg:
            ui.messageBox(msg, title)
            return 0
        elif not 'base_link' in asset_list:
            msg = 'There is no base_link. Please set base_link and run again.'
            ui.messageBox(msg, title)
            return 0
        
        # --------------------
        # Generate MJCF
        Write.write_mjcf(worldbody_dict, asset_list, package_name, robot_name, save_dir)
        
    
        # Generate STl files        
        utils.copy_occs(root)
        utils.export_stl(design, save_dir, components)
        
        ui.messageBox(msg, title)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

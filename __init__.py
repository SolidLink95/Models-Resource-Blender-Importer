import os

import bpy
import bpy.utils.previews
from bpy.props import StringProperty, EnumProperty
from bpy.types import WindowManager
from bpy.utils import register_class, unregister_class


from Models_Resource_Importer.Models_Resources_Operations import update_platforms, update_letters, update_models_files, \
    update_sections, update_games, update_models, preview_collections, BLANK_TUPLE, BLANK_DICT_MODELS_FILES
from Models_Resource_Importer.GUI import Models_Resource_Operators_OT_List, MainPanel, DOWNLOAD_OT_test_op, IMPORT_MR_OT_test_op

bl_info = {
	"name": "Models-Resource Importer",
	"author": "banan039",
	"version": (0, 0, 1),
	"blender": (2, 90, 0),
	"category": "Import",
	"location": "View layer properties > Models-Resource",
	"wiki_url": "https://github.com/banan039pl/Models-Resource-Blender-Importer",
	"description": "Imports models from https://www.models-resource.com/"
}


def register():
    root_path = os.path.expandvars("%USERPROFILE%\\Documents\\ModelsResourceCache")
    WindowManager.url = 'https://www.models-resource.com/'
    WindowManager.exts = ['.fbx','.dae','.obj']
    WindowManager.Label = StringProperty(name='', default='Label')
    WindowManager.Root_Path = StringProperty(name="Cache dir",
                               subtype='DIR_PATH',
                               default='')
    
    bpy.types.Scene.logging = False
    #create_folder(root_path)
    
    bpy.types.Scene.platforms_dynamic = bpy.props.EnumProperty(items=update_platforms)
    bpy.types.Scene.platforms_collection = {} #get_platforms(WindowManager.url, "div", {"id": 'leftnav-consoles'})
    
    
    
    bpy.types.Scene.letters_dynamic = bpy.props.EnumProperty(items=update_letters)
    bpy.types.Scene.letters_collection = {} #{"" : "None"}
    WindowManager.platform_current = StringProperty(name='', default='None')

    bpy.types.Scene.Sections = bpy.props.EnumProperty(items=update_sections)
    
    #for pcoll in preview_collections.values(): bpy.utils.previews.remove(pcoll)
    #preview_collections.clear()
    
    
    """Games section START"""
    WindowManager.games_previews_dir = StringProperty(subtype='DIR_PATH')
    WindowManager.games_previews = EnumProperty(items=update_games)
    pcoll = bpy.utils.previews.new()
    pcoll.games_previews_dir = "" #This var is to prevent scanning the directory over and over again. Not drawn
    pcoll.pngs_number = 0 
    pcoll.cur_letter = 0 
    pcoll.games_previews = BLANK_TUPLE#()

    preview_collections["games"] = pcoll
    """Games section END"""
    
    """Models section  START"""
    WindowManager.models_previews_dir = ""
    WindowManager.models_previews = EnumProperty(items=update_models)
    pcoll = bpy.utils.previews.new()
    pcoll.models_previews_dir = ''
    pcoll.pngs_number = 0
    pcoll.cur_section = ''
    pcoll.models_previews = BLANK_TUPLE#()
    pcoll.models_data = {"":"None"}
    
    preview_collections["models"] = pcoll
    """Models section  END"""
    
    """Models files """
    bpy.types.Scene.models_files = bpy.props.EnumProperty(items=update_models_files)
    bpy.types.Scene.models_files_collection = dict(BLANK_DICT_MODELS_FILES)
    WindowManager.model_current = StringProperty(name='', default='Click Download')

    WindowManager.ACTION = EnumProperty(
        items=[
            ('platform_update', 'Get platforms', 'Update list of platforms'),  # Unused in final release
            ('letters_update', 'Get letters', 'Update list of letters'),  # Unused in final release
            ('games_update', 'Get games', 'Update list of games'),  # Unused in final release
            ('models_update', 'Get models', 'Update list of models'),  # Unused in final release
            ('import_model', 'Import model', 'Import model to current scene'),
            ('download_model', 'Download model', 'Downloades model to default path'),
            # ('', '', ''),
        ]
    )

    register_class(IMPORT_MR_OT_test_op)
    register_class(DOWNLOAD_OT_test_op)
    #register_class(Models_Resource_Operators_OT_List)
    register_class(MainPanel)

    
def unregister():
    del WindowManager.games_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    
    unregister_class(MainPanel)
    #unregister_class(Models_Resource_Operators_OT_List)
    unregister_class(DOWNLOAD_OT_test_op)
    unregister_class(IMPORT_MR_OT_test_op)

if __name__ == "__main__":
    register()
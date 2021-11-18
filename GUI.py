from urllib.parse import urljoin, urlparse

import bpy
import bpy.utils.previews
import os
import threading
from bpy.props import EnumProperty
from bpy.types import Panel, Operator

from Models_Resource_Importer.Models_Resource_Soup import create_folder, get_list, get_platforms, get_zip_url
from Models_Resource_Importer.Models_Resources_Operations import download_file_and_extract, import_by_extension, preview_collections

def download_model_context(self, context):
    print('downloading model')
    wm = context.window_manager
    """Return if model url is invalid"""
    try:
        url_model = wm.models_previews
    except:
        url_model = ''
    if not url_model or url_model == 'None': return {'FINISHED'}
    url, name = get_zip_url(wm.models_previews)
    if not url: return {'FINISHED'}

    directory = os.path.join(context.window_manager.Root_Path,
                             urlparse(context.scene.letters_dynamic).path[1:].replace('.html', '').replace('/',
                                                                                                           '\\'),
                             wm.games_previews.split('/')[-2],
                             context.scene.Sections,
                             'models'
                             )
    filepath = os.path.join(directory, name + '.zip')
    create_folder(directory)
    zip_url = urljoin(wm.url, url)
    # for e in list(context.scene.models_files_collection): del context.scene.models_files_collection[e]
    thread = threading.Thread(target=download_file_and_extract, args=(self, context, zip_url, filepath, directory))
    thread.daemon = True
    thread.start()

    print(f'Downloaded {name} to {filepath} from [{zip_url}]')

    return {'FINISHED'}

def import_model_context(self, context):
    print('importing model')
    wm = context.window_manager
    """Return if model filepath is invalid"""
    try:
        filepath = context.scene.models_files
    except:
        filepath = ''
    if not filepath or filepath == 'Click Download':
        wm.Label = f'Download model first!'
        return {'FINISHED'}
    import_by_extension(filepath)
    wm.Label = f'Imported {os.path.basename(filepath)}'
    return {'FINISHED'}

# from bpy.utils import register_class, unregister_class
class IMPORT_MR_OT_test_op(Operator):
    bl_idname = 'import_mr_test.test_op'
    bl_label = 'IMPORT'
    bl_description = 'IMPORT'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return import_model_context(self=self, context=context)

class DOWNLOAD_OT_test_op(Operator):
    bl_idname = 'download_test.test_op'
    bl_label = 'DOWNLOAD'
    bl_description = 'DOWNLOAD'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return download_model_context(self=self, context=context)


class Models_Resource_Operators_OT_List(Operator):
    """Buttons class starts here, unused in final release, only for debugging"""
    bl_idname = 'models_resource_oplist.oplist_list_op'
    bl_label = 'Button'
    bl_description = 'Button'
    #bl_options = {'REGISTER', 'UNDO'}
    action = ''

    #action: EnumProperty(
    #    items=[

    def execute(self, context):
        wm = context.window_manager
        wm.ACTION = self.action
        if wm.ACTION == 'platform_update':
            self.platform_update(context=context)
        elif wm.ACTION == 'letters_update':
            self.letters_update(context=context)
        elif wm.ACTION == 'games_update':
            self.games_update(context=context)
        elif wm.ACTION == 'models_update':
            self.models_update(context=context)
        elif wm.ACTION == 'import_model':
            self.import_model(context=context)
        elif wm.ACTION == 'download_model':
            self.download_model(context=context)
        return {'FINISHED'}

    def download_model(self, context):
        return download_model_context(self=self, context=context)

    def import_model(self, context):
        return import_model_context(self=self, context=context)

    def platform_update(self, context):
        print('updating platforms')
        for e in list(context.scene.platforms_collection): del context.scene.platforms_collection[e]
        # data = get_list(context.window_manager.url, "div", {"id": 'leftnav-consoles'})
        data = get_platforms(context.window_manager.url)
        for e in data:
            context.scene.platforms_collection[e] = data[e]
        return {'FINISHED'}

    def letters_update(self, context):
        """Return if platform url is invalid"""
        try:
            cur_platform = context.scene.platforms_dynamic
        except:
            cur_platform = ''
        if not cur_platform: return {'FINISHED'}
        try:
            data = get_list(cur_platform, "div", {"id": 'letters'})
        except:
            data = {'ALL': cur_platform}
        for e in list(context.scene.letters_collection): del context.scene.letters_collection[e]
        if 'ALL' in data or not data:
            context.scene.letters_collection['ALL'] = bpy.context.scene.platforms_dynamic
        else:
            for e in data:
                context.scene.letters_collection[e] = data[e]
        return {'FINISHED'}

    def games_update(self, context):
        wm = context.window_manager
        pcoll = preview_collections["games"]
        pcoll.games_previews_dir = ""

        preview_collections["games"] = pcoll

        return {'FINISHED'}

    def models_update(self, context):
        wm = context.window_manager
        pcoll = preview_collections["models"]
        pcoll.models_previews_dir = ''

        preview_collections["models"] = pcoll
        return {'FINISHED'}


"""END of button class"""


class MainPanel(Panel):
    """Creates a Panel in the View Layer properties window"""
    bl_label = "Models Resources"
    bl_idname = "Models_Resource_PT_previews"
    bl_category = "Models Resource"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "scene"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        row = layout.row()
        row.label(text=wm.Label)

        row = layout.row()
        row.prop(wm, "Root_Path")

        row = layout.row()
        row.prop(context.scene, "platforms_dynamic", text="Platform")
        # row.operator(Operators_OT_List.bl_idname, text='Refresh platforms').action = 'platform_update'

        row = layout.row()
        row.prop(context.scene, "letters_dynamic", text="Letter")
        # row.operator(Operators_OT_List.bl_idname, text='Refresh letters').action = 'letters_update'

        row = layout.row()
        row.template_icon_view(wm, "games_previews")

        row = layout.row()
        row.prop(wm, 'games_previews', text='Games')

        # row = layout.row()
        # row.operator(Operators_OT_List.bl_idname, text='Refresh games').action = 'games_update'

        row = layout.row()
        row.prop(context.scene, "Sections", text="Section")

        row = layout.row()
        row.template_icon_view(wm, 'models_previews')

        row = layout.row()
        row.prop(wm, 'models_previews', text='Name')

        # row = layout.row()
        # row.operator(Operators_OT_List.bl_idname, text='Refresh models').action = 'models_update'

        # row = layout.row()

        row = layout.row()
        row.prop(context.scene, "models_files", text="Files")

        row = layout.row()
        row.operator(DOWNLOAD_OT_test_op.bl_idname, text='Download')
        row.operator(IMPORT_MR_OT_test_op.bl_idname, text='Import', icon='IMPORT')
        #row.operator(Models_Resource_Operators_OT_List.bl_idname, text='Download').action = 'download_model'
        #row.operator(Models_Resource_Operators_OT_List.bl_idname, text='Import', icon='IMPORT').action = 'import_model'

    def execute(self, context):
        if context.scene.logging: print(f'MainPanel executed')

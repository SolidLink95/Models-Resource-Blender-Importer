from urllib.parse import urlparse

import bpy
import bpy.utils.previews
import os
import requests
import threading

from Models_Resource_Importer.Models_Resource_Soup import create_folder, extract_archive, getListOfFiles, save_file, get_platforms_thread, \
    get_letters_thread, get_games, get_models

preview_collections = {}
model_current = ''
BLANK_TUPLE = (('None','',''),)
BLANK_TUPLE_MODELS_FILES = (('Click Download','Click Download','Click Download'),)
BLANK_DICT_MODELS_FILES = {"Click Download" : "Click Download"}

def get_valid_models(self, context, directory):
    """returns list of importable models files"""
    wm = context.window_manager
    if not os.path.exists(directory): return []
    res = []
    files = getListOfFiles(directory)
    for file in files:
        for ext in wm.exts:
            if file.endswith(ext):
                res.append(file)
                break
    return res


def download_file_and_extract(self, context, link, file_name, directory):
    """Download file from provided link"""
    BASE = os.path.basename(file_name)
    wm = context.window_manager
    if not os.path.exists(file_name):
        
        with open(file_name, "wb") as f:
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                wm.progress_begin(0.0, 100.0)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = (dl*100) / total_length
                    wm.Label = f'{BASE}: {format(done, ".2f")}%'
                    wm.progress_update(done)
                wm.progress_end()
                    
                    
    if file_name.endswith('.zip'):
        wm.Label =  f'Extracting {BASE}...'
        if extract_archive(file_name, directory):
            print(f'Extracted {file_name} to {directory}')
            wm.Label =  f'Extracted {BASE}'
        else:
            wm.Label =  f'{BASE} already extracted'
        res = get_valid_models(self=self, context=context, directory=file_name[:-4])
        if res:
            for e in list(context.scene.models_files_collection): 
                del context.scene.models_files_collection[e]
        for e in res:
            context.scene.models_files_collection[e] = os.path.basename(e)

def import_by_extension(filepath):
    ff = filepath.lower()
    if ff.endswith('.fbx'): bpy.ops.import_scene.fbx(filepath=filepath)
    elif ff.endswith('.dae'): bpy.ops.wm.collada_import(filepath=filepath)
    elif ff.endswith('.obj'): bpy.ops.import_scene.obj(filepath=filepath)
    print(f'Attempted import {os.path.basename(filepath)} [{filepath}]')


def update_platforms(self, context):
    if context.scene.logging : print('Updating platforms')
    wm = context.window_manager
    if not context.scene.platforms_collection:
        if wm.Root_Path:
            create_folder(wm.Root_Path)
            wm.Label = 'Getting platforms...'
            thread = threading.Thread(target=get_platforms_thread, args=(self, context))
            thread.daemon = True
            thread.start()
            context.scene.platforms_collection[""] = 'None'
    try: return [(context.scene.platforms_collection[t], t, t) for t in context.scene.platforms_collection]
    except: return BLANK_TUPLE
        
    
def update_letters(self,context):
    """Updating letters, run constantly when cursor is close to combobox. 
    Does nothing if collection is not empty, returns blank tuple if something
    goes wrong"""
    if context.scene.logging: print('Updating letters')
    wm = context.window_manager
    try: cur_platform = context.scene.platforms_dynamic
    except: cur_platform = ''
    
    if not cur_platform: return BLANK_TUPLE #return nothing if platforms are not there yet

    if not context.scene.letters_collection or cur_platform != wm.platform_current: #if coll is empty then run thread
        wm.Label = 'Getting letters...'
        thread = threading.Thread(target=get_letters_thread, args=(self, context))
        thread.daemon = True
        thread.start()
        context.scene.letters_collection[""] = 'None'
        wm.platform_current = cur_platform
    try: return [(context.scene.letters_collection[t], t, t) for t in context.scene.letters_collection]
    except: return BLANK_TUPLE
      
    

def update_models_files(self, context):
    """Updating importable models files""" 
    if context.scene.logging: print('Updating models')
    wm = context.window_manager
    try: 
        cur_model = wm.model_current
        cur_model_preview = wm.models_previews
    except: return BLANK_TUPLE_MODELS_FILES
    
    
    if wm.model_current != wm.models_previews or context.scene.models_files_collection == BLANK_DICT_MODELS_FILES:
        try:
            cur_model_name = None
            directory = os.path.join(context.window_manager.Root_Path, 
                         urlparse(context.scene.letters_dynamic).path[1:].replace('.html','').replace('/','\\'), 
                         wm.games_previews.split('/')[-2],
                         context.scene.Sections,
                         'models'
                         )
            for e in preview_collections['models'].models_previews:
                if e[0] == wm.models_previews:
                    cur_model_name = e[1]
                    break 
            directory = os.path.join(directory, cur_model_name)
        except: 
            return BLANK_TUPLE_MODELS_FILES
        wm.model_current = wm.models_previews
        
        valid_models = get_valid_models(self=self, context=context, directory=directory)
        for e in list(context.scene.models_files_collection): del context.scene.models_files_collection[e]  
        if valid_models:
            for file in valid_models:
                context.scene.models_files_collection[file] = os.path.basename(file)
        else:
            context.scene.models_files_collection['Click Download'] = 'Click Download'
            return BLANK_TUPLE_MODELS_FILES
        return [(t, context.scene.models_files_collection[t], t) for t in context.scene.models_files_collection]
    elif wm.model_current == wm.models_previews:
        try: return [(t, context.scene.models_files_collection[t], t) for t in context.scene.models_files_collection]
        except: return BLANK_TUPLE_MODELS_FILES   
    else:
        return BLANK_TUPLE_MODELS_FILES   
    
def update_sections(self, context):
    if context.scene.logging: print('Updating sections')
    wm = context.window_manager
    try: cur_game = wm.games_previews
    except: cur_game = ''
    if not cur_game or cur_game == 'None': return BLANK_TUPLE
    res = []
    pcoll = preview_collections["models"]
    if not pcoll.models_data or pcoll.models_data == {"": "None"}: 
        pcoll.models_data = get_models(cur_game)
    for e in pcoll.models_data:
        sec = pcoll.models_data[e]['section']
        if not sec in res: res.append(sec)
    return [(s,s,s) for s in res]

def reset_models_collection():
    bpy.utils.previews.remove(preview_collections["models"])
    pcoll = bpy.utils.previews.new()
    pcoll.models_previews_dir = ''
    pcoll.pngs_number = 0
    pcoll.cur_section = ''
    pcoll.models_previews = BLANK_TUPLE#()
    pcoll.models_data = {"":"None"}
    preview_collections["models"] = pcoll
    return preview_collections["models"]    

def reset_games_collection():
    bpy.utils.previews.remove(preview_collections["games"])
    pcoll = bpy.utils.previews.new()
    pcoll.games_previews_dir = "" #This var is to prevent scanning the directory over and over again. Not drawn
    pcoll.pngs_number = 0 
    pcoll.cur_letter = 0 
    pcoll.games_previews = BLANK_TUPLE#()
    preview_collections["games"] = pcoll
    return preview_collections["games"]    

def save_files(self, context, items, class_type):
    wm = context.window_manager
    do_I_reset_col = False
    for link in items: 
        file_to_save = items[link]
        if not do_I_reset_col:
            if not os.path.exists(file_to_save): 
                do_I_reset_col = True
        save_file(link, file_to_save, overwrite=False)
        wm.Label = 'Downloading icon: ' + os.path.basename(file_to_save)
    wm.Label = 'Downloading icons complete'
    if do_I_reset_col:
        if class_type == 'games':
            reset_games_collection()
        elif class_type == 'models':
            #preview_collections["models"].models_previews_dir = ''
            reset_models_collection()
        
        print(f'Reseting collection for class type {class_type}')
        
                


def DownloadingIconsThread(self, context, items, class_type):
    wm = context.window_manager
    thread = threading.Thread(target=save_files, args=(self, context, items, class_type))
    thread.daemon = True
    thread.start()

    
def update_games(self,context):
    """Updating games previews collection. Does nothing if games_previews_dir is 
    empty/unchanged, or letter is empty/invalid string"""
    pcoll = preview_collections["games"]
    enum_items = []
    icons_for_download = {}
    cur_index=0
    """Return if cant access letter value"""
    try: cur_letter = context.scene.letters_dynamic
    except: cur_letter = ''
    if not cur_letter or cur_letter == 'None': return BLANK_TUPLE
    
    wm = context.window_manager
    
    directory = os.path.join(context.window_manager.Root_Path, urlparse(context.scene.letters_dynamic).path[1:].replace('.html','').replace('/','\\'))
    
    """Dont scan directory for pngs if the statement below is True"""
    if directory == pcoll.games_previews_dir: 
        return pcoll.games_previews
    
    """Reset games previews if there is at least 1 icon from outside of directory path"""
    for e in pcoll.games_previews:
        if not directory in e[2]:
            print(f'Resetting games coll.\n{directory} not in \n{e[2]}')
            pcoll = reset_games_collection()
            enum_items = []
            break    

    print("Scanning directory: %s" % directory)

    data = get_games(cur_letter)
    create_folder(directory)
    for e in data:
        data[e]['icon'] = os.path.join(directory, data[e]['name'] + '.png')
        icons_for_download[data[e]['img_src']] = data[e]['icon']
        
    DownloadingIconsThread(self=self, context=context, items=icons_for_download, class_type='games')
    
    for i, name in enumerate(data):
        filepath = data[name]['icon']
        if os.path.exists(filepath):
            try:
                thumb = pcoll.load(filepath, filepath, 'IMAGE')
                enum_items.append((data[name]['link'], name, filepath, thumb.icon_id, i))
            except: 
                print(f'Error appending image {filepath}')
            

    pcoll.cur_letter = cur_letter
    pcoll.games_previews = enum_items
    pcoll.games_previews_dir = directory
    return pcoll.games_previews




def update_models(self,context):
    wm = context.window_manager
    pcoll = preview_collections["models"]
    enum_items = []
    #if context.scene.models_icons_thread: print(context.scene.models_icons_thread.downloaded)
    """If section, game or letter value is invalid, return immediately"""
    try: cur_section = context.scene.Sections
    except: cur_section = ''
    if not cur_section or cur_section == 'None': return BLANK_TUPLE
    try: cur_letter = context.scene.letters_dynamic
    except: cur_letter = ''
    if not cur_letter or cur_letter == 'None': return BLANK_TUPLE
    try: cur_game = wm.games_previews
    except: cur_letter = ''
    if not cur_letter or cur_letter == 'None': return BLANK_TUPLE

    directory = os.path.join(context.window_manager.Root_Path, 
                             urlparse(context.scene.letters_dynamic).path[1:].replace('.html','').replace('/','\\'), 
                             wm.games_previews.split('/')[-2],
                             cur_section
                             )
    
    if cur_section == pcoll.cur_section: 
        enum_items = [m for m in pcoll.models_previews]
        for e in enum_items:
            if not directory in e[2]:
                pcoll = reset_models_collection()
                enum_items = []
                break
        cur_index = len(pcoll.models_previews)
        
    icons_for_download = {}
    if context is None: return enum_items
    
    create_folder(directory)
    
    """Dont scan directory for pngs if the statement below is True"""
    if directory == pcoll.models_previews_dir: 
        if cur_section == pcoll.cur_section: 
            return pcoll.models_previews
    
    print("Scanning directory: %s" % directory)

    data = get_models(wm.games_previews)
    create_folder(directory)
    
    for e in data:
        if cur_section == data[e]['section']:
            data[e]['icon'] = os.path.join(directory, data[e]['name'] + '.png')
            icons_for_download[data[e]['img_src']] = data[e]['icon']
    DownloadingIconsThread(self=self, context=context, items=icons_for_download, class_type='models')
    
    for i, name in enumerate(data):
        if cur_section == data[name]['section']:
            filepath = data[name]['icon']
            if os.path.exists(filepath):
                try:
                    thumb = pcoll.load(filepath, filepath, 'IMAGE')
                    enum_items.append((data[name]['link'], name, filepath, thumb.icon_id, i))
                except:
                    print(f'Error adding {filepath}')
                
    pcoll.models_previews = enum_items
    pcoll.models_previews_dir = directory
    pcoll.models_data = data
    pcoll.cur_section = cur_section
    return pcoll.models_previews
    
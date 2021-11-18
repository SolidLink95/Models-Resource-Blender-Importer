# Models-Resource-Blender-Importer
Importing 3D models from https://www.models-resource.com/ in Blender UI

### How to install

1. Download `InstallModelResource.blend` from latest release

2. Open Blender as an administrator 

   ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/1.png)

3. Go to `Scripting` tab and run the code (`Alt+P`) 

   ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/2.png)

4. Close window

5. Download zip file from the latest release (don't unzip!)

6. Open Blender, go to `Edit -> Preferences` 

   ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/3.png)

7. Go to `Addons` tab and click install

8. Select zip file downloaded in step 5.

9. Done, the addon is accessible here:  

   ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/4.png)

### Panel elements

 ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/5.png)

- A - label which informs about ongoing operations (downloading models, icons, extracting zip archives, etc)
- B - cache dir is a directory where models and icons are cached, so that those assets are downloaded only once, addon won't start as long as the field is empty
- C - platform: currently selected gaming platform
- D - letter: letters available for current platform
- E - game: games available for current letter
- F - sections: sections available for current game
- G - name: 3D models available for current game
- H - files: list importable 3D model files (empty if model hasn't been downloaded yet)
- I - download button: click to download current model, does nothing if model is already downloaded
- H - import: imports the file selected in H combobox, does nothing if model is not downloaded

### Usage

Addon requires Internet connection to work, since all fields are filled dynamically from the site. Wait until all fields fill by themselves, select platform, letter, game, section, model, download it and hit import. 

Addon uses multithreading, so Blender does not freeze during downloading assets and querying `models-resource` site

### Uninstalling

1. Open Blender, go to `Edit -> Preferences`
2. Go to `Addons` tab
3. Untick the box near `Models Resource Importer` and close Blender
4. Open Blender as an administrator
5. Open `UninstallModelResource.blend` and run code (`Alt+P`)
6. Close Blender

### Credits 

All credits go to the respective developers studios. No 3D model is included with addon. All credits for exporting the models go to the respective users of `models-resource`


# Models-Resource-Blender-Importer
Addon for importing 3D models from https://www.models-resource.com/ in Blender UI. Tested on versions 2.82 and 2.93

### Requiurements

- BeautifulSoup (bs4) - shipped with latest release (v. 4.9.3)

### How to install

Since Blender uses his own custom python release, requires packages must be installed using `InstallModelResource.blend` and uninstalled with `UninstallModelResource.blend` 

5. Download zip file from the latest release (don't unzip!)

6. Open Blender, go to `Edit -> Preferences` 

   ![alt text](https://github.com/banan039pl/Models-Resource-Blender-Importer/blob/main/images/3.png)

7. Go to `Addons` tab and click install

8. Select zip file downloaded in step 1.

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
6. Close Blender

### Credits 

All credits go to the respective developers studios. No 3D model is included with addon. All credits for exporting and uploading the models go to the respective users of `models-resource`


import os
import plistlib
from pathlib import Path
import math
from collections import OrderedDict
import re
import subprocess
from pprint import pprint

class Apps:
    def __init__(self):
        pass
    
    
    def get_file_plists(self):
        plist_path = '/Applications/{}/Contents/Info.plist'
        app_path = '/Applications'
        files_and_dirs = filter(lambda i: not i.startswith('.'), os.listdir(app_path))
        paths_fixed = [os.path.join(app_path, i) for i in files_and_dirs]
        files_, dirs_ = [i for i in paths_fixed if i.endswith('.app')], [i for i in paths_fixed if not i.endswith('.app') and not i==f'{app_path}/Utilities']
        all_files = [plist_path.format(i.split('/')[-1]) for i in files_] + [plist_path.format(i.split('/')[-1]) for i in dirs_]
        all_files = sorted(all_files, key=lambda i: i.split('/')[2].lower())
        return all_files
    
    def convert_size(self, file_size):
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        factor = 1024
        
        
        
    
    def get_app_info(self):
        app_info = OrderedDict()
        file_plists = self.get_file_plists()
        for _, file_path in enumerate(file_plists, start=1):
            try:
                file_name = file_path.split('/')[2]
                file = open(file_path, 'rb').read()
                info_plist = plistlib.loads(file)
                app_info[info_plist.get('CFBundleName', file_name)] = {
                                        'Version': info_plist.get('CFBundleShortVersionString', 'N/A'),
                                        'Minimum System Version': info_plist.get('LSMinimumSystemVersion', 'N/A'),
                                        'Size': os.path.getsize(file_path)
                                        }
            except FileNotFoundError:
                pass
        
        return app_info
        
    

    

def main():
    apps = Apps()
    pprint(apps.get_app_info())

if __name__ == '__main__':
    main()
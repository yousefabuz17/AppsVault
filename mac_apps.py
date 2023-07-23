import os
import plistlib
from pathlib import Path
from collections import OrderedDict



class Apps:
    def __init__(self):
        pass
    
    
    def get_file_plists(self):
        plist_path = '/Applications/{}/Contents/Info.plist'
        files_ = filter(lambda i: i.endswith('.app'), sorted(os.listdir('/Applications'), key=lambda i: i.lower()))
        files = list(plist_path.format(i) for i in files_)
        return files
    
    def convert_size(self, file):
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        factor = 1024.0
        for unit in size_units:
            if file < factor:
                return f"{file:.2f} {unit}"
            file /= factor
        
        return f"{file:.2f} {size_units[-1]}"
    
    def get_app_info(self):
        app_info = OrderedDict()
        file_plists = self.get_file_plists()
        for idx, file_path in enumerate(file_plists, start=1):
            file = open(file_path, 'rb').read()
            info_plist = plistlib.loads(file)
            app_info[f'Application {idx}'] = {
                                    'Name': info_plist.get('CFBundleName', 'N/A'),
                                    'Version': info_plist.get('CFBundleShortVersionString', 'N/A'),
                                    'Minimum System Version': info_plist.get('LSMinimumSystemVersion', 'N/A'),
                                    'Size': self.convert_size(os.path.getsize(file_path))
                                    }
        
        return app_info
        
    

    

def main():
    apps = Apps()
    print(apps.get_app_info())

if __name__ == '__main__':
    main()
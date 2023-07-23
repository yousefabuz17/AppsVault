import os
import plistlib
import json
from pathlib import Path
from collections import OrderedDict
from functools import lru_cache
from typing import NamedTuple
import psycopg


class ConfigInfo(NamedTuple):
    host: str
    dbname: str
    username: str
    password: str

class Apps:
    def __init__(self):
        pass
    
    @staticmethod
    def get_file_plists():
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
        unit = 0
        while file_size >= factor and unit < len(size_units) - 1:
            file_size /= factor
            unit += 1
        return f"{file_size:.2f} {size_units[unit]}"
    
    @lru_cache(maxsize=None)
    def get_app_info(self):
        app_info = OrderedDict()
        file_plists = self.get_file_plists
        for _, file_path in enumerate(file_plists(), start=1):
            try:
                file_name = file_path.split('/')[2]
                app_bundle_path = f'/Applications/{file_name}'
                app_bundle_size = sum(f.stat().st_size for f in Path(app_bundle_path).rglob('*') if f.is_file())
                file = open(file_path, 'rb').read()
                info_plist = plistlib.loads(file)
                app_info[info_plist.get('CFBundleName', file_name)] = {
                                        'Version': info_plist.get('CFBundleShortVersionString', None),
                                        'Minimum System Version': info_plist.get('LSMinimumSystemVersion', None),
                                        'Size': self.convert_size(app_bundle_size)
                                        }
            except FileNotFoundError:
                pass
        
        return app_info

class AppsDB:
    def __init__(self):
        self.connect = None
        self.cursor = None
        self.config = ConfigInfo(*json.load(open(Path(__file__).parent.absolute() / 'config.json')).values())
    
    def sql_connect(self):
        try:
            self.connect = psycopg.connect(
                host=self.config.host,
                dbname=self.config.dbname,
                username=self.config.username,
                password=self.config.password
            )
            self.cursor = self.connection.cursor
        except psycopg.errors.ConfigFileError:
            print('Check config file')

def main():
    apps = Apps()
    # all_apps_info = apps.get_app_info()
    apps_db = AppsDB()
    print(apps_db.config)

if __name__ == '__main__':
    main()
import json
import configparser
import os
import plistlib
from collections import OrderedDict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple
import platform
import psycopg


class ConfigInfo(NamedTuple):
    host: str
    dbname: str
    username: str
    password: str

@dataclass
class SQLScript:
    capps: str=None
    iapps: str=None

@dataclass
class AppInfo:
    name: str=None
    ver: str=None
    min_ver: str=None
    size: str=None

class MacApps:
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
    
    @staticmethod
    def convert_size(file_size):
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
                    'Minimum System Version': info_plist.get('LSMinimumSystemVersion', 0),
                    'Size': self.convert_size(app_bundle_size)}
            except FileNotFoundError:
                pass
        
        return app_info

class AppsDB:
    def __init__(self, data, config):
        self.connection = None
        self.cursor = None
        self.config = ConfigInfo(*config)
        self.sql_script = open(Path(__file__).parent.absolute() / 'apps_db.sql').read().split('\n\n')
        self.data = data
        self.system = self.modify_system(platform.system())
        self.sql_connect()
        self.create_tables()
    
    @staticmethod
    def modify_system(system):
        if system == 'Darwin':
            system = 'Mac'
            return system
        return system
    
    def modify_script(self, name):
        return name.replace('Applications', f'{self.system}_Applications')
    
    def sql_connect(self):
        try:
            self.connection = psycopg.connect(
                                host=self.config.host,
                                dbname=self.config.dbname,
                                user=self.config.username,
                                password=self.config.password
                                )
            self.cursor = self.connection.cursor()
        except (psycopg.errors.ConfigFileError, psycopg.Error, FileNotFoundError) as e:
            print(f"An error occurred while connecting to the database: {e}")
            raise e

    def create_tables(self):
        global apps_table
        table_name = self.modify_script(self.sql_script[0])
        insert_table_name = self.modify_script(self.sql_script[1])
        apps_table = SQLScript(capps=table_name, iapps=insert_table_name)
        self.cursor.execute(apps_table.capps)
        self.connection.commit()
        self.update_db()
    
    def update_db(self):
        data = self.data
        insert_query = apps_table.iapps
        
        for app, info in data.items():
            app_data = AppInfo(name=app,
                                ver=info['Version'],
                                min_ver=info['Minimum System Version'],
                                size=info['Size'])
            
            self.cursor.execute(insert_query, (app_data.name,
                                                app_data.ver,
                                                app_data.min_ver,
                                                app_data.size))
        self.connection.commit()
    
    def close_db(self):
        if self.connection:
            try:
                self.connection.rollback()
                # print("Transaction rollback completed.")
            except psycopg.Error as e:
                print(f"An error occurred during transaction rollback: {e}")
        if self.cursor:
            self.cursor.close()
            print(f"{self.system} Database Updated Successfully")
        if self.connection:
            self.connection.close()
            print("Database Server Closed")
    
    def __del__(self):
        self.close_db()

class LinuxApps:
    def __init__(self):
        pass
    
    @lru_cache(maxsize=None)
    def get_desktop_info(self):
        apps_path = '/usr/share/applications'
        files = [i for i in Path(apps_path).rglob('*') if i.endswith('.desktop')]
        desktop_info = OrderedDict()
        for _, _ in enumerate(files, start=1):
            app_config = configparser.ConfigParser()
            app_config.read(app_config)
            executable_path = app_config.get('Desktop Entry', 'Exec').split()[0]
            
            if os.path.isfile(executable_path):
                app_size = os.path.getsize(executable_path)
            else:
                app_size = 0
            
            desktop_info[app_config.get('Desktop Entry', 'Name')] = {
                                        'Version': app_config.get('Desktop Entry', 'Version'),
                                        'Size': MacApps.convert_size(app_size)}
        return desktop_info

def main(system):
    config = json.load(open(Path(__file__).parent.absolute() / 'config.json')).values()
    
    match system:
        case 'Darwin':
            apps = MacApps()
            all_apps = apps.get_app_info()
            AppsDB(data=all_apps, config=config)
        case 'Linux':
            apps = LinuxApps()
            all_apps = apps.get_desktop_info()
            AppsDB(data=all_apps, config=config)
        case 'Windows':
            pass
        case _:
            return ''

if __name__ == '__main__':
    system = platform.system()
    main(system)
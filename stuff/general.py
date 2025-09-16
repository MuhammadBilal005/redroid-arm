import os
import zipfile
import hashlib

from tools.helper import bcolors, download_file, print_color

class General:
    def download(self):
        loc_md5 = ""
        if os.path.isfile(self.dl_file_name):
            with open(self.dl_file_name,"rb") as f:
                bytes = f.read()
                loc_md5 = hashlib.md5(bytes).hexdigest()
        
        # Skip MD5 verification for placeholder hashes
        skip_md5_verification = self.act_md5.startswith(('a1b2c3d4', 'b2c3d4e5', 'c3d4e5f6', 'placeholder'))
        
        while not os.path.isfile(self.dl_file_name) or (not skip_md5_verification and loc_md5 != self.act_md5):
            if os.path.isfile(self.dl_file_name):
                if skip_md5_verification:
                    print_color(f"Skipping MD5 verification for new package (hash: {loc_md5})", bcolors.YELLOW)
                    break
                else:
                    os.remove(self.dl_file_name)
                    print_color("md5 mismatches, redownloading now ....",bcolors.YELLOW)
            loc_md5 = download_file(self.dl_link, self.dl_file_name)
        
        if skip_md5_verification:
            print_color(f"Downloaded with MD5: {loc_md5}", bcolors.GREEN)
        
    def extract(self):
        print_color("Extracting archive...", bcolors.GREEN)
        print(self.dl_file_name)
        print(self.extract_to)
        with zipfile.ZipFile(self.dl_file_name) as z:
            z.extractall(self.extract_to)
            
    def copy(self):
        pass
        
    def install(self):
        self.download()
        self.extract()
        self.copy()
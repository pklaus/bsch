import ftplib
import collections
import os
import io
from typing import Union

File = collections.namedtuple("File", ("permissions", "linkcount", "user", "group", "size", "month", "day", "time", "name"))

class FTP(ftplib.FTP):
    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            # using the default host:
            ftplib.FTP.__init__(self, "192.168.1.1", *args, **kwargs)
        else:
            # custom call overriding the first argument ("host"):
            ftplib.FTP.__init__(self, *args, **kwargs)
        self.cwd("IMAGE")

    def list_files(self):
        files = []
        def callback(line):
            files.append(File(*line.split()))
        self.dir(callback)
        return files


    def download(self, file: Union[str, File], fp=None):
        if type(file) == File:
            file = file.name
        if fp is None:
            fp = io.BytesIO()
        self.retrbinary(f"RETR IMAGE/{file}", fp.write, blocksize=8192)
        fp.seek(0)
        return fp

    # The GTC 400 C doesn't support many commands. It then responds with
    # > 202 Command not implemented, superfluous at this site.

    def delete(self, filename):
        raise NotImplementedError()

    def rename(self, fromname, toname):
        raise NotImplementedError()

    def mlsd(self, path="", facts=[]):
        raise NotImplementedError()

    def nlst(*args):
        raise NotImplementedError()

def main():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--folder", default=".", help="Target folder for downloaded images.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    with FTP() as gtc400c:
        files = gtc400c.list_files()
        for file in files:
            target_path = os.path.join(args.folder, file.name)
            if os.path.exists(target_path) and not args.force:
                print(f"{file.name} - already downloaded - skipping...")
                continue
            with open(target_path, 'wb') as fp:
                gtc400c.download(file, fp=fp)
                print(f"{file.name} - download complete")

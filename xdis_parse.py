import os
import subprocess
import xdis.load
import xdis.std as dis

class xdisBytecode:
    filename = None
    code = None
    constants = None
    name = None

    @classmethod
    def from_file(self, path:str):
        if not os.path.exists(path):
            raise FileNotFoundError
        (version, timestamp, magic_int, co, is_pypy, source_size, sip_hash) = xdis.load.load_module(path)
        return xdisBytecode(co, co.co_filename)

    def __init__(self, co:code, filename:str):
        self.filename = filename
        self.code = list(dis.get_instructions(co))
        self.name = co.co_name
        self.constants = co.co_consts

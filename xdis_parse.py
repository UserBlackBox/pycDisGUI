import os
import xdis.load
import xdis.std as dis
from xdis import iscode


class XdisBytecode:
    filename = ""
    code = []
    constants = ()
    name = ""
    sub = []

    @classmethod
    def from_file(self, path:str):
        if not os.path.exists(path):
            raise FileNotFoundError
        (version, timestamp, magic_int, co, is_pypy, source_size, sip_hash) = xdis.load.load_module(path)
        return XdisBytecode(co, co.co_filename, True)

    def __init__(self, co:code, filename:str, file_as_name:bool):
        self.filename = filename
        self.code = list(dis.get_instructions(co))
        self.name = co.co_name
        if file_as_name:
            self.name = filename
        self.constants = co.co_consts
        self.sub = []

        for const in co.co_consts:
            if iscode(const):
                self.sub.append(XdisBytecode(const, filename, False))

    def get_bytecode(self):
        code = ""
        for instruction in self.code:
            if instruction.starts_line:
                if len(code)!=0: code+="\n"
                code += str(instruction.starts_line) + ':'
            code += "\t"
            code += str(instruction.offset)
            code += "\t"
            code += instruction.opname
            code += "\t\t"
            code += instruction.argrepr
            code += "\n"
        return code

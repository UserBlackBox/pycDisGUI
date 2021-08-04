import os
import xdis
import xdis.load
import xdis.std as dis
from xdis import iscode
import html


class XdisBytecode:
    filename = ""
    code = []
    constants = ()
    name = ""
    sub = []
    co = None

    @classmethod
    def from_file(self, path:str):
        if not os.path.exists(path):
            raise FileNotFoundError
        (version, timestamp, magic_int, co, is_pypy, source_size, sip_hash) = xdis.load.load_module(path)
        filename = co.co_filename.split('/')[-1].split('\\')[-1]
        return XdisBytecode(co, filename, True)

    def __init__(self, co:code, filename:str, file_as_name:bool):
        self.filename = filename
        self.code = list(dis.get_instructions(co))
        self.name = co.co_name
        if file_as_name:
            self.name = filename
        self.constants = co.co_consts
        self.sub = []
        self.co = co

        for const in co.co_consts:
            if iscode(const):
                self.sub.append(XdisBytecode(const, filename, False))

    def get_bytecode(self, linenum=True, jumps=True):
        code = ""
        for instruction in self.code:
            if linenum:
                if instruction.starts_line:
                    if len(code)!=0: code+="\n"
                    code += html.escape(str(instruction.starts_line)) + ':'
                code += "\t"
            if jumps:
                if instruction.is_jump_target: code += html.escape(">>> ")
                else: code += "    "
            code += html.escape(str(instruction.offset))
            code += "\t<b>"
            code += html.escape(instruction.opname)
            code += "</b>"
            if len(instruction.opname)<8: code += "\t"
            if len(instruction.opname)<16: code += "\t\t"
            else: code += "\t"
            if iscode(instruction.argval): code += html.escape("<code object {}>".format(instruction.argval.co_name))
            elif len(instruction.argrepr) != 0: code += html.escape(instruction.argrepr)
            elif instruction.argval != None: code += html.escape(str(instruction.argval))
            code += "\n"
        return code

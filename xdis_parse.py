import os
import xdis
import xdis.load
import xdis.std as dis
from xdis import iscode
import html
from datetime import datetime


class XdisBytecode:
    filename = ""
    code = []
    constants = ()
    name = ""
    sub = []
    co = None
    is_file = False
    version = None
    timestamp = None
    is_pypy = None
    source_size = None

    @classmethod
    def from_file(self, path:str):
        if not os.path.exists(path):
            raise FileNotFoundError
        (version, timestamp, magic_int, co, is_pypy, source_size, sip_hash) = xdis.load.load_module(path)
        filename = co.co_filename.split('/')[-1].split('\\')[-1]
        return XdisBytecode(co, filename, True, version, timestamp, magic_int, source_size)

    def __init__(self, co:code, filename:str, file_as_name:bool, version=None, timestamp=None, is_pypy=None, source_size=None):
        self.filename = filename
        self.code = list(dis.get_instructions(co))
        self.name = co.co_name
        self.constants = co.co_consts
        self.sub = []
        self.co = co
        self.is_file = file_as_name
        self.version = version
        self.timestamp = timestamp
        self.is_pypy = is_pypy
        self.source_size = source_size

        for const in co.co_consts:
            if iscode(const):
                self.sub.append(XdisBytecode(const, filename, False))

    def get_bytecode(self, linenum=True, jumps=True) -> str:
        code = ""
        for instruction in self.code:
            if linenum:
                if instruction.starts_line:
                    if len(code)!=0: code+="\n"
                    code += html.escape(str(instruction.starts_line)) + ':'
                code += "\t"
            if jumps:
                if instruction.is_jump_target: code += html.escape(">> ")
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

    def get_details(self) -> str:
        details = ""

        if self.is_file:
            details += "<b>Python Version:</b> " + str(self.version) + "\n"
            details += "<b>Timestamp:</b> " + str(self.timestamp)
            details += ' ({})\n'.format(str(datetime.fromtimestamp(self.timestamp)))
            details += "<b>Source Code Size:</b> {} bytes\n".format(self.source_size)
            details += "\n"

        details += "<b>Filename:</b> {}\n".format(self.filename)
        details += "<b>Method Name:</b> {}\n".format(html.escape(self.name))
        details += "<b>Argument Count:</b> {}\n".format(self.co.co_argcount)
        details += "<b>Position-Only Argument Count:</b> {}\n".format(self.co.co_posonlyargcount)
        details += "<b>Keyword-Only Argument Count:</b> {}\n".format(self.co.co_kwonlyargcount)
        details += "<b>Number of Locals:</b> {}\n".format(self.co.co_nlocals)
        details += "<b>Stack Size:</b> {}\n".format(self.co.co_stacksize)

        flags = []
        flag_num = self.co.co_flags
        for flag in sorted(xdis.COMPILER_FLAG_NAMES.keys())[::-1]:
            if flag <= flag_num:
                flags.append(xdis.COMPILER_FLAG_NAMES[flag])
                flag_num -= flag
        details += "<b>Flags:</b> {} ({})\n".format(hex(self.co.co_flags), " | ".join(flags))

        details += "<b>First Line:</b> {}\n".format(self.co.co_firstlineno)

        if len(self.co.co_names) > 0:
            details += "\n<b>Names:</b>\n"
            for i in range(len(self.co.co_names)):
                details += "\t{}: {}\n".format(i, self.co.co_names[i])

        if len(self.co.co_varnames) > 0:
            details += "\n<b>Varnames:</b>\n"
            for i in range(len(self.co.co_varnames)):
                details += "\t{}: {}\n".format(i, self.co.co_varnames[i])

        if self.co.co_argcount > 0:
            details += "\n<b>Positional Arguments:</b>\n"
            for i in range(self.co.co_argcount):
                details += "\t{}: {}\n".format(i, self.co.co_varnames[i])

        if len(self.co.co_varnames) > self.co.co_argcount:
            details += "\n<b>Local Variables:</b>\n"
            for i in range(len(self.co.co_varnames) - self.co.co_argcount):
                details += "\t{}: {}\n".format(self.co.co_argcount + i, self.co.co_varnames[self.co.co_argcount + i])

        return details

    def get_consts(self) -> str:
        consts = ""
        for i, const in enumerate(self.co.co_consts):
            if isinstance(const, str):
                const = "'{}'".format(const).replace("\n", "\\n").replace("\t", "\\t")
            consts += "{}: {}\n".format(i, const)
        return consts

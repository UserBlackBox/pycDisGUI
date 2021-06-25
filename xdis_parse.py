import os
import subprocess

class xdisBytecode:
    bytecode = ""
    filename = ""

    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        self.bytecode = subprocess.check_output(['pydisasm', path]).decode('UTF-8')

        for line in self.bytecode.split("\n"):
            if line.startswith('# Filename:'):
                self.filename = line[11:].strip()
                break

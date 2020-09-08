# This file is part of Rubber and thus covered by the GPL
# (c) Emmanuel Beffara, 2004--2006
# vim: noet:ts=4
"""
Common support for makeindex and xindy external tools.
"""

import os
import logging
msg = logging.getLogger(__name__)
import rubber.depend
from rubber.util import _

# FIXME: this class may probably be simplified a lot if inheriting
# from rubber.depend.Shell instead of rubber.depend.Node.


class Index(rubber.depend.Node):
    """
    This class represents a single index.
    """

    def __init__(self, doc, source, target, transcript):
        """
        Initialize the index, by specifying the source file (generated by
        LaTeX), the target file (the output of makeindex) and the transcript
        (e.g. .ilg) file.  Transcript is used by glosstex.py.
        """
        super().__init__()
        src = doc.basename(with_suffix="." + source)
        tgt = doc.basename(with_suffix="." + target)
        log = doc.basename(with_suffix="." + transcript)
        doc.add_product(src)
        self.add_product(tgt)
        self.add_product(log)
        self.add_source(src)
        doc.add_source(tgt)
        self.doc = doc
        self.cmd = ["makeindex", src, "-q", "-o", tgt, "-t", log]
        self.lang = None  # only for xindy
        self.modules = []  # only for xindy
        self.opts = []
        self.path = []
        self.style = None  # only for makeindex
        self.command_env = None

    def do_language(self, args):
        if len(args) != 1:
            raise rubber.SyntaxError(_("invalid syntax for directive '%s'") % args)
        lang = args[0]
        self.lang = lang

    def do_modules(self, args):
        self.modules.extend(args)

    def do_order(self, args):
        for opt in args:
            if opt == "standard":
                self.opts = []
            elif opt == "german":
                self.opts.append("-g")
            elif opt == "letter":
                self.opts.append("-l")
            else:                msg.warning(
                    _("unknown option '%s' for 'makeidx.order'") % opt)

    def do_path(self, args):
        if len(args) != 1:
            raise rubber.SyntaxError(_("invalid syntax for directive '%s'") % "path")
        path = args[0]
        self.path.append(path)

    def do_style(self, args):
        if len(args) != 1:
            raise rubber.SyntaxError(_("invalid syntax for directive '%s'") % "style")
        style = args[0]
        self.style = style

    def do_tool(self, args):
        if len(args) != 1:
            raise rubber.SyntaxError(_("invalid syntax for directive '%s'") % "tool")
        tool = args[0]
        if tool not in ("makeindex", "xindy"):
            msg.error(_("unknown indexing tool '%s'") % tool)
        self.cmd[0] = tool

    def run(self):
        # No more settings are expected, we compute the
        # command once and for all.
        if self.command_env == None:
            if self.cmd[0] == "makeindex":
                self.cmd.extend(self.opts)
                if self.style:
                    self.cmd.append('-s')
                    self.cmd.append(self.style)
                path_var = "INDEXSTYLE"
            else:  # self.cmd [0] == "texindy"
                for opt in self.opts:
                    if opt == "-g":
                        if self.lang != "":
                            msg.warning(_("'language' overrides 'order german'"))
                        else:
                            self.lang = "german-din"
                    else:  # opt == "-l"
                        self.modules.append("letter-ordering")
                        msg.warning(_("use 'module letter-ordering' instead of 'order letter'"))
                for mod in self.modules:
                    self.cmd.append('--module')
                    self.cmd.append(mod)
                if self.lang:
                    self.cmd.append('--language')
                    self.cmd.append(self.lang)
                path_var = "XINDY_SEARCHPATH"

            if self.path != []:
                self.command_env = {path_var: ':'.join(self.path + [os.getenv(path_var, '')])}
            else:
                self.command_env = {}

        # The actual run.
        return rubber.util.execute(self.cmd, env=self.command_env) == 0

# This file is part of Rubber and thus covered by the GPL
# (c) Emmanuel Beffara, 2002--2005
"""
VTeX support for Rubber.

This module specifies that the VTeX/Free compiler should be used. This
includes using "vlatex" of "vlatexp" instead of "latex" and knowing that this
produces a PDF or PostScript file directly. The PDF version is used by
default, switching to PS is possible by using the module option "ps".
"""

import rubber

class Module (rubber.rules.latex.Module):
	def __init__ (self, doc, dict):
		doc.conf.tex = "VTeX"
		if dict['opt'] == "ps":
			if doc.env.final != doc and doc.prods[0][-4:] != ".ps":
				msg.error(_("there is already a post-processor registered"))
				sys.exit(2)
			doc.conf.latex = "vlatexp"
			doc.prods = [doc.src_base + ".ps"]
		else:
			if doc.env.final != doc and doc.prods[0][-4:] != ".pdf":
				msg.error(_("there is already a post-processor registered"))
				sys.exit(2)
			doc.conf.latex = "vlatex"
			doc.prods = [doc.src_base + ".pdf"]
		doc.conf.cmdline = ["-n1", "@latex", "%s"]
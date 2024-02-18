# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "modal-paginator"
copyright = "2023, Soheab_"
author = "Soheab_"
release = "1.3.0a"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "enum_tools.autoenum",
]


templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "sphinx_rtd_theme"
html_theme = "furo"
# These folders are copied to the documentation's HTML output
html_static_path = ["_static"]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "css/custom.css",
]
html_theme_options = {
    # "collapse_navigation": True,
    # "sticky_navigation": True,
    #    "navigation_depth": 2,
    # "titles_only": False,
}
autodoc_default_options = {
    "members": True,
    #'undoc-members': False,
    #'inherited-members': True,
    "special-members": False,
    "exclude-members": "from_dict, to_dict, construct, __init__, _data, _http, __http, http",
}
# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "discord": ("https://discordpy.readthedocs.io/en/latest/", None),
}

# fmt: off
# what this basically does it shorten the commit hash to 7 characters...
# i couldn't find a better way to do this. please help me if you know how to do this better.
class FormatCommitHash:  # noqa
    def __new__(cls):# -> Any:
        # fixes the following error:
        # _pickle.PicklingError: Can't pickle <class 'FormatCommitHash'>: attribute lookup FormatCommitHash on builtins failed
        # please don't ask me why this works, i don't know either. Found it here: https://stackoverflow.com/a/17329487
        # yes, i moved it here so it looks better.
        import __main__
        setattr(__main__, cls.__name__, cls)
        cls.__module__ = "__main__" 
        return super().__new__(cls)

    def __mod__(self, spec: str) -> str:
        return f"({spec[:7]})"

# fmt: on

extlinks = {
    "commit": ("https://github.com/Soheab/modal-paginator/commit/%s", FormatCommitHash()),
}


del FormatCommitHash


viewcode_follow_imported_members = True
autoclass_signature = "separated"
autodoc_typehints_format = "short"
autodoc_member_order = "alphabetical"
autoclass_content = "class"
autodoc_typehints_description_target = "documented_params"
always_document_param_types = False
sphinx_autodoc_typehints = True
typehints_use_signature_return = False
napoleon_use_param = True
autodoc_typehints = "none"
autodoc_class_signature = "separated"
typehints_use_signature = False
extlinks_detect_hardcoded_links = True

nitpicky = True
nitpick_ignore = [
    ("py:class", "_io.BytesIO"),
    ("py:class", "discord.ext.modal_paginator.core.TextInpT"),
    ("py:class", "typing_extensions.Self"),
]

# Configuration file for the Sphinx documentation builder.

project = 'Face Scanning Using Python'
copyright = '2025, Your Name'
author = 'Your Name'

release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',   # for Google/NumPy-style docstrings
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages'
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

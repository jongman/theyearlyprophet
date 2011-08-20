from fabric.api import local

def build():
    local("pelican contents -s settings.py -t theme")

def watch():
    local("pelican contents -s settings.py -t theme -r")


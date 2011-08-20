from fabric.api import local

def build():
    local("pelican contents -s settings.py -t theme")

def build2():
    local("pelican contents -s settings.py -t notmyidea")

from fabric.api import local

def dev():
    local("rm -rf output/*")
    local("pelican contents -s settings.py -t theme")
    local("rm -rf output/theme")
    local("ln -sf theme/static output/theme")

def build():
    local("pelican contents -s settings.py -t theme")

def build2():
    local("pelican contents -s settings.py -t notmyidea")

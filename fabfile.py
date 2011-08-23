from fabric.api import local

def build():
    local("pelican contents -s settings.py -t theme")

def watch():
    local("pelican contents -s settings.py -t theme -r")

def publish():
    build()
    local("cd output && s3cmd sync * s3://theyearlyprophet.com/")


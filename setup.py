from distutils.core import setup

setup(name = "CryptBox",
    version = "0.1",
    description = "Tool for synchronizing files supporting encryption",
    author = "Jochen Skulj",
    author_email = "jochen@jochenskulj.de",
    url = "https://github.com/joskulj/cryptbox/",
    packages = ['cryptbox'],
    scripts = ["cryptbox-runner"],
    long_description = """Really long text here.""" 
) 

from distutils.core import setup

setup(name = "cryptbox",
    version = "0.2",
    description = "Tool for synchronizing files supporting encryption",
    author = "Jochen Skulj",
    author_email = "jochen@jochenskulj.de",
    url = "https://github.com/joskulj/cryptbox/",
    packages = ["cryptbox"],
    package_data = { "cryptbox" : ["*.glade"] },
    scripts = ["cryptbox-runner"],
    long_description = """Really long text here.""" 
) 

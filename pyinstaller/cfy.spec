# -*- mode: python -*-
import os
import pkg_resources
from platform import system
from PyInstaller.hooks.hookutils import get_package_paths, collect_submodules


def Entrypoint(dist, group, name, distributions,
               scripts=None, pathex=None, hiddenimports=None,
               hookspath=None, excludes=None, runtime_hooks=None):
    import pkg_resources

    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        return list(distribution.get_metadata('top_level.txt').split())

    packages = []
    for distribution in distributions:
        packages += get_toplevel(distribution)

    scripts = scripts or []
    pathex = pathex or []
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    pathex = [ep.dist.location] + pathex
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(WORKPATH, name + '-script.py')
    print "creating script for entry point", dist, group, name
    with open(script_path, 'w') as fh:
        fh.write("import {0}\n".format(ep.module_name))
        fh.write("{0}.{1}()\n".format(ep.module_name, '.'.join(ep.attrs)))
        for package in packages:
            fh.write("import {0}\n".format(package))

    return Analysis([script_path] + scripts, pathex, hiddenimports, hookspath, excludes, runtime_hooks)

if 'Windows' == system():
    binary_name = 'cfy.exe'
else:
    binary_name = 'cfy'

# add keystoneclient & novaclient egg-info directories to TOC for metadata
# support (pyinstaller doesn't support egg dirs yet)
keystoneclient = pkg_resources.get_distribution('python_keystoneclient')
keystoneclient_egg = keystoneclient.egg_name() + '.egg-info'
keystoneclient_tree = Tree(keystoneclient.location + '/' + keystoneclient_egg, keystoneclient_egg)

novaclient = pkg_resources.get_distribution('python_novaclient')
novaclient_egg = novaclient.egg_name() + '.egg-info'
novaclient_tree = Tree(novaclient.location + '/' +  novaclient_egg,  novaclient_egg)

cinderclient = pkg_resources.get_distribution('python_cinderclient')
cinderclient_egg = cinderclient.egg_name() + '.egg-info'
cinderclient_tree = Tree(cinderclient.location + '/' +  cinderclient_egg,  cinderclient_egg)

hidden_plugins = ['cloudify-openstack-plugin', 'cloudify-fabric-plugin', 'cloudify-plugins-common', 'cloudify-openstack-provider']

a = Entrypoint('cloudify', 'console_scripts', 'cfy',
               distributions=hidden_plugins,
               hookspath=['./hooks'])

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=binary_name,
          debug=False,
          strip=None,
          upx=True,
          console=True)
coll = COLLECT(exe,
               keystoneclient_tree,
               novaclient_tree,
               cinderclient_tree,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='cfy')

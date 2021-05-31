from types import SimpleNamespace
from pathlib import Path
import inspect

from .utils import resolve_scad_filename, escape_openscad_identifier
from .parse_scad import get_scad_file_as_dict

# ===========================
# = IMPORTING OPENSCAD CODE =
# ===========================
module_cache_by_resolved_filename = {}
registered_fonts = []

def check_module_cache(resolved_scad, use_not_include):
    global module_cache_by_resolved_filename

    #check the module cache for the requested module
    if resolved_scad in module_cache_by_resolved_filename.keys():
        cache_entry = module_cache_by_resolved_filename[resolved_scad]

        #if this is a include call and the module was only used until now
        #set the "use/include" flag in the module cache
        if not use_not_include and cache_entry[1]:
            cache_entry[1] = False

        return cache_entry[0]

def update_module_cache(resolved_scad, new_namespace_dict, use_not_include):
    global module_cache_by_resolved_filename
    module_cache_by_resolved_filename[resolved_scad] = \
                                        [new_namespace_dict, use_not_include]

def load_scad_file_into_dict(resolved_scad, dest_namespace_dict, use_not_include):
    #check the cache
    cached_dict = check_module_cache(resolved_scad, use_not_include)
    if cached_dict:
        dest_namespace_dict.update(cached_dict)
        return dest_namespace_dict

    #otherwise parse the file
    new_namespace_dict = get_scad_file_as_dict(resolved_scad)
    dest_namespace_dict.update(new_namespace_dict)

    #and update the cache
    update_module_cache(resolved_scad, new_namespace_dict, use_not_include)

def load_scad_dir_into_dict(resolved_scad, dest_namespace_dict, use_not_include):
    assert(resolved_scad.is_dir())

    #for each file in the dir
    for f in resolved_scad.iterdir():
        #skip non .scad files
        if f.suffix != ".scad":
            continue

        #load it
        subspace = ExpSolidNamespace(f)
        load_scad_file_or_dir_into_dict(f, subspace.__dict__, use_not_include)

        #and add it to the dest_namespace_dict
        identifier = escape_openscad_identifier(f.stem)
        dest_namespace_dict[identifier] = subspace

def load_scad_file_or_dir_into_dict(filename, dest_namespace_dict, use_not_include):
    assert(dest_namespace_dict != None)

    resolved_scad = resolve_scad_filename(filename)

    if not resolved_scad or not resolved_scad.exists():
        raise ValueError(f'Could not find .scad file {filename}.')

    if resolved_scad.is_file():
        load_scad_file_into_dict(resolved_scad,
                                 dest_namespace_dict,
                                 use_not_include)
    elif resolved_scad.is_dir():
        load_scad_dir_into_dict(resolved_scad,
                                dest_namespace_dict,
                                use_not_include)

# use() & include() mimic OpenSCAD's use/include mechanics.
# -- use() makes methods in scad_file_path.scad available to be called.
# --include() makes those methods available AND executes all code in
#   scad_file_path.scad, which may have side effects.
#   Unless you have a specific need, call use().
def get_callers_namespace_dict(depth=2):
    frame = inspect.currentframe()
    for i in range(depth):
        frame = frame.f_back

    if frame.f_code.co_name == "<module>":
        return frame.f_locals
    else:
        raise Exception("use & include can not be used inside a function!\n" +\
              "they would polute the modules namespace and only if executed. This\n" +\
              "has strange side effects! Use them on module level.\n")

        return frame.f_globals

def use(filename):
    #is this a font to register?
    p_file = Path(filename)
    if p_file.suffix == ".ttf" or p_file.suffix == ".otf":
        global registered_fonts
        registered_fonts += [p_file]
        return

    #otherwise load the scad file
    load_scad_file_or_dir_into_dict(filename, get_callers_namespace_dict(), True)

def include(filename):
    load_scad_file_or_dir_into_dict(filename, get_callers_namespace_dict(), False)

def import_scad(filename, dest_namespace=None, use_not_include=True):
    if dest_namespace == None:
        dest_namespace = ExpSolidNamespace(filename)

    load_scad_file_or_dir_into_dict(filename, dest_namespace.__dict__, use_not_include)

    return dest_namespace

# ========================
# = our helper namespace =
# ========================
class ExpSolidNamespace(SimpleNamespace):
    """
    we create our own namespace class for imported openscad modules to be able
    to overwrite the __repr__ func. This enables in a python shell

        s = import_scad("...")
        print(s)

    to list the "contents" of this namespace
    """
    def __init__(self, filename):
        super().__init__()
        self.__filename__ = filename

    def __repr__(self):
        node_strings = []
        for k in sorted(self.__dict__):
            if not k.startswith("__"):
                i = self.__dict__[k]
                if isinstance(i, ExpSolidNamespace):
                    node_strings += [f'\t{k}']
                else:
                    node_strings += [f'\t{i.__doc__}']

        return '\n'.join([f'{self.__filename__}:'] + node_strings)


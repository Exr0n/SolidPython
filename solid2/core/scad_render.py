from pathlib import Path

from .scad_import import module_cache_by_resolved_filename
from ..config import config

# =========================================
# = Rendering Python code to OpenSCAD code=
# =========================================
def render_to_stl_file(root, filename):
    scad_render_to_file(root, Path(filename).with_suffix(".stl.scad"))

    import subprocess
    args = ["openscad", "-o", filename, Path(filename).with_suffix(".stl.scad")]
    cp = subprocess.run(args, stdout=subprocess.PIPE)

    if cp.returncode == 0:
        return Path(filename).absolute().as_posix()

    return None

def scad_render(root, file_header = ''):
    #get a list of all used and included files
    includes = get_include_string()

    #call extensions pre_render
    from .extension_manager import default_extension_manager
    extensions_header_str = default_extension_manager.call_pre_render(root)
    extensions_header_str += "\n" if extensions_header_str else ''

    #wrap the extensions around the root node
    root = default_extension_manager.wrap_root_node(root)

    scad_body = root._render()

    #call extensions post_render
    extensions_footer_str = default_extension_manager.call_post_render(root)
    extensions_footer_str += "\n" if extensions_footer_str else ''

    return file_header + includes + extensions_header_str + scad_body \
                       + extensions_footer_str

def scad_render_to_file(scad_object, filename=None, out_dir=''):

    if out_dir == None:
        out_dir = ''
    header = f"// Generated by ExpSolidPython\n" + "\n"

    rendered_string = scad_render(scad_object)

    return _write_to_file(rendered_string, filename, out_dir)

def _write_to_file(out_string, filename=None, outdir=''):
    outfile = filename

    if not outfile:
        suffix = ".scad" if not config.use_implicit_builtins else ".escad"

        #try to get the filename of the calling module
        import __main__
        if hasattr(__main__, "__file__"):
            #not called from a terminal
            calling_file = Path(__main__.__file__).absolute()
            outfile = calling_file.with_suffix(suffix)
        else:
            outfile = "expsolid_out" + suffix

    outpath = Path(outdir)
    if not outpath.exists():
        outpath.mkdir()

    outfile_path = outpath / Path(outfile)

    outfile_path.write_text(out_string)
    return outfile_path.absolute().as_posix()

def get_include_string():
    strings = []
    for k, v in module_cache_by_resolved_filename.items():
        #skip builtins file
        if v[2]: #skip_render flag
            continue

        if v[1]:
            strings.append(f"use <{k}>;")
        else:
            strings.append(f"include <{k}>;")

    s = "\n".join(strings)
    s += "\n\n" if s else ''

    return s


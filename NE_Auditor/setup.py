from cx_Freeze import setup, Executable

pname: str = "NE_Auditor"
vrsn: str = "1.1"
company_name = "IES_DTC3"
excludes = ["tkinter"]
includes = ["jinxed.terminfo.vtwin10"]
include_files = ["ne_list.ini", "ne_commands.yml"]

options = {
    "build_exe": {
        "include_msvcr": True,
        "includes": includes,
        "excludes": excludes,
        "include_files": include_files,
    },
    "bdist_msi": {
        "target_name": f"{pname}_v{vrsn}",
        "initial_target_dir": r"[WindowsVolume]\%s\%s" % (company_name, pname),
    },
}

executables = [
    Executable("ne_auditor.py", icon="favicon.ico", target_name=f"{pname}.exe"),
]

setup(
    name=f"{pname}",
    version=vrsn,
    executables=executables,
    options=options,
    description=f"{pname} Copyright 2021 Aleksei Polkhirev",
)

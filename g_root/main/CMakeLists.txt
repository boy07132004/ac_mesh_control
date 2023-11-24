
idf_component_register(
    SRCS 
        "g_root.c"
        "../../src/zm_lib.c"
        "../../src/ac_control.c"

    INCLUDE_DIRS 
        "."
        ".."
        "../../src"

    REQUIRES mcommon mconfig mwifi mlink
)


idf_component_register(
    SRCS 
        "g_node_dummy.c"
        "../../src/zm_lib.c"
        "../../src/ac_control.c"
    INCLUDE_DIRS
        "."
        
    REQUIRES mcommon mconfig mwifi mlink
)

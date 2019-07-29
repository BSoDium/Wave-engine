try:
    import os,ctypes,sys,random,time
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import *
    from direct.showbase import DirectObject
    print("[SUCCESS]: successfully imported libraries")
except:
    print("[FAILURE]: library importation error, aborting...")
    sys.exit(0)

# now we need to create a simple plane (the best would be an already triangulated square, so that we can afterwards animate it)

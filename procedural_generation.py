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

'''
At this point the developer (me) didn't find enough motivation to continue writing this procedural generation shit, so he decided to close the tab,
and take a break, as it was past midnight, and the red bull cans he had stacked up all over the desk were becoming too numerous.
He saved his work, hit the on/off button and went to bed
Goodnight.
'''

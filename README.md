# Wave-simulator
A panda3d based wave-motion particle simulator in python.<br>

### Installing
The only required library is panda3d (all other libs used are included by default in the python installer package) <br>
In order to install it, type ```pip install panda``` in the windows command prompt, or install the SDK from [the panda3d webpage](panda3d.org)
Customizable physical variables inside the code:<br>
```
MAINDIR = Filename.from_os_specific(os.getcwd())
RIGIDCONST=5
TIMESCALE=0.01
FRICTIONCONST=0.98 # 0.98 = Pizza dough, 0.90 = slow mo kevlar, 0.99 is too high, there is a major risk of structural instability
GLOBALSCALE=3
BLOCKINTERVAL=0.06
GLOBALMASS=0.1 # kg USI
```

### main algorithm screenshots, with the corresponding version:
![](WaveSim_screenshot03.png)
![](WaveSim_screenshot02.png)
![](WaveSim_screenshot01.png)

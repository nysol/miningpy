#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import nysol.util.margs as margs
import nysol.mining.msketchsort as nmm


args=margs.Margs(sys.argv,"e=,tid=,i=,dist=,th=,mr=,wf=,ws=,o=,T=,seed=,-uc","e=,tid=,i=")
nmm.msketchsort(**(args.kvmap())).run(msg="on")


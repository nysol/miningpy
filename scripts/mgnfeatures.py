#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import nysol.util.margs as margs
import nysol.mining.mgnfeatures as nmm


args=margs.Margs(sys.argv,"I=,ei=,ef=,ni=,nf=,ew=,O=,mode=,-directed,-normalize,-verbose,mp=","ef=,O=")
nmm.mgnfeatures(**(args.kvmap())).run(msg="on")


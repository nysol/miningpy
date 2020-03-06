#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import nysol.util.margs as margs
import nysol.mining.mnewman as nmm

args=margs.Margs(sys.argv,"ei=,ef=,ni=,nf=,ew=,al=,o=,-directed,T=,-verbose","ei=")
nmm.mnewman(**(args.kvmap())).run(msg="on")


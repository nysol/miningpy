#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import nysol.util.margs as margs
import nysol.mining.mgfeatures as nmm

args=margs.Margs(sys.argv,"I=,ei=,ef=,ni=,nf=,o=,O=,diameter=,graph_density=,average_shortest_path,-verbose,-directed,mp=","ef=,O=")
nmm.mgfeatures(**(args.kvmap())).run(msg="on")


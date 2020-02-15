#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import nysol.util.margs as margs
import nysol.mining.mgpmetis as nmm


args=margs.Margs(sys.argv,"ei=,ef=,ew=,ni=,nf=,nw=,o=,kway=,ptype=,balance=,ncuts=,dat=,map=,-noexe,seed=,T=,-verbose,T=","kway=,ei=")
nmm.mgpmetis(**(args.kvmap())).run(msg="on")


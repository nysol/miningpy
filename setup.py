from setuptools import setup, find_packages, Extension
import re
import os
import subprocess

def checkLibRun(cc,fname,paras):
	for para in paras:
		try:
			with open(os.devnull, 'w') as fnull:
				exit_code = subprocess.call(cc + [ fname , "-l"+para],
                                    stdout=fnull, stderr=fnull)
		except OSError :
			exit_code = 1

		if exit_code == 0:
			return para

	return ""

def check_for_boost():

	import sysconfig
	import tempfile
	import shutil
	
	# Create a temporary directory
	tmpdir = tempfile.mkdtemp()
	curdir = os.getcwd()
	os.chdir(tmpdir)

	compiler = os.environ.get('CC', sysconfig.get_config_var('CC'))

	# make sure to use just the compiler name without flags
	compiler = compiler.split()
	filename = 'test.cpp'
	with open(filename,'w') as f :
		f.write("""
			int main ()
			{
				return main ();
			  return 0;
			}
			""")

	boostFLG =[]
	boostLibLists=[
		['boost_system-mt','boost_system'],
	]
	for boostlist in boostLibLists:

		boostflg = checkLibRun(compiler,filename, boostlist)
		if boostflg =="" : 	
			#err
			raise Exception("not find "+ " or ".join(boostlist))

		boostFLG.append(boostflg)

	# Clean up
	os.chdir(curdir)
	shutil.rmtree(tmpdir)

	return boostFLG

skmodLibs=["stdc++","m"]
skmodLibs.extend(check_for_boost())


skmod = Extension('nysol/mining/_sketchsortlib',
                    sources = [ 'src/mining/sketchsortrap.cpp',
                    						'src/mining/sketchsort/Main.cpp',
                    						'src/mining/sketchsort/SketchSort.cpp'],
										define_macros=[('NDEBUG', None),('_NO_MAIN_',None)],
 										extra_compile_args=['-Wno-deprecated','-pedantic','-ansi','-finline-functions',
 																				'-foptimize-sibling-calls','-Wcast-qual','-Wwrite-strings',
 																				'-Wsign-promo','-Wcast-align','-Wno-long-long','-fexpensive-optimizations',
																				'-funroll-all-loops','-ffast-math','-fomit-frame-pointer','-pipe' ],
										include_dirs=['src/mining/','src/mining/sketchsort'],
										libraries=skmodLibs)


setup(name = 'nysol_mining',
			packages=['nysol','nysol/mining','nysol/widget','nysol/model'],
			version = '0.0.1',
			description = 'This is nysol tools',
			long_description="""\
NYSOL (read as nee-sol) is a generic name of software tools and project activities designed for supporting big data analysis.

NYSOL runs in UNIX environment (Linux and Mac OS X, not Windows).
""",
			author='nysol',
			author_email='info@nysol.jp',
			license='AGPL3',
			url='http://www.nysol.jp/',
      classifiers=[ 
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
			#install_requires=[
      #	  "psutil"
	    #],
			scripts=[
				'scripts/mgfeatures.py','scripts/mgnfeatures.py',
				'scripts/mspade.py','scripts/mcarm.py','scripts/msketchsort.py' 
				],
			ext_modules =[skmod]
			)
       

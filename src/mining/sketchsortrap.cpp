
#include "Python.h"

#include "sketchsort/Main.hpp"

#if PY_MAJOR_VERSION >= 3
extern "C" {
	PyMODINIT_FUNC PyInit__sketchsortlib(void);
}
#else
extern "C" {
	void init_sketchsortlib(void);
}
#endif

#if PY_MAJOR_VERSION >= 3
 #define strGET PyUnicode_AsUTF8
#else		
 #define strGET PyString_AsString
#endif


static int strCHECK(PyObject* data){

#if PY_MAJOR_VERSION >= 3
	return PyUnicode_Check(data);
#else		
	return PyString_Check(data);
#endif

}



PyObject* sketchsort_run(PyObject* self, PyObject* args){

	PyObject *params;

	if(!PyArg_ParseTuple(args, "O", &params)){ 
		PyErr_SetString(PyExc_RuntimeError,"parameter ERROR pyobject");
		PyErr_Print();
		return PyLong_FromLong(1);
	}//err
	if(!PyList_Check(params)){
		PyErr_SetString(PyExc_RuntimeError,"parameter ERROR Not list");
		PyErr_Print();
		return PyLong_FromLong(2); 
	}//err

	Py_ssize_t psize = PyList_Size(params);
	char** vv = (char**)malloc(sizeof(char*)*(psize+1));
	if(vv==NULL){
		// ERROR
		PyErr_SetString(PyExc_RuntimeError,"Memory alloc ERROR");
		PyErr_Print();
		return PyLong_FromLong(3);
	}

	vv[0] = "sketchsort";
	Py_ssize_t i;
	for(i=0 ; i< psize;i++){
		PyObject *param = PyList_GetItem(params ,i);
		if(strCHECK(param)){
			vv[i+1] = strGET(param);
		}
		else{
			PyErr_SetString(PyExc_RuntimeError,"parameter ERROR : not str");
			if(vv){ free(vv); }
			return PyLong_FromLong(4); 
		}
	}

	// DEBUG
	//for(int i=0; i<pos;i++){ printf("%s ",vv[i]); }
	//printf("\n");

	int sts = sketchsort_main(psize+1,vv);
	//if(sts){//ERRORにはしない
	//	PyErr_SetString(PyExc_RuntimeError,"TAKE Module RUN ERROR");
	//	PyErr_Print();
	//}

	if(vv){ free(vv);}
	return PyLong_FromLong(sts);

}

static PyMethodDef miningmethods_sketchsort[] = {
	{"sketchsort_run", (PyCFunction)sketchsort_run, METH_VARARGS  },
//	{"medset_runByDict", reinterpret_cast<PyCFunction>(medset_run_dict), METH_VARARGS  },
	{NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_sketchsortlib",      /* m_name */
    NULL,							     /* m_doc */
    -1,                  /* m_size */
    miningmethods_sketchsort,      /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
};

PyMODINIT_FUNC
PyInit__sketchsortlib(void){
	PyObject* m;
	m = PyModule_Create(&moduledef);
	return m;
}

#else

void init_sketchsortlib(void){
	Py_InitModule("_sketchsortlib", miningmethods_sketchsort);
}

#endif
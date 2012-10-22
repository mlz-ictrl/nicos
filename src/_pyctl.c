/*******************************************************************************
 * NICOS-NG, the Networked Instrument Control System of the FRM-II
 * Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation; either version 2 of the License, or (at your option) any later
 * version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Module authors:
 *   Georg Brandl <georg.brandl@frm2.tum.de>
 *
 ******************************************************************************/

#include <Python.h>
#include <frameobject.h>     /* These are not included by Python.h */
#include <structmember.h>
#include <pythread.h>


typedef struct {
    PyObject_HEAD
    int started;                  /* execution started? */
    int request;                  /* request for break/stop, see REQ_FOO */
    int status;                   /* current status, see STATUS_FOO */
    int lineno;                   /* current line number */
    int break_only_in_toplevel;   /* if true, break only in starting frame */
    int lineno_behavior;          /* see LINENO_FOO */
    PyObject *observer;           /* function to call on important events */
    PyObject *break_only_in_filename; /* a filename to allow breaks in */
    PyFrameObject *startframe;    /* frame the code is executed from */
    PyFrameObject *toplevelframe; /* topmost frame of the executed code */
    PyFrameObject *currentframe;  /* current frame of the executed code */
    PyObject *breakfunc;          /* function to call on break */
    PyObject *requestarg;         /* additional argument for the breakfunc */
} CtlrObject;

/* Request constants */
#define REQ_IDLE     -1     /* nothing started */
#define REQ_RUN      0      /* no request, keep running */
#define REQ_BREAK    1      /* break at next possible location */
#define REQ_STOP     2      /* stop execution immediately */
#define REQ_DEBUG    3      /* start pdb session */

/* Status constants */
#define STATUS_IDLEEXC  -2  /* nothing started, last script raised exception */
#define STATUS_IDLE     -1  /* nothing started */
#define STATUS_RUNNING  0   /* execution running */
#define STATUS_INBREAK  1   /* execution halted, in break function */
#define STATUS_STOPPING 2   /* stop exception raised, waiting for return
                               to toplevel frame */

/* Line number tracing constants */
#define LINENO_ALL      0   /* trace all line numbers */
#define LINENO_TOPLEVEL 1   /* trace only line numbers in toplevel frame */
#define LINENO_NAME     2   /* trace only line numbers in frames with the
                               filename given by break_only_in_filename */

/* Exceptions */
static PyObject *ControlStop = NULL;
static PyObject *ControllerError = NULL;


/* set a new status and notify the observer */
inline void
set_status(CtlrObject *self, int status)
{
    if (self->status == status)
        return;
    self->status = status;
    if (self->observer) {
        /* ignore all errors when calling the observer */
        PyObject *e1, *e2, *e3;
        PyErr_Fetch(&e1, &e2, &e3);
        PyObject_CallFunction(self->observer, "ii", status, self->lineno);
        PyErr_Restore(e1, e2, e3);
    }
}

/* set a new line number and notify the observer */
inline void
set_lineno(CtlrObject *self, int lineno)
{
    if (self->lineno == lineno)
        return;
    self->lineno = lineno;
    if (self->observer) {
        /* ignore all errors when calling the observer */
        PyObject *e1, *e2, *e3;
        PyErr_Fetch(&e1, &e2, &e3);
        PyObject_CallFunction(self->observer, "ii", self->status, lineno);
        PyErr_Restore(e1, e2, e3);
    }
}

/* The main trace function */
static int
trace_function(CtlrObject *self, PyFrameObject *frame, int what, PyObject *arg)
{
    PyObject *ret;
    /* if we're back in the starting frame, stop tracing */
    if (frame == self->startframe) {
        PyEval_SetTrace(NULL, NULL);
        return 0;
    }

    /* the first frame we're called in is the "toplevel" frame
       of the traced code */
    if (self->toplevelframe == NULL) {
        self->toplevelframe = frame;
        Py_INCREF(self->toplevelframe);
    }

    if (frame != self->currentframe) {
        Py_XDECREF(self->currentframe);
        self->currentframe = frame;
        Py_INCREF(self->currentframe);
    }

    if (what == PyTrace_LINE) {
        if (self->lineno_behavior == LINENO_NAME &&
            strcmp(PyString_AS_STRING(frame->f_code->co_filename),
                   PyString_AS_STRING(self->break_only_in_filename)) == 0)
            set_lineno(self, frame->f_lineno);
        else if (self->lineno_behavior == LINENO_TOPLEVEL &&
                 frame == self->toplevelframe)
            set_lineno(self, frame->f_lineno);
        else if (self->lineno_behavior == LINENO_ALL)
            set_lineno(self, frame->f_lineno);
    }

    switch (self->request) {
    case REQ_RUN:
        return 0;
    case REQ_BREAK:
        /* always break if frame filename starts with <break> */
        if (strncmp(PyString_AS_STRING(frame->f_code->co_filename), "<break>", 7) != 0) {
            if (self->break_only_in_toplevel && frame != self->toplevelframe) {
                /* keep the break request, but wait until in toplevel */
                return 0;
            }
            if (self->break_only_in_filename &&
                strcmp(PyString_AS_STRING(frame->f_code->co_filename),
                       PyString_AS_STRING(self->break_only_in_filename)) != 0) {
                /* keep the break request, but wait until in frame with
                   the specified filename */
                return 0;
            }
        }
        /* set this before call, since the break function may set
           another request */
        self->request = REQ_RUN;
        set_status(self, STATUS_INBREAK);
        ret = PyObject_CallFunctionObjArgs(self->breakfunc, frame,
                                           self->requestarg, NULL);
        set_status(self, STATUS_RUNNING);
        Py_XDECREF(ret);
        if (self->request == REQ_STOP) {
            set_status(self, STATUS_STOPPING);
            PyErr_SetObject(ControlStop, self->requestarg);
            ret = NULL;
        }
        if (!ret)
            return -1;
        return 0;
    case REQ_DEBUG:
        if (self->status == STATUS_RUNNING && PyCallable_Check(self->requestarg)) {
            /* the requestarg should be the set_trace() function of a Pdb instance */
            ret = PyObject_CallFunctionObjArgs(self->requestarg, self->currentframe,
                                               self->toplevelframe, NULL);
            /* NOTE: if the debugger set_trace succeeded, our trace function will be
               inactive until someone calls reset_trace() */
            if (ret == NULL) {
                PyErr_WriteUnraisable(NULL);
                PyErr_Clear();
            }
            Py_DECREF(ret);
            self->request = REQ_RUN;
        }
        return 0;
    case REQ_STOP:
        if (self->status != STATUS_STOPPING) {
            set_status(self, STATUS_STOPPING);
            PyErr_SetObject(ControlStop, self->requestarg);
            return -1;
        }
        /*
        if (strcmp(PyString_AS_STRING(frame->f_code->co_name), "__del__") == 0)
            / don't raise exceptions in destructors /
            return 0;
        */
        /* fallthrough */
    default:
        return 0;
    }
}

/* Controller methods */

static void
reset(CtlrObject *self, int raised)
{
    Py_CLEAR(self->currentframe);
    Py_CLEAR(self->toplevelframe);
    Py_CLEAR(self->startframe);
    self->started = 0;
    self->request = REQ_IDLE;
    set_status(self, raised ? STATUS_IDLEEXC : STATUS_IDLE);
    set_lineno(self, -1);
}

static void
prepare(CtlrObject *self)
{
    self->started = 1;
    self->request = REQ_RUN;
    set_status(self, STATUS_RUNNING);
    set_lineno(self, 0);

    Py_CLEAR(self->toplevelframe);
    Py_CLEAR(self->requestarg);
    Py_CLEAR(self->startframe);
    self->startframe = PyEval_GetFrame();
    Py_INCREF(self->startframe);
}

static int
ctlr_init(CtlrObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *func;
    PyObject *break_only_in_filename = NULL;
    int break_only_in_toplevel = 0;
    int lineno_behavior = LINENO_TOPLEVEL;
    static char *kwlist[] = {"breakfunc", "break_only_in_toplevel",
                             "break_only_in_filename", "lineno_behavior", 0};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|iOi:Controller", kwlist,
                                     &func,
                                     &break_only_in_toplevel,
                                     &break_only_in_filename,
                                     &lineno_behavior))
        return -1;
    if (break_only_in_filename == Py_None)
        break_only_in_filename = NULL;
    if (break_only_in_filename && !PyString_Check(break_only_in_filename)) {
        PyErr_SetString(PyExc_TypeError, "break_only_in_filename arg must be "
                        "a string");
        return -1;
    }
    if (lineno_behavior == LINENO_NAME && !break_only_in_filename) {
        PyErr_SetString(PyExc_ValueError, "must give break_only_in_filename "
                        "arg if lineno_behavior is LINENO_NAME");
        return -1;
    }

    reset(self, 0);
    Py_INCREF(func);
    self->breakfunc = func;
    self->break_only_in_toplevel = break_only_in_toplevel;
    Py_XINCREF(self->break_only_in_filename);
    self->break_only_in_filename = break_only_in_filename;
    self->lineno_behavior = lineno_behavior;
    self->observer = NULL;
    return 0;
}

static void
ctlr_dealloc(CtlrObject *self)
{
    Py_CLEAR(self->startframe);
    Py_CLEAR(self->toplevelframe);
    Py_CLEAR(self->currentframe);
    Py_CLEAR(self->breakfunc);
    Py_CLEAR(self->requestarg);
    Py_CLEAR(self->break_only_in_filename);
    Py_CLEAR(self->observer);
}

static PyObject *
ctlr_start(CtlrObject *self, PyObject *callable)
{
    PyObject *ret;

    if (self->started) {
        PyErr_SetString(ControllerError, "Controller already started");
        return NULL;
    }
    prepare(self);
    PyEval_SetTrace((Py_tracefunc)trace_function, (PyObject *)self);
    ret = PyObject_CallFunctionObjArgs(callable, NULL);
    reset(self, 0);
    return ret;
}

static PyObject *
ctlr_start_exec(CtlrObject *self, PyObject *args)
{
    PyObject *ret;
    PyObject *code = NULL, *globals = NULL, *locals = NULL, *debugarg = NULL;

    if (self->started) {
        PyErr_SetString(ControllerError, "Controller already started");
        return NULL;
    }
    if (!PyArg_ParseTuple(args, "OO|OO:start_exec", &code, &globals, &locals,
                                                    &debugarg))
        return NULL;
    if (!PyCode_Check(code)) {
        PyErr_SetString(PyExc_TypeError, "start_exec needs a code object");
        return NULL;
    }
    if (!PyDict_Check(globals)) {
        PyErr_SetString(PyExc_TypeError, "globals must be a dict");
        return NULL;
    }
    if (locals && locals != Py_None) {
        if (!PyDict_Check(locals)) {
            PyErr_SetString(PyExc_TypeError, "locals must be a dict");
            return NULL;
        }
    } else {
        locals = globals;
    }
    prepare(self);
    if (debugarg && debugarg != Py_None) {
        self->request = REQ_DEBUG;
        self->requestarg = debugarg;
        Py_INCREF(self->requestarg);
    }
    PyEval_SetTrace((Py_tracefunc)trace_function, (PyObject *)self);
    ret = PyEval_EvalCode((PyCodeObject *)code, globals, locals);
    reset(self, ret == NULL);
    return ret;
}

static PyObject *
ctlr_set_break(CtlrObject *self, PyObject *arg)
{
    if (!self->started) {
        PyErr_SetString(ControllerError, "Controller not started");
        return NULL;
    }
    Py_CLEAR(self->requestarg);
    self->requestarg = arg;
    Py_INCREF(self->requestarg);
    self->request = REQ_BREAK;
    Py_RETURN_NONE;
}

static PyObject *
ctlr_set_stop(CtlrObject *self, PyObject *arg)
{
    if (!self->started) {
        PyErr_SetString(ControllerError, "Controller not started");
        return NULL;
    }
    Py_CLEAR(self->requestarg);
    self->requestarg = arg;
    Py_INCREF(self->requestarg);
    self->request = REQ_STOP;
    Py_RETURN_NONE;
}

static PyObject *
ctlr_set_debug(CtlrObject *self, PyObject *arg)
{
    if (!self->started) {
        PyErr_SetString(ControllerError, "Controller not started");
        return NULL;
    }
    Py_CLEAR(self->requestarg);
    self->requestarg = arg;
    Py_INCREF(self->requestarg);
    self->request = REQ_DEBUG;
    Py_RETURN_NONE;
}

static PyObject *
ctlr_reset_trace(CtlrObject *self, PyObject *unused)
{
    PyEval_SetTrace((Py_tracefunc)trace_function, (PyObject *)self);
    Py_RETURN_NONE;
}

static PyObject *
ctlr_set_observer(CtlrObject *self, PyObject *arg)
{
    if (!PyCallable_Check(arg)) {
        PyErr_SetString(ControllerError, "argument is not a callable");
        return NULL;
    }
    Py_CLEAR(self->observer);
    self->observer = arg;
    Py_INCREF(self->observer);
    Py_RETURN_NONE;
}

static PyMethodDef ctlr_methods[] = {
    {"start", (PyCFunction)ctlr_start, METH_O, NULL},
    {"start_exec", (PyCFunction)ctlr_start_exec, METH_VARARGS, NULL},
    {"set_break", (PyCFunction)ctlr_set_break, METH_O, NULL},
    {"set_stop", (PyCFunction)ctlr_set_stop, METH_O, NULL},
    {"set_debug", (PyCFunction)ctlr_set_debug, METH_O, NULL},
    {"reset_trace", (PyCFunction)ctlr_reset_trace, METH_NOARGS, NULL},
    {"set_observer", (PyCFunction)ctlr_set_observer, METH_O, NULL},
    {NULL},
};

static PyMemberDef ctlr_members[] = {
    {"status", T_INT, offsetof(CtlrObject, status), READONLY},
    {"currentframe", T_OBJECT, offsetof(CtlrObject, currentframe), READONLY},
    {"toplevelframe", T_OBJECT, offsetof(CtlrObject, toplevelframe), READONLY},
    {"lineno", T_INT, offsetof(CtlrObject, lineno), READONLY},
    {NULL},
};

static PyTypeObject CtlrType = {
    PyObject_HEAD_INIT(NULL)
    0,					/* ob_size		*/
    "_pyctl.Controller",		/* tp_name		*/
    sizeof(CtlrObject),			/* tp_basicsize		*/
    0,					/* tp_itemsize		*/
    (destructor)ctlr_dealloc,		/* tp_dealloc		*/
    0,					/* tp_print		*/
    0,					/* tp_getattr		*/
    0,					/* tp_setattr		*/
    0,					/* tp_compare		*/
    0,					/* tp_repr		*/
    0,					/* tp_as_number		*/
    0,					/* tp_as_sequence	*/
    0,					/* tp_as_mapping	*/
    0,					/* tp_hash		*/
    0,					/* tp_call		*/
    0,					/* tp_str		*/
    PyObject_GenericGetAttr,		/* tp_getattro		*/
    0,					/* tp_setattro		*/
    0,					/* tp_as_buffer		*/
    Py_TPFLAGS_DEFAULT
       | Py_TPFLAGS_BASETYPE,		/* tp_flags		*/
    0,					/* tp_doc		*/
    0,					/* tp_traverse		*/
    0,					/* tp_clear		*/
    0,					/* tp_richcompare	*/
    0,					/* tp_weaklistoffset	*/
    0,					/* tp_iter		*/
    0,					/* tp_iternext		*/
    ctlr_methods,			/* tp_methods		*/
    ctlr_members,			/* tp_members		*/
    0,					/* tp_getset		*/
    0,					/* tp_base		*/
    0,					/* tp_dict		*/
    0,					/* tp_descr_get		*/
    0,					/* tp_descr_set		*/
    0,					/* tp_dictoffset	*/
    (initproc)ctlr_init,		/* tp_init		*/
    PyType_GenericAlloc,		/* tp_alloc		*/
    PyType_GenericNew,			/* tp_new		*/
    0,					/* tp_free		*/
};


static PyMethodDef functions[] = {
    {NULL}
};

void
init_pyctl(void)
{
    PyObject *module;
    module = Py_InitModule("_pyctl", functions);
    CtlrType.ob_type = &PyType_Type;
    Py_INCREF((PyObject *)&CtlrType);
    PyModule_AddObject(module, "Controller", (PyObject *)&CtlrType);
    ControlStop = PyErr_NewException("_pyctl.ControlStop",
                                     PyExc_BaseException, NULL);
    if (ControlStop != NULL) {
        Py_INCREF(ControlStop);
        PyModule_AddObject(module, "ControlStop", ControlStop);
    }
    ControllerError = PyErr_NewException("_pyctl.ControllerError", NULL, NULL);
    if (ControllerError != NULL) {
        Py_INCREF(ControllerError);
        PyModule_AddObject(module, "ControllerError", ControllerError);
    }
}

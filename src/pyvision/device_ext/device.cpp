// EnumerateDevice.cpp : Ce fichier contient la fonction 'main'. L'exécution du programme commence et se termine à cet endroit.
//

#include "Python.h"
#include <Windows.h>
#include <dshow.h>
#include <comutil.h>

#include <iostream>

#pragma comment(lib, "strmiids")

#pragma comment(lib, "comsuppwd.lib")

void _FreeMediaType(AM_MEDIA_TYPE& mt) {
    if (mt.cbFormat != 0) {
        CoTaskMemFree((PVOID)mt.pbFormat);
        mt.cbFormat = 0;
        mt.pbFormat = nullptr;
    }
    if (mt.pUnk != nullptr) {
        // pUnk should not be used
        mt.pUnk->Release();
        mt.pUnk = nullptr;
    }
}

void _DeleteMediaType(AM_MEDIA_TYPE* pmt) {
    if (pmt != nullptr) {
        _FreeMediaType(*pmt);
        CoTaskMemFree(pmt);
    }
}

HRESULT EnumerateDevices(REFGUID category, IEnumMoniker** ppEnum) {
    // Create the system device enumerator
    ICreateDevEnum* pDevEnum;
    HRESULT hr = CoCreateInstance(CLSID_SystemDeviceEnum, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));

    if (SUCCEEDED(hr)) {
        // Create an enumetator for the category
        hr = pDevEnum->CreateClassEnumerator(category, ppEnum, 0);
        if (hr == S_FALSE) {
            hr = VFW_E_NOT_FOUND;
        }
        pDevEnum->Release();
    }
    return hr;
}

PyObject* CreateResolutionList(IPin* pPin) {
    PyObject* resolutionList = PyList_New(0);
    IEnumMediaTypes* pEnumMediaTypes = nullptr;
    AM_MEDIA_TYPE* mediaType = nullptr;
    HRESULT hr = pPin->EnumMediaTypes(&pEnumMediaTypes);
    if (FAILED(hr)) return resolutionList; // Return empty list on failure

    while (S_OK == pEnumMediaTypes->Next(1, &mediaType, nullptr)) {
        if ((mediaType->formattype == FORMAT_VideoInfo) &&
            (mediaType->cbFormat >= sizeof(VIDEOINFOHEADER)) &&
            (mediaType->pbFormat != nullptr)) {

            auto videoInfoHeader = (const VIDEOINFOHEADER*)mediaType->pbFormat;
            PyObject* size = PyTuple_New(2);
            PyTuple_SetItem(size, 0, Py_BuildValue("i", videoInfoHeader->bmiHeader.biWidth));
            PyTuple_SetItem(size, 1, Py_BuildValue("i", videoInfoHeader->bmiHeader.biHeight));
            PyList_Append(resolutionList, size);
        }
        _DeleteMediaType(mediaType);
    }
    pEnumMediaTypes->Release();
    return resolutionList;
}

PyObject* GetDeviceDescription(IPropertyBag* pPropBag) {
    VARIANT var;
    VariantInit(&var);
    HRESULT hr = pPropBag->Read(L"Description", &var, nullptr);
    if (FAILED(hr)) {
        hr = pPropBag->Read(L"FriendlyName", &var, nullptr);
    }
    if (SUCCEEDED(hr)) {
        // Directly use the BSTR without converting it to a char*
        PyObject* desc = Py_BuildValue("u", var.bstrVal); // "u" for Unicode (wide char) string
        VariantClear(&var);
        return desc;
    }
    VariantClear(&var);
    return nullptr;
}

PyObject* GetResolutionListForMoniker(IMoniker* pMoniker) {
    IBaseFilter* pFilter = nullptr;
    HRESULT hr = pMoniker->BindToObject(nullptr, nullptr, IID_IBaseFilter, (void**)&pFilter);
    if (FAILED(hr)) return nullptr;

    IEnumPins* pEnumPins = nullptr;
    hr = pFilter->EnumPins(&pEnumPins);
    if (FAILED(hr)) {
        pFilter->Release();
        return nullptr;
    }

    PyObject* resolutionList = PyList_New(0);
    IPin* pPin = nullptr;
    while (S_OK == pEnumPins->Next(1, &pPin, nullptr)) {
        PyObject* pinResolutions = CreateResolutionList(pPin);
        PyList_Append(resolutionList, pinResolutions);
        Py_DECREF(pinResolutions);
        pPin->Release();
    }

    pEnumPins->Release();
    pFilter->Release();
    return resolutionList;
}

PyObject* DisplayDeviceInformation(IEnumMoniker* pEnum) {
    PyObject* pyList = PyList_New(0);
    IMoniker* pMoniker = nullptr;

    while (pEnum->Next(1, &pMoniker, nullptr) == S_OK) {
        IPropertyBag* pPropBag;
        HRESULT hr = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
        if (FAILED(hr)) {
            pMoniker->Release();
            continue;
        }

        // Get the supported resolution list
        PyObject* resolutionList = GetResolutionListForMoniker(pMoniker);
        if (!resolutionList) {
            pPropBag->Release();
            pMoniker->Release();
            continue;
        }

        // Get the device description
        PyObject* deviceDescription = GetDeviceDescription(pPropBag);
        if (!deviceDescription) {
            Py_DECREF(resolutionList);
            pPropBag->Release();
            pMoniker->Release();
            continue;
        }

        // Append the device description and resolution list to the main list
        PyObject* tuple = PyTuple_New(2);
        PyTuple_SetItem(tuple, 0, deviceDescription);
        PyTuple_SetItem(tuple, 1, resolutionList);
        PyList_Append(pyList, tuple);
        Py_DECREF(tuple);

        pPropBag->Release();
        pMoniker->Release();
    }

    return pyList;
}


static PyObject* getDeviceList(PyObject* self, PyObject* args) {
    PyObject* pyList = nullptr;

    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (SUCCEEDED(hr)) {
        IEnumMoniker* pEnum;

        hr = EnumerateDevices(CLSID_VideoInputDeviceCategory, &pEnum);
        if (SUCCEEDED(hr)) {
            pyList = DisplayDeviceInformation(pEnum);
            pEnum->Release();
        }
        CoUninitialize();
    }

    return pyList;
}

static PyMethodDef device_methods[] = {
    {"getDeviceList", getDeviceList, METH_VARARGS, "get device list"},
    {nullptr, nullptr, 0, nullptr} /* Sentinel */
};

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_device(void)
{
    (void) Py_InitModule("device", device_methods);
}
#else /* PY_MAJOR_VERSION >= 3 */
static struct PyModuleDef device_module_def = {
    PyModuleDef_HEAD_INIT,
    "device",
    "Internal \"device\" module",
    -1,
    device_methods
};

PyMODINIT_FUNC PyInit_device(void)
{
    return PyModule_Create(&device_module_def);
}
#endif /* PY_MAJOR_VERSION >= 3 */

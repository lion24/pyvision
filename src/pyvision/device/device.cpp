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
        mt.pbFormat = NULL;
    }
    if (mt.pUnk != NULL) {
        // pUnk should not be used
        mt.pUnk->Release();
        mt.pUnk = NULL;
    }
}

void _DeleteMediaType(AM_MEDIA_TYPE* pmt) {
    if (pmt != NULL) {
        _FreeMediaType(*pmt);
        CoTaskMemFree(pmt);
    }
}

HRESULT EnumerateDevices(REFGUID category, IEnumMoniker** ppEnum) {
    // Create the system device enumerator
    ICreateDevEnum* pDevEnum;
    HRESULT hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));

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

PyObject* DisplayDeviceInformation(IEnumMoniker* pEnum) {
    // Create an empty python list

    PyObject* pyList = PyList_New(0);

    IMoniker* pMoniker = NULL;

    while (pEnum->Next(1, &pMoniker, NULL) == S_OK) {
        IPropertyBag* pPropBag;
        HRESULT hr = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
        if (FAILED(hr)) {
            pMoniker->Release();
            continue;
        }

        // Get supported resolution
        IEnumPins *pEnum = NULL;
        IBaseFilter* pFilter = NULL;
        hr = pMoniker->BindToObject(0, 0, IID_IBaseFilter, (void**)&pFilter);
        if (FAILED(hr)) {
            pMoniker->Release();
            continue;
        }

        hr = pFilter->EnumPins(&pEnum);
        if (FAILED(hr)) {
            pMoniker->Release();
            continue;
        }

        IPin* pPin = NULL;
        PyObject* resolutionList = PyList_New(0);
        while (S_OK == pEnum->Next(1, &pPin, NULL)) {
            IEnumMediaTypes *pEnumMediaTypes = NULL;
            AM_MEDIA_TYPE *mediaType = NULL;
            VIDEOINFOHEADER* videoInfoHeader = NULL;
            HRESULT hr = pPin->EnumMediaTypes(&pEnumMediaTypes);
            if (FAILED(hr)) {
                continue;
            }

            while (hr = pEnumMediaTypes->Next(1, &mediaType, NULL), hr == S_OK) {
                if ((mediaType->formattype == FORMAT_VideoInfo) &&
                    (mediaType->cbFormat >= sizeof(VIDEOINFOHEADER)) &&
                    (mediaType->pbFormat != NULL))
                {
                    videoInfoHeader = (VIDEOINFOHEADER*)mediaType->pbFormat;
                    videoInfoHeader->bmiHeader.biWidth;
                    videoInfoHeader->bmiHeader.biHeight;
                    PyObject *size = PyTuple_New(2);
                    PyTuple_SetItem(size, 0, Py_BuildValue("i", videoInfoHeader->bmiHeader.biWidth));
                    PyTuple_SetItem(size, 1, Py_BuildValue("i", videoInfoHeader->bmiHeader.biHeight));
                    PyList_Append(resolutionList, size);
                }
                _DeleteMediaType(mediaType);
            }
            pEnumMediaTypes->Release();
        }

        VARIANT var;
        VariantInit(&var);

        hr = pPropBag->Read(L"Description", &var, 0);
        if (FAILED(hr)) {
            hr = pPropBag->Read(L"FriendlyName", &var, 0);
        }
        if (SUCCEEDED(hr)) {
            // Append a result to python list
            char* pValue = _com_util::ConvertBSTRToString(var.bstrVal);
            PyObject* tuple = PyTuple_New(2);
            PyTuple_SetItem(tuple, 0, Py_BuildValue("s", pValue));
            PyTuple_SetItem(tuple, 1, resolutionList);
            hr = PyList_Append(pyList, tuple);
            delete[] pValue;
            if (FAILED(hr)) {
                printf("failed to append the object item at the end of list\n");
                return pyList;
            }

            VariantClear(&var);
        }

        hr = pPropBag->Write(L"FriendlyName", &var);
        hr = pPropBag->Read(L"DevicePath", &var, 0);
        if (SUCCEEDED(hr)) {
            VariantClear(&var);
        }

        pPropBag->Release();
        pMoniker->Release();
    }

    return pyList;
}

static PyObject* getDeviceList(PyObject* self, PyObject* args) {
    PyObject* pyList = NULL;

    HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
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
    {NULL, NULL, 0, NULL} /* Sentinel */
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

int main()
{
    std::cout << "Hello World!\n";
}

// Exécuter le programme : Ctrl+F5 ou menu Déboguer > Exécuter sans débogage
// Déboguer le programme : F5 ou menu Déboguer > Démarrer le débogage

// Astuces pour bien démarrer :
//   1. Utilisez la fenêtre Explorateur de solutions pour ajouter des fichiers et les gérer.
//   2. Utilisez la fenêtre Team Explorer pour vous connecter au contrôle de code source.
//   3. Utilisez la fenêtre Sortie pour voir la sortie de la génération et d'autres messages.
//   4. Utilisez la fenêtre Liste d'erreurs pour voir les erreurs.
//   5. Accédez à Projet > Ajouter un nouvel élément pour créer des fichiers de code, ou à Projet > Ajouter un élément existant pour ajouter des fichiers de code existants au projet.
//   6. Pour rouvrir ce projet plus tard, accédez à Fichier > Ouvrir > Projet et sélectionnez le fichier .sln.

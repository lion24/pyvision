# Pyvision

## Bootstrap

```sh
hatch build
hatch env create
```

And run using:
```sh
hatch run pyvision
```

## EnumerateDevice

Using opencv it is not possible to enumerate capture device.
For that we need to use native code that will use the DirectShow C++ windows API
to enumerate the capture device available on the system.
EnumerateDevice is a hence a shared library that query the DirectShow API and return
a list of tuple for every capture devices found on the system and the supported resolution
for each of the devices.

This library is automatically built and shipped when running the project.
It requires the Windows SDK and Python native code extension enabled.
Those can be obtained from the Visual Studio Community installer (not visual studio code)
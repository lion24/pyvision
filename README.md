# Pyvision

## Bootstrap

### Dependencies

You need the Windows SDK and Python native code extension enabled. This is needed to enemurate camera of the system.
See `src/pyvision/device_ext` section.

Install [Hatch](https://hatch.pypa.io/latest/install/#windows)

Hatch is a modern, extensible Python project manager. It will automtically help to construct the
project, managed the dependencies and automatically keep everything in sync.

And run using:
```sh
hatch env prune # make sure no previous env is left over which can cause some issues.
hatch run pyvision
```

## src/pyvision/device_ext

Using opencv it is not possible to enumerate capture device.
For that we need to use native code that will use the DirectShow C++ windows API
to enumerate the capture device available on the system.
`src/pyvision/device_ext` is a hence a shared library that query the DirectShow API and return
a list of tuple for every capture devices found on the system and the supported resolution
for each of the devices.

This library is automatically built and shipped when running the project.
It requires the Windows SDK and Python native code extension enabled.
Those can be obtained from the [Visual Studio Community installer](https://visualstudio.microsoft.com/vs/community/) (not visual studio code)

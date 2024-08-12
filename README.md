# Pyvision

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

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

## Some references

Here are the GitHub bibliographical references in markdown format:

* [Week 4: Image Filtering and Edge Detection](https://sbme-tutorials.github.io/2018/cv/notes/4_week4.html)
* [Image Gradients with OpenCV (Sobel and Scharr)](https://pyimagesearch.com/2021/05/12/image-gradients-with-opencv-sobel-and-scharr/)
* [Optimizing RTSP Video Processing in OpenCV: Overcoming FPS Discrepancies and Buffering Issues](https://medium.com/@vikas.c20/optimizing-rtsp-video-processing-in-opencv-overcoming-fps-discrepancies-and-buffering-issues-463e204c7b86)
* [Exploring the Data Types in OpenCV4: A Comprehensive Guide](https://medium.com/@nullbyte.in/part-2-exploring-the-data-types-in-opencv4-a-comprehensive-guide-49272f4a775)
* [Image Edge Detection: Sobel and Laplacian](https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Gradient_Sobel_Laplacian_Derivatives_Edge_Detection.php)
* [OpenCV Transparent API](https://learnopencv.com/opencv-transparent-api/)
* [Edge Detection with Gaussian Blur](https://www.projectrhea.org/rhea/index.php/Edge_Detection_with_Gaussian_Blur)

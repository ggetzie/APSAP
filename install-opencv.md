# Notes on how to install opencv-python with CUDA support to use the GPU

It is possible to install opencv via the python package [opencv-python](https://github.com/opencv/opencv-python) with `pip`. However the default version is CPU only.

In order to enable CUDA support we must build the package from source per the Manual builds section of the opencv-python README.

## Prerequisites

1. An Nvidia GPU with CUDA installed: [Download CUDA](https://developer.nvidia.com/cuda-downloads)
2. A C/C++ compiler for windows such as [Visual Studio](https://visualstudio.microsoft.com/vs/community/) or [MinGW-w64](https://www.msys2.org/)
3. [CMAKE](https://cmake.org/download/)
4. [Git](https://git-scm.com/download/win)  
   Make sure `C:\Program Files\Git\cmd` is added to your PATH environment variable.


A full list of the build options for opencv can be found [here](https://docs.opencv.org/4.x/db/d05/tutorial_config_reference.html)

We need to set the following options:
`OPENCV_EXTRA_MODULES_PATH=./opencv_contrib/modules` - CUDA modules stored in opencv_contrib
`ENABLE_CONTRIB`
`WITH_CUDA`   - Include NVidia Cuda Runtime support
`WITH_CUFFT`  - Include NVidia Cuda Fast Fourier Transform (FFT) library support
`WITH_CUBLAS` - Include NVidia Cuda Basic Linear Algebra Subprograms (BLAS) library support
`WITH_CUDNN`    - Include NVIDIA CUDA Deep Neural Network (cuDNN) library support

To enable these options and compile on Windows Powershell:
First activate any venv you might want to use

```
$Env:CMAKE_ARGS="-DWITH_CUDA=ON -DWITH_CUFFT=ON -DWITH_CUBLAS=ON -DWITH_CUDNN=ON"
$Env:ENABLE_CONTRIB=1
pip wheel . --verbose
```
This should generate two custom-built wheel files in the directory. One for numpy and one for opencv named like:

```
numpy-1.23.3-cp310-cp310-win_amd64.whl
opencv_contrib_python-4.6.0.3725898-cp310-cp310-win_amd64.whl
```

Pre-compiled wheel files for Windows 10 can be downloaded [here](https://hkuhk-my.sharepoint.com/:f:/g/personal/ggetzie_hku_hk/EpVz4AOOzGVIsW45aydShVcBBHScH8dG0gC_51w5Q09Zhg?e=baipX7)

These can be installed directly in the virtual environment with pip

```
pip install path/to/numpy-1.23.3-cp310-cp310-win_amd64.whl
pip install path/to/opencv_contrib_python-4.6.0.3725898-cp310-cp310-win_amd64.whl
```











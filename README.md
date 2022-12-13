# Getting Started

## Prerequisites

Make sure [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local) 11.6 or 11.7 is installed

Install Python 3.9

Create a Python 3.9 virtual environment in the project directory

```
python3.9 -m venv .venv --prompt apsap
```

Activate the environment and [manually install pytorch](https://pytorch.org/get-started/locally/#windows-verification) with CUDA support

```
.venv/Scripts/Activate.ps1
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

Note: edit cu117 to the version of CUDA installed

Install the rest of the requirements from the requirements.txt file.

```
pip install -r requirements.txt
```

To start the program, run the mainWindow.py file with the virtual environment active.

```
python ./mainWindow.py
```

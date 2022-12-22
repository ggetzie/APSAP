# Ceramic Sherd Matcher

## Getting Started

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

Download the model and add the directory to the repository (this is excluded from git due to size)

[model download](https://hkuhk-my.sharepoint.com/:f:/g/personal/ggetzie_hku_hk/EjFo29VjsmJHvQLH1pAD6kwBQaOKFCcut0XJSjTSBv6IAA?e=M5Ul8h)

To start the program, run the mainWindow.py file with the virtual environment active.

```
python ./mainWindow.py
```
## Explanations

To understand how the application actually works, take a look at the pdf(s) in the folder "./docs/"
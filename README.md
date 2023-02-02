# Ceramic Sherd Matcher

## Getting Started

 
Create a conda environment installed with Python 3.9 and activate it
```
conda create -n APSAP python=3.9
conda activate APSAP
```

Activate the environment and [manually install pytorch](https://pytorch.org/get-started/locally/#windows-verification) with CUDA support

```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

Install the rest of the requirements from the requirements.txt file.

```
pip install -r requirements.txt
```

Install the remaining Django-environ package

```
pip install django-environ
```

Download the model and add the directory to the repository (this is excluded from git due to size). Notice that an opengl32.dll is included as well.

[model download](https://hkuhk-my.sharepoint.com/:f:/g/personal/ggetzie_hku_hk/EjFo29VjsmJHvQLH1pAD6kwBQaOKFCcut0XJSjTSBv6IAA?e=M5Ul8h)


Finally, create a .env file inside the folder and put the environment details in it(Not included in Github for security reasons).

To start the program, run the mainWindow.py file with the virtual environment active.

```
python ./mainWindow.py
```

## Explanations

To understand how the application actually works, take a look at the pdf(s) in the folder "./docs/"
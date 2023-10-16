# Ceramic Sherd Matcher

## Getting Started
As the program is now situated in the directory "E:\tools\APSAP", a separation installation is not necessary.

To run the program, simply click the "run.bat" file in "E:\tools\APSAP". 


## (Optional) Installation from scratch

This step is optional as the application's dependencies has been installed as a conda environment inside E:\tools\APSAP\envs\APSAP.  


1. Create a conda environment installed with Python 3.9 and activate it
```
conda create -n APSAP python=3.9
conda activate APSAP
```

2. Activate the environment and [manually install pytorch](https://pytorch.org/get-started/locally/#windows-verification) with CUDA support

```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
```

3. Install the rest of the requirements from the requirements.txt file.

```
pip install -r requirements.txt
```

4. Install the remaining Django-environ package

```
pip install django-environ
```

5. Download the computation folder, which includes files outside the Git commit and put it under the project folder. and add the directory to the repository (this is excluded from git due to size). Notice that an opengl32.dll is included as well.

[computation folder download](https://hkuhk-my.sharepoint.com/:f:/g/personal/ggetzie_hku_hk/EonhiCqkDuJNq7dyXJ6FepUB0BmlgvZYbF5rfhGiSr5ZKA)


6. Finally, create a .env file inside the folder and put the environment details in it(Not included in Github for security reasons).

7. To start the program, run the mainWindow.py file with the virtual environment activated.

```
python ./mainWindow.py
```

## Explanations

To understand how the application actually works, here's a list of 

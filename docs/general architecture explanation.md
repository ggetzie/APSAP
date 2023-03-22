**Explanations of the architecture**

The application consists of two parts, the main part and the subsidary part.

**Subsidary part**

The subsidary part contains things that are not that related to the main operation of the code, they include:

- assets: it contains static assets like the logo of the application.
- configs: it contains basic settings and initial parameters in the application.
- docs: it contains documents for understanding the application.
- experimentals: it contains codes for doing experiments to figure things out, you can omit this folder entirely.

**Main part**

The application was organised in a MVP fashion, following the model view presenter architecture. It is impossible, however, to straightly follow this architecture since the library we use is PYQT. Nevertheless, the idea is generally there. Let's start the conversation with a gentle explanation of the model first.

**Model**

In MVP, model stands for data. It represents the underlying data necessary for the application to work. Our mode folder is of the following structure:

![image](https://user-images.githubusercontent.com/90679381/226843247-8767408e-ccb9-4b87-a6c7-ab9ef447adaa.png)

There are two things worth noticing:

- There is a folder called mixins.
- There is a main_model.

In Python there is a class synax like this:
```
class PythonClass(PythonMixin1, PythonMixin2):
  pass
```

What this does is that PythonClass gets all the members and variables from PythonMixin1 and PythonMixin2. This approach can help us separate the concerns from the main_model and put them into separate files in mixin. Indeed, this kind of extraction is also done in the view folder and controller folder.

Data can come from the database or local files, so there are the "DatabaseMixin" in database.py and "FileIOMixin" in file_IO.py. We have one extra file called "initial_load.py", which is for loading the data when the application starts.

**View**

The View in MVP stands for the GUI interface. The folder structure of the view is this:

![image](https://user-images.githubusercontent.com/90679381/226848701-8566f041-b834-4720-8b1b-39dc504c945b.png)

As you can see, similiarly we have a folder called mixins and this time a main_view that inherits the mixins. 

PYQT, the GUI library of this application, uses ui files to store the GUI layout and structure. Therefore, we have a new folder called ui_files.

A simple explanation of the ui_files folder and the mixins folder is here:

mixins:

- about_window.py: it contains the code related to the pop_up window when you click "about" in the menu bar.
- adjust_window.py: it contains the code related to the pop_up window when you click "weights adjustment. In this pop up you can adjust the relative importance of the criteria of comparisons.
- image_window.py
- ply_window.py

ui_files:
- MainWindow.py: it contains the XML-ish file that describes the layout of the main program
- adjust.py: it contains the pop-up layout for the code related to adjust_window.py

**Presenter**

The model governs the data while the view determines the GUI interface. The presenter acts as a middleman between the two. It(presenter) connects buttons in the GUI(view) and the data(Model), thus allowing the program to update the shred, change parameters, remove matching, so on and so forth.

![image](https://user-images.githubusercontent.com/90679381/226854424-0952e321-f224-4f0a-9188-9986dfdb828e.png)

As you can see, there are way more folders and files within the mixin folders, what is going on here?

We can group them into two categories:

- similarity calculation
- loading files and images
- updating matching info

Similarity calculation

- main_measure_pixels_data.py: it contains the code related to getting the pixels' information. To minimise code per file, we have a measure_pixels_data folder to contain more code for the same purpose.
- main_calculuate_similarity.py: it contains the code related to calculuate the similarity between 3d models and 2d jpegs. Similarly, we have a extra folder called calculuate_similarity to reduce code per file
- calculuate_all_features.py: to speed up the application, I already calculuated a lot of data of the 3d models and 2d jpegs and ran the functions inside this mixin. For now this part of code is not in use.

Loading Files and Images

- select_path.py: it contains the code related to set up the current context directory to work on.
- main_load_jpgs_plys.py: it contains the code related to loading the jpegs and plys in the current path. Extra folder is used to reduce code size per file.
- load_1_jpg_pair.jpg: it contains the code related to loading the current pair of jpegs we want to consider
- display_3d_model.py: it contains the code related to displaying the 3d model we want to consider

Updating matching info

- add_and_remove_match.py it contains the code related to add a new match or remove an existent match from the database.









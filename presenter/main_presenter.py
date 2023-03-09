from presenter.mixins.select_path import SelectPathMixin
from presenter.mixins.main_load_jpgs_plys import LoadJpgsPlysMixin
from presenter.mixins.add_and_remove_match import AddAndRemoveMatchMixin
from presenter.mixins.load_1_jpg_pair import Load1jpgPairMixin
from presenter.mixins.display_3d_model import Display3dModelMixin
from presenter.mixins.main_calculuate_similarity import CalculateSimilarityMixin
from presenter.mixins.main_measure_pixels_data import MeasurePixelsDataMixin
import time
import re
from pathlib import PurePath
class Mainpresenter(
    SelectPathMixin,
    MeasurePixelsDataMixin,
    CalculateSimilarityMixin,
    Load1jpgPairMixin,
    LoadJpgsPlysMixin,
    AddAndRemoveMatchMixin,
    Display3dModelMixin,
):


    def calculuate_all_jpgs(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        jpg_path_pairs = main_model.get_all_jpgs()
        count = 0
        validCount = 0
        all_jpgs_measurements = []
        for pair in jpg_path_pairs:
            print(f"count: {count}")
            print(f"validCount: {validCount}")
            img_1_path = pair[0]
            img_2_path = pair[1]
            #
            if count % 100 == 0:
                print("saving")
                self.main_model.simple_save_json(all_jpgs_measurements, f"saved__measurement_jpg_data.json")

               
            try:
                area_img_1,  area_img_2, light_ima_1, light_ima_2, img_1_width_length, img_2_width_length= self.measure_pixels_2d(img_1_path, img_2_path)

                img_1_data = {
                    "area_img_1": area_img_1,
                    "light_ima_1": light_ima_1,
                    "img_1_width_length": img_1_width_length,
                    "img_1_path" : img_1_path,
                }
                all_jpgs_measurements.append(img_1_data)
                img_2_data = {
                    "area_img_2": area_img_2,
                    "light_ima_2": light_ima_2,
                    "img_2_width_length": img_2_width_length,
                    "img_2_path" : img_2_path,
                }
                all_jpgs_measurements.append(img_2_data)
                print(f"img_1_path: {img_1_path}")
                print(f"img_2_path: {img_2_path}")
                validCount += 1
            except:
                print("We faced an error!")
            count +=1
        self.main_model.simple_save_json(all_jpgs_measurements, f"saved__measurement_jpg_data{time.time()}.json")

    def calculuate_all_plys(self):
    
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        
        ply_paths = main_model.get_all_plys()
        
        pls_measurement = []
        actualConut = 0
        count = 0
        tempjson = main_model.simple_get_json("./computation/saved__measurement_ply_data.json")
        tempSet = set()
        for row in tempjson:
            if not row["path"] in tempSet:
                print(f"Adding {row['path']}")
                tempSet.add(row["path"])
        
        for path in ply_paths:
            print(f"count: {count}")
            

            if not path in tempSet:
                #if actualConut % 100 == 0:
                 #   self.main_model.simple_save_json(pls_measurement, f"saved__measurement_ply_data{time.time()}.json")
                try:
                    print(f"Actual count: {actualConut}")
                    print(f"Loading 3d model: {path}")
                    main_view.operationLabel.setText(f"Loading: {path}")
                    #Extra the batch and piece number from the path
                    parts = (PurePath(path).parts)
                    m = re.search(
                            main_model.path_variables["MODELS_FILES_RE"],
                        path.replace("\\", "/"),
                    )
                    
                    batch_num = m.group(1)
                    piece_num = m.group(2)
            
                    now = time.time()
                    brightness_3d = list(main_presenter.get_brightnesses_3d(path))    
                    (
                        area,
                        width_length_summary,
                    ) = main_presenter.get_3d_object_area_and_width_length(path)

                    

                    width_length_summary = list(width_length_summary)
                    
                    
                    hemisphere = parts[4]
                    zone = parts[5]
                    utm_easting = parts[6]
                    utm_northing = parts[7]
                    context = parts[8]
                    temp = {
                        "path": path, "batch_num": batch_num, "piece_num": piece_num,
                        "brightness_summary": brightness_3d,
                        "area": area, "width_length_summary": width_length_summary,
                        "context":context, "zone":zone, "hemisphere": hemisphere, "utm_easting": utm_easting,"utm_northing": utm_northing
                    }
            

                    pls_measurement.append(temp)
                    actualConut +=  1
                except:
                    print(F"The path {path} doesn't work")
            count += 1
        self.main_model.simple_save_json(pls_measurement, f"./computation/saved__measurement_ply_data{time.time()}.json")
        print(path)
    def __init__(self, model, view):

        self.main_model = model
        self.main_view = view
        main_presenter = self
        
        self.main_model.prepare_data(self.main_view)
        
        self.main_view.set_up_view_presenter_connection(main_presenter)
        self.populate_hemispheres()
        view.contextDisplay.setText(main_presenter.get_context_string())

        MeasurePixelsDataMixin.__init__(self, self.main_view, self.main_model)
       
        super().__init__(self.main_view, self.main_model)

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self

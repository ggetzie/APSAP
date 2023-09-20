from glob import glob
import os
class FindsAndObjectsFilter:


    def batch_start_change(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.batch_end.setMinimum(main_view.batch_start.value())

    def batch_end_change(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.batch_start.setMaximum(main_view.batch_end.value())

    def find_start_change(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.find_end.setMinimum(main_view.find_start.value())

    def find_end_change(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.find_start.setMaximum(main_view.find_end.value())

    def set_filter(self):
         
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        # Deselect finds list
        main_view.finds_list.setCurrentItem(None)
        main_view.finds_list.clear()

        # #Remove all 3d models from
        # main_view.sorted_model_list.clear()

        main_presenter.clearInterface()
        # When we load finds, we also know the years the 3d models belong to
  

        context_dir = main_presenter.get_context_dir()
        from pathlib import Path

        # We first set the min and max of the filter
        years_folder_path = (
            context_dir / main_model.path_variables["BATCH_3D_SUBDIR"] / "*"
        ).as_posix()
        years = [Path(path).parts[-1] for path in glob(years_folder_path)]

        if not years:  # Empty
            main_view.year.setMinimum(0)
            main_view.year.setMaximum(0)
            main_view.year.setReadOnly(True)
        else:
            yearsSet = set()
            for year in years:
                try:
                    yearsSet.add(int(year))
                except:
                    pass
            main_view.year.setMinimum(min(yearsSet))
            main_view.year.setMaximum(max(yearsSet))
            main_view.year.setReadOnly(False)

        batch_nums_folder_path = (
            context_dir / main_model.path_variables["BATCH_3D_SUBDIR"] / "*" / "*"
        ).as_posix()
        # One line to turn the get all batch numbers situated in the year(s) folder of a context
        batch_nums = []
        for path in glob(batch_nums_folder_path):
            if "batch_" == Path(path).parts[-1][:6]:
                batch_nums.append(int(Path(path).parts[-1].replace("batch_", "")))

        if batch_nums:
            batch_min = min(batch_nums)
            batch_max = max(batch_nums)
            main_view.batch_start.setReadOnly(False)
            main_view.batch_end.setReadOnly(False)

        else:
            batch_min = 0
            batch_max = 0
            main_view.batch_start.setReadOnly(True)
            main_view.batch_end.setReadOnly(True)

        main_view.batch_start.setMinimum(batch_min)
        main_view.batch_start.setMaximum(batch_max)
        main_view.batch_start.setValue(batch_min)
        main_view.batch_end.setMinimum(batch_min)
        main_view.batch_end.setMaximum(batch_max)
        main_view.batch_end.setValue(batch_max)

        finds_photo_dir = main_model.path_variables["FINDS_PHOTO_DIR"]

        nums = glob(
            (context_dir / main_model.path_variables["FINDS_SUBDIR"] / "*").as_posix()
        )
        find_nums = []
        for i in nums:
            path1 = Path(i) / finds_photo_dir / "1.jpg"
            path2 = Path(i) / finds_photo_dir / "2.jpg"
            if os.path.exists(path1) and os.path.exists(path2):
                if Path(i).parts[-1].isnumeric():
                    find_nums.append(int(Path(i).parts[-1]))

        if find_nums:
            find_min = min(find_nums)
            find_max = max(find_nums)
            main_view.find_start.setReadOnly(False)
            main_view.find_end.setReadOnly(False)
        else:
            find_min = 0
            find_max = 0
            main_view.find_start.setReadOnly(True)
            main_view.find_end.setReadOnly(True)

        main_view.find_start.setMinimum(find_min)
        main_view.find_start.setMaximum(find_max)
        main_view.find_start.setValue(find_min)
        main_view.find_end.setMinimum(find_min)
        main_view.find_end.setMaximum(find_max)
        main_view.find_end.setValue(find_max)

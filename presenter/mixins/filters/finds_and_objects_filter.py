class FindsAndObjectsFilter:
    def set_filter(self):
        """This function cleans the interface then set up appropriate filters in the
        interface based on the current path"""
        _, _, main_presenter = self.get_model_view_presenter()
        main_presenter.block_signals(True)
        main_presenter.clear_interface()

        main_presenter.set_year_filter()
        main_presenter.set_batch_filter()
        main_presenter.set_find_filter()
        main_presenter.block_signals(False)

    def set_year_filter(self):
        """This function sets up the max and min of the year filters based on the year
        subfolders(which have values like 2022, 2021, 2023)"""

        main_model, main_view, _ = self.get_model_view_presenter()
        years = {
            m.batch_year for m in main_model.a3dmodels_list
        }  # set of unique batch_years

        # if there is not a single year folder in the current path, we disable the filter and return
        if not years:
            main_view.year.setMinimum(0)
            main_view.year.setMaximum(0)
            main_view.year.setReadOnly(True)
            return

        # We set the minimum and maximum of our filter to be the max and min of the years we got.
        main_view.year.setMinimum(min(years))
        main_view.year.setMaximum(max(years))
        main_view.year.setReadOnly(False)
        return

    def set_batch_filter(self):
        """This function sets up the min and max of the batch filter based on the
        batch subfolders"""
        main_model, main_view, _ = self.get_model_view_presenter()

        batch_nums = {m.batch_number for m in main_model.a3dmodels_list}

        # We set the default value of the batch_start and batch_end to be 0 and read only
        batch_min = 0
        batch_max = 0
        main_view.batch_start.setReadOnly(True)
        main_view.batch_end.setReadOnly(True)

        # If we really have valid batch folders, we find their min and max, then set
        # the batch filter to be writable
        if batch_nums:
            batch_min = min(batch_nums)
            batch_max = max(batch_nums)
            main_view.batch_start.setReadOnly(False)
            main_view.batch_end.setReadOnly(False)

        # Set the min and max of batch start and batch end to the appropriate values
        main_view.batch_start.setMinimum(batch_min)
        main_view.batch_start.setMaximum(batch_max)
        main_view.batch_start.setValue(batch_min)
        main_view.batch_end.setMinimum(batch_min)
        main_view.batch_end.setMaximum(batch_max)
        main_view.batch_end.setValue(batch_max)

    def set_find_filter(
        self,
    ):
        """This function sets up the min and max of the find filter based on the the find
        subfolders"""
        main_model, main_view, _ = self.get_model_view_presenter()

        find_nums = sorted({f.find_number for f in main_model.finds_list})

        # Set the default values of all finds's min and max as 0 and the GUI to be readonly
        find_min = 0
        find_max = 0
        main_view.find_start.setReadOnly(True)
        main_view.find_end.setReadOnly(True)

        # If there are legitimate finds under the current folder, we enable the GUI and set
        # the min and max of the finds accordingly.
        if find_nums:
            find_min = min(find_nums)
            find_max = max(find_nums)
            main_view.find_start.setReadOnly(False)
            main_view.find_end.setReadOnly(False)

        # Set the min and max of find start and find end to the appropriate values
        main_view.find_start.setMinimum(find_min)
        main_view.find_start.setMaximum(find_max)
        main_view.find_start.setValue(find_min)
        main_view.find_end.setMinimum(find_min)
        main_view.find_end.setMaximum(find_max)
        main_view.find_end.setValue(find_max)

    def batch_start_change(self):
        """This function set the minimum of the batch_end Spinbox to be the current value
        of batch_start.

        This helps maintain the property that batch_start is smaller or equal to batch_end
        """
        _, main_view, _ = self.get_model_view_presenter()
        main_view.batch_end.setMinimum(main_view.batch_start.value())

    def batch_end_change(self):
        """This function set the maximum of the batch_start Spinbox to be the current value
        of batch_end.

        This helps maintain the property that batch_start is smaller or equal to batch_end
        """
        _, main_view, _ = self.get_model_view_presenter()
        main_view.batch_start.setMaximum(main_view.batch_end.value())

    def find_start_change(self):
        """This function set the minimum of the find_end Spinbox to be the current value
        of find_start.

        This helps maintain the property that find_start is smaller or equal to find_end
        """
        _, main_view, _ = self.get_model_view_presenter()
        main_view.find_end.setMinimum(main_view.find_start.value())

    def find_end_change(self):
        """This function set the maximum of the find_start Spinbox to be the current value
        of find_end.

        This helps maintain the property that find_start is smaller or equal to find_end
        """
        _, main_view, _ = self.get_model_view_presenter()
        main_view.find_start.setMaximum(main_view.find_end.value())

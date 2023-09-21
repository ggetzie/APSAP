from glob import glob


class get3dModelSortedBySimilarityMixin:
    def get_potential_3d_models_sorted_by_similarity(self, find_path):
        """Given a certain path of a find, we have two images, 1.jpg and 2.jpg. By comparing them with the 3d model, we can have a sorted
        list of 3d models sorted by how similiar that find is with respect to the 3d models. This function gets such a sorted list

        Args:
            find_path (str): The path to the find in which we have 1.jpg and 2.jpg. We compare the 3d models

        Returns:
             list[batch_num, piece_num, year]: A list of batch_num piece_num, year, which uniquly define a 3d model.
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        # Getting the path to the front and back images
        path_front = find_path / "1.jpg"
        path_back = find_path / "2.jpg"

        # Measuring all the relevant data of the front and back images so that we can compare them with the data of the 3d models later
        (
            (area_front, width_front, length_front, contour_front),
            (area_back, width_back, length_back, contour_back),
        ) = main_presenter.measure_pixels_2d(path_front, path_back)

        # The list will be appened with [similarity_mean, batch_num, piece_num, year] of all 3d models we want to compare with
        similarity_scores = []

        # A regular expression with which that we search all relevant 3d models.
        model_paths_re = str(
            main_presenter.get_context_dir()
            / main_model.path_variables["MODELS_FILES_DIR"]
        )

        # Iterating all 3d models
        for path_3d in glob(model_paths_re):
            # Measure all the relevant data of the 3d model
            (
                area_3d,
                (width_3d, length_3d),
                contour_3d,
                year,
                batch_num,
                piece_num,
            ) = main_presenter.measure_pixels_3d(path_3d)

            # If the batch number is outside of the filter or the year doesn't match, we skip this 3d model!.
            if (
                int(batch_num) < int(main_view.batch_start.value())
                or int(batch_num) > int(main_view.batch_end.value())
                or int(year) != int(main_view.year.value())
            ):
                continue

            # We update the GUI to show which 3d model we are calculating the 3d model of
            main_view.statusLabel.setText(f"Calculate the similarity with {path_3d}")
            main_view.statusLabel.repaint()

            # Then we calculuat the similarity with respect to different criteria
            area_similarity = main_presenter.get_area_similarity(
                area_3d,
                area_front,
                area_back,
            )

            width_length_similarity = main_presenter.get_width_length_similarity(
                width_3d,
                length_3d,
                width_front,
                length_front,
                width_back,
                length_back,
            )

            contour_simlarity = main_presenter.get_contour_simlarity(
                contour_3d, contour_front, contour_back
            )
            # We get a weighted mean of similarity for this model.
            similarity_mean = (
                area_similarity * 1.2
                + width_length_similarity * 0.2
                + contour_simlarity * 0.7
            )
            # We append the similarity and 3d model data to the list we defined
            similarity_scores.append([similarity_mean, batch_num, piece_num, year])

        # We return a list of 3d model sorted by their similarity_mean, we ignore similarity_mean
        # so we effectively are returning a list of [batch_num, piece_num, year]
        return [items[1:] for items in sorted(similarity_scores)]

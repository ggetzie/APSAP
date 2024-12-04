import random

from model.main_model import MainModel
import model.models as models
import model.measure as gabe
import presenter.main_presenter as main_presenter

presenter = main_presenter.MainPresenter()
sc = models.TEST_SC
finds = sc.list_finds(presenter.main_model.conn.cursor())
a3dmodels = sc.list_models()


def compare():
    sample_finds = random.sample(finds, 10)

    for find in sample_finds:
        front_path = find.photo_path("front")
        back_path = find.photo_path("back")
        bert_area_front, bert_width_front, bert_length_front, bert_contour_front = (
            presenter.get_area_width_length_contour2d(str(front_path))
        )

        bert_area_back, bert_width_back, bert_length_back, bert_contour_back = (
            presenter.get_area_width_length_contour2d(str(back_path))
        )

        find.measure(
            ceramic_predictor=presenter.main_model.predictors["ceramics"],
            color_grid_predictor=presenter.main_model.predictors["colorgrid"],
            cache=presenter.main_model.measure_cache,
        )
        rows = ["width", "length", "area"]
        l_offset = max(len(row) for row in rows) + 2
        print(f"Front measurements for {find}")
        print(f"{'bert'.center(10)}\t{'gabe'.center(10)}".rjust(l_offset))
        print(f"width: {bert_width_front:.2f}\t{find.width_front:.2f}".rjust(l_offset))
        print(
            "length: {bert_length_front:.2f}\t{find.length_front:.2f}".rjust(l_offset)
        )
        print("area: {bert_area_front:.2f}\t{find.area_front:.2f}".rjust(l_offset))

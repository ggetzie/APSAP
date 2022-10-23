import pandas as pd
import numpy as np
from pathlib import Path

pd.set_option("display.max_rows", 1000)
basedir = Path(__file__).resolve().parent


def identify_range_of_batches(
    trench_northing, trench_easting, current_context, current_piece
):
    # trench_northing = trench_northing
    # trench_easting = trench_easting
    # current_context = current_context
    # current_piece = current_piece

    print(trench_northing, trench_easting, current_context, current_piece)
    path = basedir / "data" / str(trench_northing) / str(trench_easting)
    if not path.exists():
        return []

    # path = basedir.joinpath(
    #     "data" "\\{}_{}_reference.csv".format(trench_northing, trench_easting)
    # )
    print(str(path))
    df = pd.read_csv(path)
    context_lines = pd.DataFrame(df["context_num"].dropna())
    context_lines.insert(loc=0, column="row_num", value=np.arange(len(context_lines)))
    context_start = context_lines[df["context_num"] == current_context]
    current_row_number = context_start.iloc[0, 0]
    if current_row_number == len(context_lines) - 1:
        current_start_num = context_start.index[0]
        current_end_num = len(df)
    else:
        context_next = context_lines.loc[
            context_lines["row_num"] == current_row_number + 1
        ]
        current_start_num = context_start.index[0]
        current_end_num = context_next.index[0]

    current_context_df = df.iloc[current_start_num:current_end_num, :]
    current_context_df["range"] = (
        current_context_df["range"].dropna().apply(lambda x: int(x.split("-")[0]))
    )

    batches_start = current_context_df[
        current_context_df["range"] <= int(current_piece)
    ].iloc[-1]
    range_markers = pd.DataFrame(current_context_df[["range", "batch_num"]].dropna())
    range_markers.insert(loc=0, column="row_num", value=np.arange(len(range_markers)))
    current_batch_row_num = range_markers.loc[batches_start.name]["row_num"]
    range_start = batches_start.name
    if current_batch_row_num == len(range_markers) - 1:
        next_range = current_context_df.iloc[len(current_context_df) - 1].name
        current_range_df = df.iloc[range_start : next_range + 1, :]
        output = current_range_df["batch_num"].tolist()
    else:
        next_range = (
            range_markers.loc[range_markers["row_num"] == current_batch_row_num + 1]
        ).index[0]
        current_range_df = df.iloc[range_start:next_range, :]
        output = current_range_df["batch_num"].tolist()
    return output

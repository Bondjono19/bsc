import numpy as np
def get_reference_points():
    return np.array(
            [
                [38.29459953, 51.69630051],
                [73.53179932, 51.50139999],
                [56.02519989, 71.73660278],
                [41.54930115, 92.3655014 ],
                [70.72990036, 92.20410156]
            ],
            dtype=np.float32
        )

#0: right eye     1: left eye    2: nose      3: right    4: left
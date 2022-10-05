#%%

import numpy as np

def correction_pm25(pm25:np.array, humidity:np.array) -> np.array:

    return 0.524 * pm25 - 0.0862 * humidity + 5.75


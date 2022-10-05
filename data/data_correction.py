#%%

import numpy as np

def correction_pm25(pm25:np.array, humidity:np.array) -> np.array:

    return 0.524 * pm25 - 0.0862 * humidity + 5.75

# %%

# trying things
a = df_all['PM25 (ug/m3)'].to_numpy()
b = df_all['Humidity (%HR)'].to_numpy()

df_all['PM25 (HR-corr)'] = correction_pm25(a,b)
# %%

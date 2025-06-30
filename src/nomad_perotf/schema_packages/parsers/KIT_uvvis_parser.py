from scipy.signal import argrelextrema, savgol_filter
import numpy as np
from io import StringIO
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.signal import argrelextrema, savgol_filter
from scipy.optimize import curve_fit


def find_peaks_and_fit_gaussian(x, y):
    
    def gaussian(x, amp, cen, wid):
        return amp * np.exp(-((x - cen) ** 2) / (2 * wid**2))
    
    peaks = argrelextrema(y, np.greater)[0]
    if peaks.size == 0:
        return []

    results = []
    y_masked = np.copy(y)
    while True:
        peaks = argrelextrema(y_masked, np.greater)[0]
        if peaks.size == 0:
            break
        
        peak = peaks[np.argmax(y_masked[peaks])]
        peak_energy = x[peak]
        
        if len(results) > 0 and y_masked[peak] < results[0][1][0] / 4:
            break
        
        fitting_range = (x > peak_energy - 0.1) & (x < peak_energy + 0.1)
        try:
            popt, _ = curve_fit(gaussian, x[fitting_range], y[fitting_range], p0=[y[peak], peak_energy, 0.05])
            results.append((popt[1], popt, fitting_range))
        except RuntimeError:
            break
        
        y_masked[fitting_range] = 0
    return results

def get_uvvis_data(filedata):
    df = pd.read_csv(StringIO(filedata), sep=r';', header=0, names=["wavelength", "reflection", "transmission"])
    df = df.astype(float)

    df["photonenergy"] = 1239.841984 / df["wavelength"]
    df["absorption"] = 100. - df["reflection"] - df["transmission"]

    energy_range = np.linspace(df["photonenergy"].min(), df["photonenergy"].max(), 1001)
    spline = CubicSpline(df["photonenergy"].tolist(), df["absorption"].tolist())
    interpolated_absorption = spline(energy_range)
    smoothed_absorption = savgol_filter(interpolated_absorption, window_length=101, polyorder=3)
    derivate_absorption = np.gradient(smoothed_absorption, energy_range)
    result = find_peaks_and_fit_gaussian(energy_range, derivate_absorption)
    
    df_ = {"photonenergy": df["photonenergy"].tolist(), "absorption":  df["absorption"].tolist(), "energy_range": energy_range, "smoothed_absorption": smoothed_absorption, "derivate_absorption": derivate_absorption, "Eg,popt,f_r": result}
    #fig = plot_results(df["photonenergy"].tolist(), df["absorption"].tolist(), energy_range, smoothed_absorption, derivate_absorption, result)
    return df_
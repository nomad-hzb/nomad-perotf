"""
Plotly figures for the measurement entries.

The entry layouts of the new NOMAD GUI (v2) only show plots stored in the entry's own
PlotSection.figures; they ignore the a_plot annotation and figures of sub sections,
which is where baseclasses puts its JV, MPP, EQE, UV-vis and XRD curves. These
functions build the same curves as figures of the entry.
"""

import plotly.graph_objects as go
from nomad.datamodel.metainfo.plot import PlotlyFigure


def magnitude(quantity, unit):
    return None if quantity is None else quantity.to(unit).magnitude


def figure(label, traces, xaxis, yaxis, **layout):
    fig = go.Figure(data=traces)
    fig.update_layout(xaxis_title=xaxis, yaxis_title=yaxis, showlegend=True, **layout)
    return PlotlyFigure(label=label, figure=fig.to_plotly_json())


def jv_figures(jv_curves):
    traces = [
        go.Scatter(
            x=magnitude(curve.voltage, 'V'),
            y=magnitude(curve.current_density, 'mA/cm**2'),
            name=curve.cell_name,
            mode='lines',
        )
        for curve in jv_curves
        if curve.voltage is not None and curve.current_density is not None
    ]
    if not traces:
        return []
    return [figure('JV curves', traces, 'Voltage (V)', 'Current density (mA/cm²)')]


def mpp_figures(mpp):
    if mpp.time is None or mpp.power_density is None:
        return []
    time = magnitude(mpp.time, 's')
    traces = [
        go.Scatter(
            x=time,
            y=magnitude(mpp.power_density, 'mW/cm**2'),
            name='Power density',
            mode='lines',
        )
    ]
    if mpp.voltage is not None:
        traces.append(
            go.Scatter(
                x=time,
                y=magnitude(mpp.voltage, 'V'),
                name='Voltage',
                mode='lines',
                yaxis='y2',
            )
        )
    return [
        figure(
            'MPP tracking',
            traces,
            'Time (s)',
            'Power density (mW/cm²)',
            yaxis2=dict(title='Voltage (V)', overlaying='y', side='right'),
        )
    ]


def eqe_figures(eqe_data):
    traces = [
        go.Scatter(
            x=magnitude(eqe.wavelength_array, 'nm'),
            y=eqe.eqe_array,
            name=eqe.eqe_data_file or f'EQE {i + 1}',
            mode='lines',
        )
        for i, eqe in enumerate(eqe_data)
        if eqe.wavelength_array is not None and eqe.eqe_array is not None
    ]
    if not traces:
        return []
    return [figure('EQE', traces, 'Wavelength (nm)', 'EQE')]


def uvvis_figures(measurements):
    traces = [
        go.Scatter(
            x=magnitude(measurement.wavelength, 'nm'),
            y=measurement.intensity,
            name=measurement.name,
            mode='lines',
        )
        for measurement in measurements
        if measurement.wavelength is not None and measurement.intensity is not None
    ]
    if not traces:
        return []
    return [figure('UV-vis', traces, 'Wavelength (nm)', 'Intensity (%)')]


def xrd_figures(data):
    if data is None or data.angle is None or data.intensity is None:
        return []
    trace = go.Scatter(
        x=magnitude(data.angle, 'degree'),
        y=data.intensity,
        name=data.name or 'XRD',
        mode='lines',
    )
    return [figure('XRD', [trace], '2θ (°)', 'Counts')]

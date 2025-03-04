from io import StringIO
import numpy as np
import pandas as pd
from scipy import interpolate


def identify_file_type(file_content):
    """
    Identify whether the file is from LabVIEW or Python
    by checking for specific keywords.
    """
    if 'Singapore Solar Simulator, Python' in file_content:

        return 'python'

    return 'labview'


def calculatePVparametersFromJV(
    jvData, cellArea=0.105, lineFittingDataPoints=20):
    digitsPCE = 2
    digitsJSC = 2
    digitsVOC = 5
    digitsFF = 2
    digitsRS = 0
    digitsRSHUNT = 0

    v = jvData[:, 0]
    j = (jvData[:, 1], jvData[:, 2])

    p = (v * j[0], v * j[1])

    ind_mpp = (np.argmax(p[0]), np.argmax(p[1]))

    mpp = ((v[ind_mpp[0]], j[0][ind_mpp[0]]), 
           (v[ind_mpp[1]], j[1][ind_mpp[1]]))

    f0 = interpolate.interp1d(v, j[0])
    f1 = interpolate.interp1d(v, j[1])
    v_new = np.linspace(v[0], v[len(v) - 1], 1000)
    j_interpolated = (f0(v_new), f1(v_new))

    # check if the curve crosses both axes

    if (True in np.diff(np.signbit(j_interpolated[0]))) & (
        True in np.diff(np.signbit(v_new))
    ):
        try:
            voc_ind = (
                np.where(np.diff(np.signbit(j_interpolated[0])))[0].item(),
                np.where(np.diff(np.signbit(j_interpolated[1])))[0].item(),
            )
            voc = (
                np.round(v_new[voc_ind[0]], digitsVOC),
                np.round(v_new[voc_ind[1]], digitsVOC),
            )
        except BaseException:
            voc_ind = (
                np.where(np.diff(np.signbit(j_interpolated[0])))[0][0],
                np.where(np.diff(np.signbit(j_interpolated[1])))[0][0],
            )
            voc = (
                np.round(v_new[voc_ind[0]], digitsVOC),
                np.round(v_new[voc_ind[1]], digitsVOC),
            )

        jsc_ind = (
            np.where(np.diff(np.signbit(v_new)))[0].item(),
            np.where(np.diff(np.signbit(v_new)))[0].item(),
        )

        jsc = (
            np.round(j_interpolated[0][jsc_ind[0]], digitsJSC),
            np.round(j_interpolated[1][jsc_ind[1]], digitsJSC),
        )

        if voc[0] > 0 and jsc[0] > 0:
            ff = (
                np.round((mpp[0][0] * mpp[0][1]) / (voc[0] * jsc[0]) * 100, digitsFF),
                np.round((mpp[1][0] * mpp[1][1]) / (voc[1] * jsc[1]) * 100, digitsFF),
            )
        else:
            ff = (0,0)
            
            # v_quadrant_0=v_new[jsc_ind[0]:voc_ind[0]]
            # j_quadrant_0=j_interpolated[0][jsc_ind[0]:voc_ind[0]]
            
            # v_quadrant_1=v_new[jsc_ind[1]:voc_ind[1]]
            # j_quadrant_1=j_interpolated[1][jsc_ind[1]:voc_ind[1]]
            
            # p_quadrant_0=v_quadrant_0*j_quadrant_0
            # p_quadrant_1=v_quadrant_1*j_quadrant_1
            
            # ind_mpp = (np.argmax(np.abs(p_quadrant_0)), 
            #            np.argmax(np.abs(p_quadrant_1)))

       
            # mpp = ((v_quadrant_0[ind_mpp[0]], j_quadrant_0[ind_mpp[0]]), 
            #        (v_quadrant_1[ind_mpp[1]], j_quadrant_1[ind_mpp[1]]))
            
        
            # voc = np.abs(voc)
            # jsc = np.abs(jsc)
            # mpp = np.abs(mpp)
          
            # ff = (
            #     np.round((mpp[0][0] * mpp[0][1]) / (voc[0] * jsc[0]) * 100, digitsFF),
            #     np.round((mpp[1][0] * mpp[1][1]) / (voc[1] * jsc[1]) * 100, digitsFF),
            # )

        pce = (
            np.round(voc[0] * jsc[0] * ff[0] / 100, digitsPCE),
            np.round(voc[1] * jsc[1] * ff[1] / 100, digitsPCE),
        )

        try:
            m1, b1 = np.polyfit(
                v_new[
                    voc_ind[0] - lineFittingDataPoints : voc_ind[0]
                    + lineFittingDataPoints
                ],
                j_interpolated[0][
                    voc_ind[0] - lineFittingDataPoints : voc_ind[0]
                    + lineFittingDataPoints
                ],
                1,
            )
            rs_backward = np.round(((-1 / m1) / cellArea) / 1e-3, digitsRS)
        except BaseException:
            rs_backward = np.nan

        try:
            m2, b2 = np.polyfit(
                v_new[
                    voc_ind[1] - lineFittingDataPoints : voc_ind[1]
                    + lineFittingDataPoints
                ],
                j_interpolated[1][
                    voc_ind[1] - lineFittingDataPoints : voc_ind[1]
                    + lineFittingDataPoints
                ],
                1,
            )
            rs_forward = np.round(((-1 / m2) / cellArea) / 1e-3, digitsRS)

        except BaseException:
            rs_forward = np.nan

        r_s = (rs_backward, rs_forward)

        # at JSC there are more data points available
        factor = 4
        factor = 1

        try:
            m3, b3 = np.polyfit(
                v_new[
                    jsc_ind[0] - lineFittingDataPoints * factor : jsc_ind[0]
                    + lineFittingDataPoints * factor
                ],
                j_interpolated[0][
                    jsc_ind[0] - lineFittingDataPoints * factor : jsc_ind[0]
                    + lineFittingDataPoints * factor
                ],
                1,
            )
            i = 1
            while m3 > 0:
                m3, b3 = np.polyfit(
                    v_new[
                        jsc_ind[0] - lineFittingDataPoints + i : jsc_ind[0]
                        + lineFittingDataPoints
                        + i
                    ],
                    j_interpolated[0][
                        jsc_ind[0] - lineFittingDataPoints + i : jsc_ind[0]
                        + lineFittingDataPoints
                        + i
                    ],
                    1,
                )
                i += 1
            rshunt_backward = np.round(((-1 / m3) / cellArea) / 1e-3, digitsRSHUNT)

        except BaseException:
            rshunt_backward = np.nan

        try:
            m4, b4 = np.polyfit(
                v_new[
                    jsc_ind[1] - lineFittingDataPoints * factor : jsc_ind[1]
                    + lineFittingDataPoints * factor
                ],
                j_interpolated[1][
                    jsc_ind[1] - lineFittingDataPoints * factor : jsc_ind[1]
                    + lineFittingDataPoints * factor
                ],
                1,
            )
            i = 1
            while m4 > 0:
                m4, b4 = np.polyfit(
                    v_new[
                        jsc_ind[1] - lineFittingDataPoints * factor + i : jsc_ind[1]
                        + lineFittingDataPoints * factor
                        + i
                    ],
                    j_interpolated[1][
                        jsc_ind[1] - lineFittingDataPoints * factor + i : jsc_ind[1]
                        + lineFittingDataPoints * factor
                        + i
                    ],
                    1,
                )
                i += 1
            rshunt_forward = np.round(((-1 / m4) / cellArea) / 1e-3, digitsRSHUNT)

        except BaseException:
            rshunt_forward = np.nan

        r_shunt = (rshunt_backward, rshunt_forward)


    else:
        pce = (np.nan, np.nan)
        voc = (np.nan, np.nan)
        jsc = (np.nan, np.nan)
        ff = (np.nan, np.nan)
        r_shunt = (np.nan, np.nan)
        r_s = (np.nan, np.nan)

 

    return pce, voc, jsc, ff, r_shunt, r_s, mpp






def get_jv_data(filedata):
    
    file_type = identify_file_type(filedata)
    jv_dict = {}
    
    if file_type == 'labview':
            
        df_header = pd.read_csv(
            StringIO(filedata),
            skiprows=0,
            nrows=10,
            sep='\t',
            # index_col=0,
            engine='python',
        )
    
        jv_dict['active_area'] = float(df_header.iloc[1, 1])
        jv_dict['datetime'] = f'{df_header.iloc[3, 0]} {df_header.iloc[3, 1]}'
   
        df_curves = pd.read_csv(
            StringIO(filedata),
            # header=0,
            skiprows=11,
            sep='\t',
            engine='python',
        )
        
        df_curves = df_curves.dropna(how='all', axis=1)
        

        voc_help = df_curves.iloc[:, 0][np.where(np.diff(np.signbit(df_curves.iloc[:, 1])))[0][0].item()]
        jsc_help = df_curves.iloc[:, 1][np.where(np.diff(np.signbit(df_curves.iloc[:, 0])))[0][0].item()]

        
        

        if voc_help < 0:
            #     voltage = -voltage
            df_curves['Voltage [V]'] = df_curves['Voltage [V]'] * -1
  
        if jsc_help < 0:
        #     current = -current
            j_columns = [
                'Current density [1] [mA/cm^2]',
                'Current density [2] [mA/cm^2]',
                'Average current density [mA/cm^2]',
            ]
            df_curves[j_columns] = df_curves[j_columns] * -1
            

    
        if df_curves['Voltage [V]'][0]>df_curves['Voltage [V]'][len(df_curves['Voltage [V]'])-1]:         
            df_curves = df_curves.iloc[::-1].reset_index(drop=True)
            

           
    
        jv_dict['jv_curve'] = []
        for column in range(1, len(df_curves.columns) - 1):
            jv_dict['jv_curve'].append(
                {
                    'name': df_curves.columns[column],
                    'voltage': df_curves[df_curves.columns[0]].values,
                    'current_density': df_curves[df_curves.columns[column]].values,
                }
            )
    
        pce, voc, jsc, ff, RSHUNT, RS, mpp = calculatePVparametersFromJV(
            np.array(df_curves),
            cellArea=jv_dict['active_area'],
            lineFittingDataPoints=20,
        )
    
        jv_dict['P_MPP'] = list(
            (np.round(mpp[0][0] * mpp[0][1], 2), np.round(mpp[1][0] * mpp[1][1], 2))
        )
        jv_dict['J_MPP'] = list((mpp[0][1], mpp[1][1]))
        jv_dict['U_MPP'] = list((mpp[0][0], mpp[1][0]))
        jv_dict['R_ser'] = list(RS)
        jv_dict['R_par'] = list(RSHUNT)
            
        jv_dict['J_sc'] = list(jsc)
        jv_dict['V_oc'] = list(voc)
        jv_dict['Fill_factor'] = list(ff)
        jv_dict['Efficiency'] = list(pce)

            
    
    elif file_type == 'python':
        
        df_header = pd.read_csv(
            StringIO(filedata),
            skiprows=0,
            nrows=46,
            sep='\t',
            # index_col=0,
            engine='python',
        )
        
        
        jv_dict['active_area'] = float(df_header.loc['PixArea:'].iloc[0])
        jv_dict['datetime'] = f'{df_header.loc["DateTime:"].iloc[0]}'


        df_curves = pd.read_csv(
            StringIO(filedata),
            # header=0,
            skiprows=48,
            sep='\t',
            engine='python',
        )

        
        df_curves = df_curves.dropna(how='all', axis=1)
            
        
        voc_help = df_curves.iloc[:, 0][np.where(np.diff(np.signbit(df_curves.iloc[:, 1])))[0][0].item()]
        jsc_help = df_curves.iloc[:, 1][np.where(np.diff(np.signbit(df_curves.iloc[:, 0])))[0][0].item()]
        
               

        if voc_help < 0:
            #     voltage = -voltage
            df_curves['Voltage'] = df_curves['Voltage'] * -1
            

        if jsc_help < 0:
        #     current = -current
            j_columns = ['CurrentDensity','Current', ]
            df_curves[j_columns] = df_curves[j_columns] * -1
            
             
            
        if df_curves['Voltage'][0]>df_curves['Voltage'][len(df_curves['Voltage'])-1]:         
            df_curves = df_curves.iloc[::-1].reset_index(drop=True)
            

        df_curves['Current']=df_curves['CurrentDensity'].copy()
        

        jv_dict['jv_curve'] = []
        for column in range(1, len(df_curves.columns) - 1):
            jv_dict['jv_curve'].append(
                {
                    'name': df_curves.columns[column],
                    'voltage': df_curves[df_curves.columns[0]].values,
                    'current_density': df_curves[df_curves.columns[column]].values,
                }
            )
             
        pce, voc, jsc, ff, RSHUNT, RS, mpp = calculatePVparametersFromJV(
            np.array(df_curves),
            cellArea=jv_dict['active_area'],
            lineFittingDataPoints=20, )

             
        jv_dict['P_MPP'] = list([
            (np.round(mpp[0][0] * mpp[0][1], 2))]
        )
        jv_dict['J_MPP'] = list([mpp[0][1]])
        jv_dict['U_MPP'] = list([mpp[0][0]])
        jv_dict['R_ser'] = list([RS[0]])
        jv_dict['R_par'] = list([RSHUNT[0]])
            
        jv_dict['J_sc'] = list([jsc[0]])
        jv_dict['V_oc'] = list([voc[0]])
        jv_dict['Fill_factor'] = list([ff[0]])
        jv_dict['Efficiency'] = list([pce[0]])
             




    
    return jv_dict
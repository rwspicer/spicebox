"""
Digital Globe Tools
-------------------

Tools for processing dgtal globe data 

see:
https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf
and
https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf
 
"""

def calc_julian_days_dg(tlc_time):
    """Calculate the Julida dayys according to the fomula provided by
    DigitalGlobe. Found in section 4.1.2 
    here https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf

    Parameters
    ----------
    tlc_time: datetime.datetime

    Returns
    -------
    int:
        days since the beginning of the year -4712 
        Meuss, Jean. "Astronomical algorithms, 2nd Ed.." Richmond, VA: Willmann-Bell(1998). Pg 61
    """
    a = tlctime.year//100 
    b = 2 - a + (a // 4)
    UT = tlctime.hour + tlctime.minute/60 + (tlctime.second+tlctime.microsecond)/3600
    jd = int(365.25*tlctime.year+4716) + \
        int(30.6001*(tlctime.month+1)) + \
        tlctime.day + UT/24+b-1524.5
    return jd

def calc_dist_sun_earth_au(jd):
    """Caclulate the earth sun distance in AU. Found in section 4.1.2 
    here https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/207/Radiometric_Use_of_WorldView-3_v2.pdf

    Parameters
    ----------
    jd: int in julian days

    Returns
    -------
    float
        earth sun distance  in AU
    """
    d = jd - 2451545.0
    g = 357.529 + 0.98560028 * d
    d_es = 1.00014 - 0.01671 * np.cos(g) - 0.00014*np.cos(2*g)
    return d_es

def calc_absolute_radiometric_calibration(
        data, gain,offset, abs_cal_factor, effective_bandwidth, 
    ):
    """Calculates the absolute radiometric calibration of data
    see https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf
    for digital globe data

    Parameters 
    ----------
    data: np.array
        image data
    gain: number 
        gain value see document above
    offset: number
        offset value see document above
    abs_cal_factor: number
        calibration factor pulled from image metadata
    effective_bandwidth:
        calibration bandwidth pulled from image metadata

    Retruns
    -------
    radiometrically corrected image data correct
    """
    return gain*data*(abs_cal_factor/effective_bandwidth) + offset

def calc_toa_reflectance(radiance, dist_earth_sun, irradiance, theta):
    """Calculate the Top-of-Atmosphere reflectance for digital globe data
    see: https://dg-cms-uploads-production.s3.amazonaws.com/uploads/document/file/209/ABSRADCAL_FLEET_2016v0_Rel20170606.pdf    

    Parameters
    ----------
    radiance: Array
        input image data absolute radiometric radiance value 
    dist_earth_sun: Number
        Earth sun distance
    irradiance: Number
        Irradiance - see table 4 in document linked above
    theta:
        solar zenith angle

    Returns
    -------
    Reflectance data
    """
    ref = (radiance * (dist_earth_sun**2) * np.pi)/ (irradiance * np.cos(theta))
    return ref

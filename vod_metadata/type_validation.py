# Problems are often encountered reading ADIs (From Providers), which do not comply CableLabs® VOD Content Specification Version 1.1:
# - dates with invalid formats.
# - texts with more characters than those supported.
# - etc.

# In order to validate and correct, class must be called:
# vod_package = VodPackage("C:/Videos/The Hounds of Baskerville.xml", validate_type=True)

# if errors encountered:
# vod_package.D_ams = corrected ADI
# vod_package.D_ams_orig = original ADI

import datetime
import time
import random
import string

def validate_D_app(D_app):
    #  TODO
    return D_app

def validate_D_ams(D_ams):
    # Has been included corrections of errors captured from different providers.
    # Work in progress.

    # Asset_ID
    # Req
    # String (Fixed 20 chars, alpha/numeric) 4 alpha characters followed by 16 numbers, no spaces-Ex."ABCD1234567890123456"
    _asset_ids = []
    for k,v in D_ams.items():
        if 'Asset_ID' in D_ams[k]:
            _asset_ids.append(D_ams[k]['Asset_ID'])
        else:
            D_ams = _rebuild_asset_ids(D_ams)
            _asset_ids = []
            break
    if _asset_ids:
        for _aid in _asset_ids:
            if len(_aid) != 20:
                D_ams = _rebuild_asset_ids(D_ams)
                break
            # if first 4 characters contains digit, fail
            elif any(char.isdigit() for char in _aid[0:4]):
                D_ams = _rebuild_asset_ids(D_ams)
                break
            # if first 4 characters not upper, fail
            elif any(char.islower() for char in _aid[0:4]):
                D_ams = _rebuild_asset_ids(D_ams)
                break
            # if 4->20 characters not digits, fail
            elif any(char.isalpha() for char in _aid[4:20]):
                D_ams = _rebuild_asset_ids(D_ams)
                break
        # if duplicated assets_id fails
        if len(_asset_ids) != len(set(_asset_ids)):
            D_ams = _rebuild_asset_ids(D_ams)
    # Product
    # Req
    # An identifier for the product offering.String (Max 20 Chars)
    _products = []
    for k,v in D_ams.items():
        if 'Product' in D_ams[k]:
            _products.append(D_ams[k]['Product'])
        else:
            D_ams = _rebuild_products(D_ams)
            _products = []
            break
    if _products:
        for _prod in _products:
            if len(_prod) > 20:
                D_ams = _rebuild_products(D_ams)
                break
    # Asset_Name
    # Req
    # A string containing the identifying name of String (Max 50 chars) Asset names must be unique within a product.
    _asset_names = []
    for k,v in D_ams.items():
        if 'Asset_Name' in D_ams[k]:
            _asset_names.append(D_ams[k]['Asset_Name'])
        else:
            D_ams = _rebuild_asset_names(D_ams)
            _asset_names = []
            break
    if _asset_names:
        for _a_nam in _asset_names:
            if len(_a_nam) > 50:
                D_ams = _rebuild_asset_names(D_ams)
                break
        if len(_asset_names) != len(set(_asset_names)):
            D_ams = _rebuild_asset_names(D_ams)
    # Version_Major
    # Req
    # An integer representing the major version
    _versions_major = []
    for k,v in D_ams.items():
        if 'Version_Major' in D_ams[k]:
            _versions_major.append(D_ams[k]['Version_Major'])
        else:
            D_ams = _rebuild_versions_major(D_ams)
            _versions_major = []
            break
    if _versions_major:
        for _v_maj in _versions_major:
            if any(char.isalpha() for char in _v_maj):
                D_ams = _rebuild_versions_major(D_ams)
                break
    # Version_Minor
    # Req
    # An integer representing the minor version
    _versions_minor = []
    for k,v in D_ams.items():
        if 'Version_Minor' in D_ams[k]:
            _versions_minor.append(D_ams[k]['Version_Minor'])
        else:
            D_ams = _rebuild_versions_minor(D_ams)
            _versions_minor = []
            break
    if _versions_minor:
        for _v_min in _versions_minor:
            if any(char.isalpha() for char in _v_min):
                D_ams = _rebuild_versions_minor(D_ams)
                break
    # Description
    # Req
    # A human-readable string describing the Asset.
    _descriptions = []
    for k,v in D_ams.items():
        if 'Description' in D_ams[k]:
            _descriptions.append(D_ams[k]['Description'])
        else:
            D_ams = _rebuild_descriptions(D_ams)
            _descriptions = []
            break
    if _descriptions:
        for _desc in _descriptions:
            if _desc == '':
                D_ams = _rebuild_descriptions(D_ams)
                break
    # Creation_Date
    # Req
    # A string representing the date on which the Asset was created.
    # String – "yyyy-mm-dd" (2022-09-27)
    _creation_dates = []
    for k,v in D_ams.items():
        if 'Creation_Date' in D_ams[k]:
            _creation_dates.append(D_ams[k]['Creation_Date'])
        else:
            D_ams = _rebuild_creation_dates(D_ams)
            _creation_dates = []
            break
    if _creation_dates:
        for _cd in _creation_dates:
            try:
                datetime.datetime.strptime(_cd, '%Y-%m-%d')
            except ValueError:
                D_ams = _rebuild_creation_dates(D_ams)
                break
    # Provider_ID
    # Req
    # A unique identifier for the provider of the Asset. The Provider_ID must be set to a registered internet domain name
    # restricted to at most 20 lower-case characters and belonging to the provider. For example a valid Provider_ID for
    # CableLabs is "cableLabs-films.com" (19 chars)
    _provider_ids = []
    for k,v in D_ams.items():
        if 'Provider_ID' in D_ams[k]:
            _provider_ids.append(D_ams[k]['Provider_ID'])
        else:
            D_ams = _rebuild_provider_ids(D_ams)
            _provider_ids = []
            break
    if _provider_ids:
        for _p_id in _provider_ids:
            if len(_p_id) > 20:
                D_ams = _rebuild_provider_ids(D_ams)
                break
            elif any(char.isupper() for char in _p_id if char.isalpha):
                D_ams = _rebuild_provider_ids(D_ams)
                break
            elif not '.' in _p_id:
                D_ams = _rebuild_provider_ids(D_ams)
                break
    return D_ams

def _rebuild_asset_ids(D_ams):
    # Asset_ID
    # Req
    # String (Fixed 20 chars, alpha/numeric) 4 alpha characters followed by 16 numbers, no spaces-Ex."ABCD1234567890123456"
    _now = str(int(time.time()))
    _digits = string.digits * 4
    _n = 0
    for k,v in D_ams.items():
        D_ams[k]['Asset_ID'] = 'VOD' + string.ascii_uppercase[_n] + _now + '{:0>6}'.format(_digits[_n + 1])
        _n += 1
    return D_ams

def _rebuild_products(D_ams):
    # Product
    # Req
    # An identifier for the product offering.String (Max 20 Chars)
    _product = "FVOD;;;;;;;;"
    for k,v in D_ams.items():
        D_ams[k]['Product'] = _product
    return D_ams

def _rebuild_asset_names(D_ams):
    # Asset_Name
    # Req
    # A string containing the identifying name of String (Max 50 chars) Asset names must be unique within a product.
    # productive examples:
    # Asset_Name="We're Here - Temporada 01 - #01"
    # Asset_Name="We're Here - Temporada 01 - #01_HDPoster"
    # Asset_Name="We're Here - Temporada 01 - #01_movie"
    # Asset_Name="We're Here - Temporada 01 - #01_Title"
    # Asset_Name="We're Here - Temporada 01 - #01_box cover"
    _a_names = []
    _max_k_name = ''
    for k,v in D_ams.items():
        if len(k) > len(_max_k_name):
            _max_k_name = k
        if 'Asset_Name' in D_ams[k]:
            _a_names.append(D_ams[k]['Asset_Name'])
    _len_str = 50 - len(' - #01_' + _max_k_name)
    if len(_a_names) == 0:
        _base_a_name = 'You probably need to correct this field'[0:_len_str]
    else:
        _base_a_name = min([str(x) for x in _a_names])[0:_len_str]
    for k,v in D_ams.items():
        D_ams[k]['Asset_Name'] = _base_a_name + ' - #01_' + k
    return D_ams

def _rebuild_versions_major(D_ams):
    # Version_Major
    # Req
    # An integer representing the major version
    for k,v in D_ams.items():
        D_ams[k]['Version_Major'] = "1"
    return D_ams

def _rebuild_versions_minor(D_ams):
    # Version_Minor
    # Req
    # An integer representing the minor version
    for k,v in D_ams.items():
        D_ams[k]['Version_Minor'] = "0"
    return D_ams

def _rebuild_descriptions(D_ams):
    # Description
    # Req
    # A human-readable string describing the Asset.
    # productive examples:
    # Description="We're Here - Temporada 01 - #01"
    # Description="We're Here - Temporada 01 - #01_Title"
    # Description="We're Here - Temporada 01 - #01_movie"
    # Description=""
    _d_names = []
    for k,v in D_ams.items():
        if 'Description' in D_ams[k]:
            _d_names.append(D_ams[k]['Description'])
    if len(_d_names) == 0:
        _base_d_name = 'You probably need to correct this field'
    else:
        _base_d_name = min([str(x) for x in _d_names])
    for k,v in D_ams.items():
        D_ams[k]['Description'] = _base_d_name + ' - #01_' + k
    return D_ams

def _rebuild_creation_dates(D_ams):
    # Creation_Date
    # Req
    # A string representing the date on which the Asset was created.
    # String – "yyyy-mm-dd" (2022-09-27)
    _today = datetime.date.today().strftime('%Y-%m-%d')
    for k,v in D_ams.items():
        D_ams[k]['Creation_Date'] = _today
    return D_ams

def _rebuild_provider_ids(D_ams):
    # Provider_ID
    # Req
    # A unique identifier for the provider of the Asset. The Provider_ID must be set to a registered internet domain name
    # restricted to at most 20 lower-case characters and belonging to the provider. For example a valid Provider_ID for
    # CableLabs is "cableLabs-films.com" (19 chars)
    _provider_id = "cableLabs-films.com"
    for k,v in D_ams.items():
        D_ams[k]['Provider_ID'] = _provider_id
    return D_ams

import datetime
import os
import random

from vod_metadata import config_path, template_path
from vod_metadata.config_read import parse_config
from vod_metadata.vodpackage import VodPackage

__all__ = ["generate_metadata"]


def generate_metadata(file_path, vod_config):
    # Time-sensitive values
    timestamp = datetime.datetime.today()
    creation_date = timestamp.strftime("%Y-%m-%d")
    end_date = (timestamp + datetime.timedelta(days=999)).strftime("%Y-%m-%d")
    asset_id = timestamp.strftime("%Y%m%d%H%M")

    # Randomly-generated values
    suffix = format(random.randint(0, 9999), "04")
    title_billing_id = "{}B".format(suffix)

    # Start with a minimal metadata template
    vod_package = VodPackage(template_path, vod_config=vod_config)
    file_name = os.path.splitext(os.path.split(file_path)[1])[0]
    outfile_path = "{}_{}.xml".format(file_name, suffix)
    vod_package.xml_path = os.path.join(os.getcwd(), outfile_path)

    # Video file-specific value
    vod_package.D_content["movie"] = file_path
    vod_package.check_files()

    # Package section
    package_asset_name = "{} {} (package)".format(file_name[:20], suffix)
    package_description = "{} {} (package asset)".format(
        file_name[:20], suffix
    )
    package_asset_id = "{}P{}{}".format(vod_config.prefix, asset_id, suffix)

    vod_package.D_ams["package"] = {
        "Provider":  vod_config.provider,
        "Product": vod_config.product,
        "Asset_Name": package_asset_name,
        "Version_Major": '1',
        "Version_Minor": '0',
        "Description": package_description,
        "Creation_Date": creation_date,
        "Provider_ID": vod_config.provider_id,
        "Asset_ID": package_asset_id,
        "Asset_Class": "package"
    }
    vod_package.D_app["package"] = {"Metadata_Spec_Version": "CableLabsVOD1.1"}

    # Title section
    title_asset_name = "{} {} (title)".format(file_name[:20], suffix)
    title_description = "{} {} (title asset)".format(file_name[:20], suffix)
    title_asset_id = "{}T{}{}".format(vod_config.prefix, asset_id, suffix)
    title_title_brief = "{} {}".format(file_name[:14], suffix)
    title_title = "{} {}".format(file_name[:124], suffix)

    vod_package.D_ams["title"] = {
        "Provider":  vod_config.provider,
        "Product": vod_config.product,
        "Asset_Name": title_asset_name,
        "Version_Major": '1',
        "Version_Minor": '0',
        "Description": title_description,
        "Creation_Date": creation_date,
        "Provider_ID": vod_config.provider_id,
        "Asset_ID": title_asset_id,
        "Asset_Class": "title"
    }
    vod_package.D_app["title"] = {
        "Type": "title",
        "Title_Brief": title_title_brief,
        "Title": title_title,
        "Summary_Short": title_title,
        "Rating": ["NR"],
        "Closed_Captioning": 'N',
        "Year": timestamp.strftime("%Y"),
        "Category": [vod_config.title_category],
        "Genre": ["Other"],
        "Show_Type": "Other",
        "Billing_ID": title_billing_id,
        "Licensing_Window_Start": creation_date,
        "Licensing_Window_End": end_date,
        "Preview_Period": "300",
        "Provider_QA_Contact": "N/A"
    }

    # Movie section
    movie_asset_name = "{} {} (movie)".format(file_name[:20], suffix)
    movie_description = "{} {} (movie asset)".format(file_name[:20], suffix)
    movie_asset_id = "{}M{}{}".format(vod_config.prefix, asset_id, suffix)

    vod_package.D_ams["movie"] = {
        "Provider":  vod_config.provider,
        "Product": vod_config.product,
        "Asset_Name": movie_asset_name,
        "Version_Major": '1',
        "Version_Minor": '0',
        "Description": movie_description,
        "Creation_Date": creation_date,
        "Provider_ID": vod_config.provider_id,
        "Asset_ID": movie_asset_id,
        "Asset_Class": "movie"
    }
    vod_package.D_app["movie"]["Type"] = "movie"

    return vod_package

import datetime
import os
import random

from vod_metadata import default_template_path
from vod_metadata.vodpackage import VodPackage
from _overlapped import NULL

__all__ = ["generate_metadata"]

IMAGE_EXTENSIONS = [".bmp", ".jpg"]


def _check_for_ae(ae_type, movie_name, extensions):
    ae_safe = ae_type.replace(' ', '_')
    ae_paths = ['{}_{}{}'.format(movie_name, ae_safe, x) for x in extensions]
    for ae_path in ae_paths:
        if os.path.exists(ae_path):
            return ae_path

    return None


def _set_ae(vod_package, movie_name, ae_type, extensions):
    ae_safe = ae_type.replace(' ', '_')
    has_ae = getattr(vod_package, 'has_{}'.format(ae_safe))
    ae_path = _check_for_ae(ae_type, movie_name, extensions)
    if has_ae:
        if ae_path is None:
            getattr(vod_package, 'remove_{}'.format(ae_safe))()
            has_ae = False
        else:
            vod_package.D_content[ae_type] = ae_path

    return has_ae


def generate_metadata(
    file_path, vod_config, template_path=default_template_path
):
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
    short_name = file_name[:20]
    outfile_path = "{}_{}.xml".format(file_name, suffix)
    vod_package.xml_path = os.path.join(os.getcwd(), outfile_path)

    # File-specific values: looks for a preview of the same type as the movie,
    # and a poster / box cover with a suitable extension.
    movie_name, movie_ext = os.path.splitext(file_path)
    vod_package.D_content["movie"] = file_path

    has_preview = _set_ae(vod_package, movie_name, "preview", [movie_ext])
    has_poster = _set_ae(vod_package, movie_name, "poster", IMAGE_EXTENSIONS)
    has_box_cover = _set_ae(
        vod_package, movie_name, "box cover", IMAGE_EXTENSIONS
    )

    vod_package.check_files()

    # Package section
    package_asset_name = "{} {} (package)".format(short_name, suffix)
    package_description = "{} {} (package asset)".format(short_name, suffix)
    package_asset_id = "{}P{}{}".format(vod_config.prefix, asset_id, suffix)

    vod_package.D_ams["package"].update(
        {
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
    )
    vod_package.D_app["package"].update(
        {"Metadata_Spec_Version": "CableLabsVOD1.1"}
    )

    # Title section
    title_asset_name = "{} {} (title)".format(short_name, suffix)
    title_description = "{} {} (title asset)".format(short_name, suffix)
    title_asset_id = "{}T{}{}".format(vod_config.prefix, asset_id, suffix)
    title_title_brief = "{} {}".format(file_name[:14], suffix)
    title_title = "{} {}".format(file_name[:124], suffix)

    vod_package.D_ams["title"].update(
        {
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
    )
    vod_package.D_app["title"].update(
        {
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
    )

    # Movie section
    movie_asset_name = "{} {} (movie)".format(short_name, suffix)
    movie_description = "{} {} (movie asset)".format(short_name, suffix)
    movie_asset_id = "{}M{}{}".format(vod_config.prefix, asset_id, suffix)

    vod_package.D_ams["movie"].update(
        {
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
    )
    vod_package.D_app["movie"].update(
                                      {
                                       "Type": "movie",
                                       "Languages": "enES, enEN, enMX"
                                       }
                                      )

    # Preview section
    if has_preview:
        preview_asset_name = "{} {} (preview)".format(short_name, suffix)
        preview_description = "{} {} (preview asset)".format(
            short_name, suffix
        )
        preview_asset_id = "{}R{}{}".format(
            vod_config.prefix, asset_id, suffix
        )
        vod_package.D_ams["preview"].update(
            {
                "Provider":  vod_config.provider,
                "Product": vod_config.product,
                "Asset_Name": preview_asset_name,
                "Version_Major": '1',
                "Version_Minor": '0',
                "Description": preview_description,
                "Creation_Date": creation_date,
                "Provider_ID": vod_config.provider_id,
                "Asset_ID": preview_asset_id,
                "Asset_Class": "preview"
            }
        )
        vod_package.D_app["preview"].update(
            {"Type": "preview", "Rating": ["NR"]}
        )

    if has_poster:
        poster_asset_name = "{} {} (poster)".format(short_name, suffix)
        poster_description = "{} {} (poster asset)".format(short_name, suffix)
        poster_asset_id = "{}I{}{}".format(vod_config.prefix, asset_id, suffix)
        vod_package.D_ams["poster"].update(
            {
                "Provider":  vod_config.provider,
                "Product": vod_config.product,
                "Asset_Name": poster_asset_name,
                "Version_Major": '1',
                "Version_Minor": '0',
                "Description": poster_description,
                "Creation_Date": creation_date,
                "Provider_ID": vod_config.provider_id,
                "Asset_ID": poster_asset_id,
                "Asset_Class": "poster"
            }
        )
        vod_package.D_app["poster"].update({"Type": "poster"})

    if has_box_cover:
        box_cover_asset_name = "{} {} (box cover)".format(short_name, suffix)
        box_cover_description = "{} {} (box cover asset)".format(
            short_name, suffix
        )
        box_cover_asset_id = "{}B{}{}".format(
            vod_config.prefix, asset_id, suffix
        )
        vod_package.D_ams["box cover"].update(
            {
                "Provider":  vod_config.provider,
                "Product": vod_config.product,
                "Asset_Name": box_cover_asset_name,
                "Version_Major": '1',
                "Version_Minor": '0',
                "Description": box_cover_description,
                "Creation_Date": creation_date,
                "Provider_ID": vod_config.provider_id,
                "Asset_ID": box_cover_asset_id,
                "Asset_Class": "box cover"
            }
        )
        vod_package.D_app["box cover"].update({"Type": "box cover"})

    return vod_package

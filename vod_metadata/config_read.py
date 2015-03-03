import configparser

__all__ = ["ConfigurationError", "parse_config"]


class ConfigurationError(Exception):
    pass


def parse_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    # extensions determines what files will be processed
    extensions = config.get(
        "Extensions", "extensions", fallback="mpg, ts, mp4"
    )
    extensions = set(".{}".format(x.strip()) for x in extensions.split(','))

    # Product can be up to 20 characters
    product = config.get("VOD", "product", fallback="MOD").strip()
    if len(product) > 20:
        raise ConfigurationError(
            "Configuration file error: product must be 20 characters or fewer"
        )

    # Provider_ID must be a lower-case domain name up to 20 characters
    provider_id = config.get("VOD", "provider_id", fallback="example.com")
    provider_id = provider_id.lower().strip()

    domain = provider_id.split(".")
    if (len(domain) != 2) or (len(domain[1]) == 1):
        raise ConfigurationError(
            "Configuration file error: provider_id must be a domain name."
        )
    if len(provider_id) > 20:
        raise ConfigurationError(
            "Configuration file error: provider_id must be less than 20 "
            "characters."
        )

    # Prefix must be 3 alphabetic characters
    prefix = config.get("VOD", "prefix", fallback="MSO").upper().strip()
    if (len(prefix) != 3) or (not prefix.isalpha()):
        raise ConfigurationError(
            "Configuration file error: prefix must be 3 alphabetic characters"
        )

    # Category must be a /-delimeted hierarchy of folder names, each folder
    # name 20 characters or fewer
    title_category = (
        config.get("VOD", "title_category", fallback="Testing/Videos").strip()
    )
    if any((len(folder) > 20 for folder in title_category.split("/"))):
        raise ConfigurationError(
            "Configuration file error: category title_category be a "
            "/-delimeted hierarchy of folder names, each folder name 20 "
            "characters or fewer"
        )

    # Provider can be up to 20 characters
    provider = config.get("VOD", "provider", fallback="001").strip()
    if len(provider) > 20:
        raise ConfigurationError(
            "Configuration file error: provider must be 20  characters or "
            "fewer"
        )

    # The ecn_2009 flag can be either "True" or "False"
    ecn_2009 = config.get("VOD", "ecn_2009", fallback="False")
    ecn_2009 = ecn_2009 == "True"

    return (
        extensions,
        product,
        provider_id,
        prefix,
        title_category,
        provider,
        ecn_2009
    )

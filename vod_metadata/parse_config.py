# VOD metadata file generator - parse_config sub-module
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
import configparser

class ConfigurationError(Exception):
  pass

def parse_config(config_path):
  config = configparser.ConfigParser()
  _ = config.read(config_path)
  
  # extensions determines what files will be processed
  extensions = config["Extensions"].get("extensions", "mpg, ts, mp4")
  extensions = set(".{}".format(x.strip()) for x in extensions.split(','))
  
  # Product can be up to 20 characters
  product = config["VOD"].get("product", "MOD").strip()
  if len(product) > 20:
    raise ConfigurationError("""Configuration file error: product must be 20 \
characters or fewer""")
  
  # Provider_ID must be a lower-case domain name up to 20 characters
  provider_id = config["VOD"].get("provider_id", "example.com").lower().strip()
  domain = provider_id.split(".")
  if (len(provider_id) > 20
      or len(domain) != 2
      or len(domain[0]) == 0
      or len(domain[1]) == 1):
    raise ConfigurationError("""Configuration file error: provider_id must be \
must be a lower-case domain name up to 20 characters""")

  # Prefix must be 3 alphabetic characters
  prefix = config["VOD"].get("prefix", "MSO").upper().strip()
  if not prefix.isalpha():
    raise ConfigurationError("""Configuration file error: prefix must be 3 \
alphabetic characters""")
  
  # Category must be a /-delimeted hierarchy of folder names, each folder name
  # 20 characters or fewer 
  default_category = "Testing/Videos"
  title_category = config["VOD"].get("title_category", "Testing/Videos").strip()
  if any((len(folder) > 20 for folder in title_category.split("/"))):
    raise ConfigurationError("""Configuration file error: category \
title_category be a /-delimeted hierarchy of folder names, each folder name 20 \
characters or fewer""")
  
  # Provider can be up to 20 characters
  provider = config["VOD"].get("provider", "001").strip()
  if len(provider) > 20:
    raise ConfigurationError("""Configuration file error: provider must be 20 \
characters or fewer""")
  
  # The ecn_2009 flag can be either "True" or "False"
  ecn_2009 = config["VOD"].get("ecn_2009", "False")
  ecn_2009 = True if (ecn_2009 == "True") else False
  
  return (extensions,
          product,
          provider_id,
          prefix,
          title_category,
          provider,
          ecn_2009)
import os, re, ConfigParser
from chiara.settings.common import COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE, COLLECTION_TRAITS_FILE
from collection import webfolder
from exception.exceptions import MissingDescriptionFileException
from utils import enum


def create_traits(user, rel_path, cid):
    """Creates the trait file for storing collection informations."""
    traits_parser = ConfigParser.RawConfigParser()
    traits_path = os.path.join(webfolder.get_abs_path(user, rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE)
    f = open(traits_path,'w')
    traits_parser.add_section("Common")
    traits_parser.set("Common", "id", cid)
    traits_parser.write(f)
    f.close()

def parse_description(user, rel_path):
    """Parse the description file of the collection.
    Returns the Description parser if the file was parsed correctly, 
    otherwise raise an ."""
    info_dir_path = os.path.join(webfolder.get_abs_path(user, rel_path), COLLECTION_INFO_DIR)
    if os.path.exists(os.path.join(info_dir_path, COLLECTION_DESCRIPTION_FILE)):
        description_file = open(os.path.join(info_dir_path, COLLECTION_DESCRIPTION_FILE), 'r')
        desc_parser = DescriptionParser()
        desc_parser.read(description_file)
        desc_parser.parse()
        return desc_parser
    else:
        raise MissingDescriptionFileException()


class DescriptionParser():
    """Class for parsing the description file of a collection."""
    
    desc_file = None
    abstract = None
    details = None
    tags = None
    
    
    def read(self, desc_file):
        """Save the given file to global attribute."""
        self.desc_file = desc_file
    
    def parse(self):
        """Parse the stored file and save the content into
        summary, details and tags attributes."""
        # if file was read
        if self.desc_file:
            self.abstract = []
            self.details = []
            self.tags = []
            stage=0
            for line in self.desc_file:
                if stage==0:
                    if re.search("### abstract ###", line.lower()):
                        stage = 1
                    else:
                        continue
                # save summary
                elif stage==1:
                    if re.search("### details ###", line.lower()):
                        stage = 2
                    else:
                        self.abstract.append(line)
                # save details
                elif stage==2:
                    if re.search("### tags ###", line.lower()):
                        stage = 3;
                    else:
                        self.details.append(line)
                # save tags
                elif stage==3:
                    line = line.split('#')[0]
                    parts = line.split(':')
                    # check if line is in format "key: values"
                    if 1<len(parts):
                        key = parts[0].strip()
                        if len(key) > 0:
                            # convert to singular
                            if key[-1] == "s":
                                key = key[:-1]
                            # check if key choice exist
                            if key in [k for (k,_) in enum.Tag.CHOICES_A]:
                                values = ':'.join(parts[1:]).strip()
                                # save all values under the key
                                for value in values.split(';'):
                                    self.tags.append((key, value.strip()))
        # if file was not read            
        else:
            raise MissingDescriptionFileException()
    
    
    def get_abstract(self):
        return ''.join(self.abstract)
    
    def get_details(self):
        return ''.join(self.details)
    
    def get_tags(self):
        return self.tags



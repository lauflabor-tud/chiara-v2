import os, re, ConfigParser
from chiara.settings.common import COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE, COLLECTION_TRAITS_FILE
import webfolder.functions as wf_func
from exception.exceptions import MissingDescriptionFileException


def create_traits(user, rel_path, cid):
    """Creates the trait file for storing collection informations."""
    traits_parser = ConfigParser.RawConfigParser()
    traits_path = os.path.join(wf_func.get_abs_path(user, rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE)
    f = open(traits_path,'w')
    traits_parser.add_section("Common")
    traits_parser.set("Common", "id", cid)
    traits_parser.write(f)
    f.close()

def parse_description(user, rel_path):
    """Parse the description file of the collection.
    Returns the Description parser if the file was parsed correctly, 
    otherwise raise an ."""
    info_dir_path = os.path.join(wf_func.get_abs_path(user, rel_path), COLLECTION_INFO_DIR)
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
    summary = None
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
            self.summary = []
            self.details = []
            self.tags = []
            stage=0
            for line in self.desc_file:
                if stage==0:
                    if re.search("### summary ###", line.lower()):
                        stage = 1
                    else:
                        continue
                # save summary
                elif stage==1:
                    if re.search("### details ###", line.lower()):
                        stage = 2
                    else:
                        self.summary.append(line)
                # save details
                elif stage==2:
                    if re.search("### tags ###", line.lower()):
                        stage = 3;
                    else:
                        self.details.append(line)
                # save tags
                elif stage==3:
                    parts = line.split(':')
                    # check if line is in format "key: values"
                    if 1<len(parts):
                        key = parts[0].strip()
                        if len(key) > 0:
                            values = ':'.join(parts[1:]).strip()
                            for value in values.split(','):
                                self.tags.append((key, value.strip()))
        # if file was not read            
        else:
            raise MissingDescriptionFileException()
    
    def get_summary(self):
        return ''.join(self.summary)
    
    def get_details(self):
        return ''.join(self.details)
    
    def get_tags(self):
        return self.tags



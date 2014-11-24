

class MissingDescriptionFileException(Exception):
    pass

class NoLocalChangesException(Exception):
    pass

class NotNewestRevisionException(Exception):
    pass

class CollectionIsUpdatedException(Exception):
    pass

class CannotParseStringToDateException(Exception):
    def __init__(self, date):
        self.date = date
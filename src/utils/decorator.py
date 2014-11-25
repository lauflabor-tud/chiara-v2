from exception.exceptions import CollectionIsUpdatedException


def updateCollectionFlag(func):
    """Set flag for a collection when it is updated."""
    
    def _decorator(self, *args, **kwargs):
        # collection is updated at the moment
        if args[2].is_updated():
            raise CollectionIsUpdatedException()
        # collection is not updated
        else:
            # set update flag
            args[2].add_update_flag()
            # execute update function
            try:
                func(self, *args, **kwargs)
            except Exception as ex:
                raise ex
            # remove update flag
            finally:
                args[2].remove_update_flag()
                
    return _decorator
        

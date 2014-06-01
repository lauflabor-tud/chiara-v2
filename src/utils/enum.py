class Permission:
	READ = 'R'
	WRITE = 'W'
	
	CHOICES = (
		(READ, 'read'),
		(WRITE, 'write')
	)
	
class Tag:
	TITLE = "title"
	ABSTRACT = "abstract"
	AUTHOR = "author"
	CREATION_DATE = "creation_date"
	CREATION_DATE_MIN = "creation_date_min"
	CREATION_DATE_MAX = "creation_date_max"
	PUBLISHING_DATE_MIN = "publishing_date_min"
	PUBLISHING_DATE_MAX = "publishing_date_max"
	LAST_MODIFICATION_DATE_MIN = "last_modification_date_min"
	LAST_MODIFICATION_DATE_MAX = "last_modification_date_max"
	TOPIC = "topic"
	PROJECT = "project"
	KEYWORD = "keyword"
	
	CHOICES_A = (
		(AUTHOR, "author"),
		(CREATION_DATE, "creation date"),
		(TOPIC, "topic"),
		(PROJECT, "project"),
		(KEYWORD, "keyword")			
	)
	
	CHOICES_B = (
		(TITLE, "title"),
		(ABSTRACT, "abstract"),
		(AUTHOR, "author"),
		(TOPIC, "topic"),
		(PROJECT, "project"),
		(CREATION_DATE_MIN, u"creation date \u2265 "),
		(CREATION_DATE_MAX, u"creation date \u2264 "),
		(PUBLISHING_DATE_MIN, u"publishing date \u2265 "),
		(PUBLISHING_DATE_MAX, u"publishing date \u2264 "),
		(LAST_MODIFICATION_DATE_MIN, u"last modification date \u2265 "),
		(LAST_MODIFICATION_DATE_MAX, u"last modification date \u2264 "),
		(KEYWORD, "keyword")		
	)
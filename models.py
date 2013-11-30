from trovetheses import db


class Thesis(db.Document):
	work_id = db.IntField()
	version_id = db.IntField()
	record = db.DictField()
	format_type = db.ListField()
	issued = db.ListField()
	holdings_count = db.IntField()
	holdings = db.ListField()
	duplicates = db.ListField()

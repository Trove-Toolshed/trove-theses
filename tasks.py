from harvester.harvester import TroveHarvester
from models import Thesis
import time
from operator import itemgetter

from credentials import TROVE_API_KEY


def remove_fullstops(dic):
	"""
	Remove fullstops from keys before saving dictionary to Mongo.
	"""
	new_dic = {}
	try:
		for key, value in dic.items():
			new_dic[key.replace('.','_')] = remove_fullstops(value)
	except AttributeError:
		return dic
	else:
		return new_dic


class ThesisHarvester(TroveHarvester):

	def process_results(self, results):
		total = results[0]['records']['total']
		print '{} results'.format(total)
		for work in results[0]['records']['work']:
			for version in work['version']:
				# Separate out multiple records in versions
				if ('record' in version) and (('type' in version and 'Thesis' in version['type']) or 'type' not in version): #ignore strange UniSA records
					if 'issued' in version:
						if isinstance(version['issued'], list):
							issued = version['issued']
						else:
							issued = [version['issued']]
					else:
						issued = []
					if isinstance(version['record'], list):
						version_ids = version['id'].split()
						print version_ids
						for index, record in enumerate(version['record']):
							record = remove_fullstops(record)
							duplicates = [vid for vid in version_ids if vid != version_ids[index]]
							thesis, created = Thesis.objects.get_or_create(
								version_id=version_ids[index],
								defaults={
									'work_id': work['id'],
									'record': record,
									'issued': issued,
									'holdings_count': version['holdingsCount'],
									'duplicates': duplicates
								})
							if 'type' in version:
								thesis.format_type = version['type']
							if 'holding' in version:
								thesis.holdings = version['holding']
							thesis.save()
							print 'Version {} saved'.format(thesis.version_id)
					else:
						record = self.remove_fullstops(version['record'])
						thesis, created = Thesis.objects.get_or_create(
								version_id=version['id'],
								defaults={
									'work_id': work['id'],
									'record': record,
									'issued': issued,
									'holdings_count': version['holdingsCount']
								})
						if 'type' in version:
							thesis.format_type = version['type']
						if ('holding' in version):
							thesis.holdings = version['holding']
						thesis.save()
						print 'Version {} saved'.format(thesis.version_id)
			self.harvested += 1
			print 'Processed {} of {} works'.format(self.harvested, total)
		time.sleep(1)


def do_harvest(start=0, number=20):
	query = 'http://api.trove.nla.gov.au/result?q=%20&zone=book&l-format=Thesis&n=20&encoding=json&include=workversions&include=holdings&l-australian=y'
	key = TROVE_API_KEY
	harvester = ThesisHarvester(query=query, key=key, start=start, number=number)
	harvester.harvest()


def collate_fields():
	fields = {}
	for thesis in Thesis.objects(record__metadata__exists=True):
		#print thesis.record['metadata']
		for key, value in thesis.record['metadata'].items():
			if key != 'value':
				#print value
				try:
					for field in value.keys():
						print field
						try:
							fields[field] += 1
						except KeyError:
							fields[field] = 1
				except AttributeError:
					if isinstance(value, list):
						for record in value:
							for field in record.keys():
								print field
								try:
									fields[field] += 1
								except KeyError:
									fields[field] = 1

	fields = sorted(fields.items(), key=itemgetter(1), reverse=True)
	print fields
	for f in fields:
		print '{}: {}'.format(f[0], f[1])
	


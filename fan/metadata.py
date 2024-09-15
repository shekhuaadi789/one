METADATA =\
{
	'name': 'fan',
	'description': 'Next generation face swapper and enhancer',
	'version': '2.1.2',
	'license': 'MIT',
	'author': 'Henry Ruhs',
	'url': 'https://fan.io'
}


def get(key : str) -> str:
	return METADATA[key]

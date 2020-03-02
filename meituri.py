import sys
import os
import urllib.request
import time
import click


URL = 'http://ii.hywly.com/a/1/{}/{}.jpg'


# Adds -h in addition to the default --help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-a', '--album', type=int,
	prompt='Enter the album id',
	help='Album ID located in the URL: https://www.meituri.com/a/$ID')
@click.option('-n', '--number', type=int,
	prompt='Enter the number of images',
	help='Number of pictures on top of the page followed by P.')
# couldn't figure out to also optionally add arguments below
# @click.argument('album', type=int, required=False)
# @click.argument('number', type=int, required=False)
def start(album, number):
	out = []
	path = f'albums/hywly-{album}/'
	try:
		if not os.path.exists(path):
			os.makedirs(path)
	except NotADirectoryError as e:
		print(f'NotADirectoryError: {e}')
		return
	except OSError as e:
		print(f'OSError: {e}')
		return

	for x in range(1, number+1):
		out.append(URL.format(album, x))
	
	download_images(out, path)
	
def get_opener():
	opener = urllib.request.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')]
	urllib.request.install_opener(opener)

def download_images(links, path):
	total_time = 0
	total_pauses = 0
	get_opener()
	for n, link in enumerate(links):
		name = link.split('/')[-1]
		print('Downloading %s.' % link)
		start = time.time()
		urllib.request.urlretrieve(link, path + name)
		end = time.time()
		passed = end - start
		total_time += passed
		print('Complete. Took %.2f seconds.' % passed)
		
		if (n + 1) == len(links):
			pass
		elif passed < 5:
			add = 5 - passed
			print('Waiting for an additional %.2f seconds.' % add)
			time.sleep(add)
			total_pauses += add

	print('---\nDownloading %d images took %.2f seconds to complete.\nPlus %.2f additional seconds of wait time.' % (len(links), total_time, total_pauses))


if __name__ == '__main__':
	start()

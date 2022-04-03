import sys
import os
import urllib.request
import time
import argparse
import urllib.request as ul
from urllib.error import HTTPError

COMPLETE_TIME = 5
URL = 'http://lns.hywly.com/a/1/{}/{}.jpg'


def start():
        parser = argparse.ArgumentParser(description='Album downloader for meituri.com.')
        group_req = parser.add_argument_group('required arguments')
        group_req.add_argument('-a', '--album', metavar='ID',
                help='album ID located in the URL: https://www.meituri.com/a/$ID',
                type=int)
        group_req.add_argument('-n', '--number', metavar='pics',
                help='number of pictures on top of the page followed by P',
                type=int)

        # Add support for buondua.com
        group_req.add_argument('-l', '--link', metavar='link',
                help='link of buondua.com albums to download (-a and -n parameters are not required.)',
                type=str)

        args = parser.parse_args()
        out = []

        # Manual arg verification bc argparse aren't able to
        # put conditional relations between argument groups.
        if args.link is None and (args.album is None or args.number is None):
                print("[x] Argument requirements are not satisfied.")
                return

        album_name = ""  # Use additional album_name constructed by the link
                         # instead of `args.album`

        if args.link is not None and "buondua.com" in args.link:   # branch for buondua.com
                magic_string = "photo 1-0"                         # used for finding the first picture link

                # Connect and get the web page
                client = ul.urlopen(ul.Request(args.link, headers={'User-Agent': 'Mozilla/5.0'}))
                htmllines = client.read().decode().split('\n')
                client.close()

                srcline = ""
                for each_line in htmllines:                # search for the first picture link
                        if magic_string in each_line:
                                srcline = each_line
                                break

                srcline_split = srcline.split(" ")         # split for better manipulation
                datasrc = "".join([x if "data-src=" in x else "" for x in srcline_split])    # delete other parts except the part containing the pic download link

                # Construct link template
                link_template = datasrc.replace("data-src=","").replace("\"", "").split("?")[0].replace("001.jpg","%03d.jpg").replace("001.jpeg","%03d.jpeg")

                # Get the album size from link
                album_size = int( srcline_split[srcline_split.index("photos)") - 1].replace("(","") )
                print(link_template)
                for x in range(1, album_size+1):
                        out.append(link_template % x)
                album_name = link_template.split("/")[-1]
                album_name = album_name[: album_name.find("MrCong.com")-1]
        else:
                for x in range(1, args.number+1):
                        out.append(URL.format(args.album, x))
                album_name = args.album


        path = f'albums/{album_name}/'
        try:
                if not os.path.exists(path):
                        os.makedirs(path)
        except OSError as e:
                print(f'OSError: {e}')
                return

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
                try:
                        name = link.split('/')[-1].split('-')[-1]
                        print('Downloading %s.' % link)
                        start = time.time()
                        urllib.request.urlretrieve(link, path + name)
                        end = time.time()
                        passed = end - start
                        total_time += passed
                        print('Complete. Took %.2f seconds.' % passed)

                        if (n + 1) == len(links):
                                pass
                        elif passed < COMPLETE_TIME:
                                add = COMPLETE_TIME - passed
                                print('Waiting for an additional %.2f seconds.' % add)
                                time.sleep(add)
                                total_pauses += add

                except HTTPError as e:
                        print(f'\033[91mError: {e}\033[0m')
                finally:
                        continue


        print('---\nDownloading %d images took %.2f seconds to complete.\nPlus %.2f additional seconds of wait time.' % (len(links), total_time, total_pauses))


if __name__ == '__main__':
        start()

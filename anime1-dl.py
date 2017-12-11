from __future__ import print_function, division

try:
	from urllib2 import urlopen, Request, HTTPError
except ImportError:
	from urllib.request import urlopen, Request
	from urllib.error import HTTPError

import sys
import re
import os.path
import datetime

if os.name == "nt":
    path_delim = "\\"
elif os.name == "posix":
    path_delim = "/"

def main():
	print("anime1-dl made by Dragneel1234", end="\n\n")
	if len(sys.argv) == 1:
		print("usage: anime1-dl url")
		return

	print("[anime1-dl] Checking URL...")
	if "anime1.com" not in sys.argv[1]:
		print("[anime1-dl] Not a correct anime1 link")
		return

	if "/watch/" in sys.argv[1]:
		if "episode-" not in sys.argv[1]:
			print("[anime1.dl] A possible series link detected")
			download_series(sys.argv[1])
		else:
			print("[anime1.dl] A possible episode link detected")
			download_episode(sys.argv[1], "")

def download_series(url):
	__VALID_URL__ = r"http://www.anime1.com/watch/*/"
	if re.match(__VALID_URL__, url) is None:
		print("[anime1-dl] Not a correct URL")
		return

	print("\n[anime1-dl] Downloading webpage")
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	page = urlopen(req).read()

	print("[anime1-dl] Getting series name and number of episode(s)")
	YouAreHereIndex = page.find(b"You Are Here")
	if YouAreHereIndex == -1:
		print("\n[anime1-dl] Seriously... Wrong Link")
		return

	TruncatedForName = page[YouAreHereIndex : ]
	NameIndex = TruncatedForName.find(b"</a></div>")
	Name = TruncatedForName[83 : NameIndex].decode()

	LatestEpIndex = page.find("Latest {} Episodes".format(Name).encode())
	if LatestEpIndex != -1:
		TruncatedForEpisode = page[LatestEpIndex + len("Latest {} Episodes".format(Name)) : ]
		EpIndex = TruncatedForEpisode.find("{} Episodes".format(Name).encode())
		TruncatedForEpisode = TruncatedForEpisode[EpIndex : ]
		EndOfEpisodes = TruncatedForEpisode.find(b"</ul>")
		TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]
	else:
		TruncatedForEpisode = page[YouAreHereIndex : ]
		EndOfEpisodes = TruncatedForEpisode.find(bytes("</ul>", "utf-8"))
		TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]

	URLs = re.findall(b"http://www.anime1.com/watch/[a-zA-Z0-9-]+/[a-z-]+-[0-9-]{1,8}", TruncatedForEpisode)

	print("\n[anime1-dl] Name: {}".format(Name))
	print("[anime1-dl] Episodes Found: {}".format(len(URLs)))

	for url in URLs:
		download_episode(url.decode(), Name)

def get_info(URL):
	print("[anime1-dl] Download webpage")
	req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
	
	try:
		web = urlopen(req)
	except HTTPError:
		print("[anime1-dl] Webpage not found, Error code: {}".HTTPError.code)
		return "", ""
	page = web.read()

	print("[anime1-dl] Finding Video")
	v_URL = page.find(b'file: "') + 7
	f_URL = page.find(b'label: "') + 8
	if v_URL is -1 or f_URL is -1:
		return "", ""
	TruncatedForName = page[f_URL: ]
	TruncatedForName = TruncatedForName[: TruncatedForName.find(b'"')]
	TruncatedForVideo = page[v_URL: ]
	TruncatedForVideo = TruncatedForVideo[ : TruncatedForVideo.find(b'"')]
	TruncatedForVideo = TruncatedForVideo.replace(b" ", b"%20")
	return TruncatedForVideo.decode(), TruncatedForName.decode().replace(":", "").replace("Episode Episode", "Episode")

def download_episode(URL, Name):
    print("\n[anime1-dl] Download episode from {}...{}".format(URL[ : URL.find(".com/") + 5], URL[URL.find("/episode-") : ]))
    print("[anime1-dl] Getting Info on the Episode")
    __FINAL__URL__, __FINAL__NAME__ = get_info(URL)
    if __FINAL__URL__ is "" or __FINAL__NAME__ is "":
        print("[anime1-dl] Video not Found")
        return
        
    if Name != "" and not os.path.exists(Name):
        os.makedirs(Name)
    
    Video = urlopen(__FINAL__URL__)
    File_Size = Video.info()["Content-Length"]
    File_Type = Video.info()["Content-Type"]
    __FINAL__NAME__ = Name + path_delim + __FINAL__NAME__ + "." + File_Type[File_Type.find("/") + 1 : ]
   
    if os.path.isfile(__FINAL__NAME__) and os.path.getsize(__FINAL__NAME__) == int(File_Size):
        print("[anime1-dl] File found and is of same size, skipping")
        return

    File_Size_Text = BytesToPrefix(int(File_Size))
    f_Video = open(__FINAL__NAME__, "wb")
    print("\n[anime1-dl] Destination: {}\n[anime1-dl] Type: {}".format(__FINAL__NAME__[__FINAL__NAME__.find(path_delim) + 1 : ], File_Type))
    
    Downloaded = 0
    BlockSize = 8192

    while True:
        Buffer = Video.read(BlockSize)
        if not Buffer:
            break

        Downloaded += len(Buffer)
        f_Video.write(Buffer)

        Status_Text = "[anime1-dl] {:9s}/{:9s} [{:7.3f}%]".format(
            BytesToPrefix(int(Downloaded)), File_Size_Text, int(Downloaded) * 100 / int(File_Size))
        print("{}  ".format(Status_Text), end="\r")

    f_Video.close()
    print()

def BytesToPrefix(Size):
	Prefix_N = 0
	Prefixes = ["B", "KiB", "MiB", "GiB", "TiB"]
	t_Size = Size
	l_Size = Size

	while t_Size > 0:
		t_Size = t_Size // 1024
		if t_Size:
			Prefix_N += 1

	l_Size = Size / (1024 ** Prefix_N)

	return "{:6.2f} {}".format(l_Size, Prefixes[Prefix_N])


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\n\nKeyboard Interupt detected, exiting")
		sys.exit(-1)

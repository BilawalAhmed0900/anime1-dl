import sys
import re
import urllib.request
import os.path
import datetime

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
			download_episode(sys.argv[1])
		
def download_series(url):
	__VALID_URL__ = r"http://www.anime1.com/watch/*/"
	if re.match(__VALID_URL__, url) is None:
		print("[anime1-dl] Not a correct URL")
		return
		
	print("\n[anime1-dl] Downloading webpage")
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	page = urllib.request.urlopen(req).read()
	
	print("[anime1-dl] Getting series name and number of episode(s)")
	YouAreHereIndex = page.find(bytes("You Are Here", "utf-8"))
	if YouAreHereIndex == -1:
		print("\n[anime1-dl] Seriously... Wrong Link")
		return
	
	TruncatedForName = page[YouAreHereIndex : ]
	NameIndex = TruncatedForName.find(bytes("</a></div>", "utf-8"))
	Name = TruncatedForName[83 : NameIndex].decode()
	
	LatestEpIndex = page.find(bytes("Latest {} Episodes".format(Name), "utf-8"))
	if LatestEpIndex != -1:
		TruncatedForEpisode = page[LatestEpIndex + len("Latest {} Episodes".format(Name)) : ]
		EpIndex = TruncatedForEpisode.find(bytes("{} Episodes".format(Name), "utf-8"))
		TruncatedForEpisode = TruncatedForEpisode[EpIndex : ]
		EndOfEpisodes = TruncatedForEpisode.find(bytes("</ul>", "utf-8"))
		TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]
	else:
		TruncatedForEpisode = page[YouAreHereIndex : ]
		EndOfEpisodes = TruncatedForEpisode.find(bytes("</ul>", "utf-8"))
		TruncatedForEpisode = TruncatedForEpisode[ : EndOfEpisodes]
	
	URLs = re.findall(bytes("http://www.anime1.com/watch/[a-zA-Z0-9-]+/episode-[0-9]{1,4}", "utf-8"), TruncatedForEpisode)
	
	print("\n[anime1-dl] Name: {}".format(Name))
	print("[anime1-dl] Episodes Found: {}".format(len(URLs)))
	
	for url in URLs:
		download_episode(url.decode())
		
def get_info(URL):
	print("[anime1-dl] Download webpage")
	req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
	page = urllib.request.urlopen(req).read()
	
	print("[anime1-dl] Finding Video")
	v_URL = page.find(bytes('file: "', "utf-8")) + 7
	f_URL = page.find(bytes('label: "', "utf-8")) + 8
	if v_URL is -1 or f_URL is -1:
		return "", ""
	TruncatedForName = page[f_URL: ]
	TruncatedForName = TruncatedForName[: TruncatedForName.find(bytes('"', "utf-8"))]
	TruncatedForVideo = page[v_URL: ]
	TruncatedForVideo = TruncatedForVideo[ : TruncatedForVideo.find(bytes('"', "utf-8"))]
	TruncatedForVideo = TruncatedForVideo.replace(bytes(" ", "utf-8"), bytes("%20", "utf-8"))
	return TruncatedForVideo.decode(), TruncatedForName.decode().replace(":", "").replace("Episode Episode", "Episode")
		
def download_episode(URL):
	print("\n[anime1-dl] Download episode from {}...{}".format(URL[ : URL.find(".com/") + 5], URL[URL.find("/episode-") : ]))
	print("[anime1-dl] Getting Info on the Episode")
	__FINAL__URL__, __FINAL__NAME__ = get_info(URL)
	if __FINAL__URL__ is "" or __FINAL__NAME__ is "":
		print("[anime1-dl] Video not Found")
		return
	
	Video = urllib.request.urlopen(__FINAL__URL__)
	File_Size = Video.info()["Content-Length"]
	File_Type = Video.info()["Content-Type"]
	
	if os.path.isfile(__FINAL__NAME__) and os.path.getsize(__FINAL__NAME__) == int(File_Size):
		print("[anime1-dl] File found and is of same size, skipping")
		return
		
	File_Size_Text = BytesToPrefix(int(File_Size))
		
	f_Video = open(__FINAL__NAME__ + "." + File_Type[File_Type.find("/") + 1 : ], "wb")
	print("\n[anime1-dl] Destination: {}\n[anime1-dl] Type: {}".format(__FINAL__NAME__, File_Type))
	
	Downloaded = 0
	BlockSize = 8192
	Total_Time = 0
	Steps = 0
	
	while True:
		Before = datetime.datetime.now()
		Buffer = Video.read(BlockSize)
		After = datetime.datetime.now()
		if not Buffer:
			break
			
		Steps += 1
		Downloaded += len(Buffer)
		f_Video.write(Buffer)
		
		Total_Time += (After - Before).total_seconds()
		Avg_Time = Total_Time / Steps
		if Avg_Time == 0:
			Avg_Time = 1
		
		Status_Text = "[anime1-dl] {:9s}/{:9s} [{:7.3f}%] Speed = {:10s}/s".format(
			BytesToPrefix(int(Downloaded)), File_Size_Text, int(Downloaded) * 100 / int(File_Size), BytesToPrefix(len(Buffer) / Avg_Time))
		print("{}  ".format(Status_Text), end="\r")
		
	f_Video.close()
		
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

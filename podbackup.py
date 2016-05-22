import datetime
import os
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree import ElementTree as eTree

__author__ = 'Erik Andersson'


def download_all(url):
    try:
        rss = eTree.parse(urlopen(url))
    except ValueError:
        print("invalid url")
        return

    show = rss.getroot()
    name = show.find("channel").find("title").text
    if not os.path.exists(name):
        os.makedirs(name)

    parent_map = {c: p for p in show.iter() for c in p}
    date_ep_pairs = {}
    for episode in show.iter('enclosure'):
        try:
            date = datetime.datetime.strptime(
                parent_map[episode].find("pubDate").text,
                "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            date = datetime.datetime.strptime(
                parent_map[episode].find("pubDate").text,
                "%a, %d %b %Y %H:%M:%S %z")
        date_ep_pairs[date.strftime("%Y-%m-%d")] = episode.attrib["url"]
    for i, episode in enumerate(date_ep_pairs):
        print("Downloading", i + 1, "of", len(date_ep_pairs),
              "(" + str(i / len(date_ep_pairs) * 100) + "%)")
        download_episode(date_ep_pairs[episode], episode, name)
    return


def download_episode(url, name, dir):
    try:
        remote = urlopen(url)
    except HTTPError as e:
        print(e, "when downloading episode", name)
        return
    local = open(os.path.join(dir, name + ".mp3"), "wb")
    local.write(remote.read())
    local.close()
    remote.close()
    return


download_all(input("Enter the URL of a podcast feed:\n"))

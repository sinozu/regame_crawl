#!/usr/bin/env python

from requests_html import HTMLSession

from models.notion import Notion
from models.regame_info import RegameInfo


def main():
    session = HTMLSession()
    notion = Notion()
    get_regame(session, notion, "https://realdgame.jp/event/")


def get_regame(session, notion, url, archive=False):
    r = session.get(url)
    event_main_area = r.html.find('#event_main_area', first=True)
    for element in event_main_area.find('.thumbnail'):
        notion.add_page(RegameInfo(element, archive))


if __name__ == '__main__':
    main()

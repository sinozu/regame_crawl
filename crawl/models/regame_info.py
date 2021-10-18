#!/usr/bin/env python

class RegameInfo:
    def __init__(self, elem, finished: bool) -> None:
        self.title = elem.find('.thumbnail_h', first=True).text
        place = elem.find('.thumbnail_venue', first=True)
        if place is not None:
            self.place = elem.find('.thumbnail_venue', first=True).text
        else:
            self.place = ""

        self.image = elem.find('.thumbnail_wrap img', first=True).attrs['src']

        self.lp_url = elem.find('.thumbnail_wrap a', first=True).attrs['href']

        # if self.title in 'リバイバル' or self.title in '再演':
        #     self.revival = True
        # else:
        #     self.revival = False

        self.finished = finished

    def get_title(self):
        # t = self.title.replace('【リバイバル公演】', '')
        # return t.replace('【再演】', '')
        return self.title

    def get_place(self):
        return self.place

    def get_image(self):
        return self.image

    def get_lp_url(self):
        return self.lp_url

    def is_revival(self):
        # return self.revival
        return False

    def is_finished(self):
        return self.finished

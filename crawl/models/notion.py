#!/usr/bin/env python

import json
import os
import requests
import time

from models.regame_info import RegameInfo


class Notion:
    def __init__(self):
        self.api_token = os.environ.get('NOTION_API_KEY')
        self.database_id = os.environ.get('NOTION_DATABASE_ID')
        self.notion_version = os.environ.get('NOTION_VERSION')
        self.page_list = []

    def add_page(self, info: RegameInfo):
        page_id = self.__get_existing_page(info.get_title())
        print(info.get_title())
        if page_id is None:
            self.__create_page(info)
        elif not info.is_revival():
            self.__update_page(info, page_id)
        else:
            print("リバイバルなので更新スキップ")

    def __create_page(self, info: RegameInfo):
        try:
            r = requests.post(
                'https://api.notion.com/v1/pages',
                headers=self.__headers(),
                data=self.__page_properties(info)
            )
            r.raise_for_status()
            time.sleep(0.5)
            print("create!!")
        except requests.exceptions.RequestException as e:
            print(r.text)
            print("エラー : ", e)
            raise

    def __update_page(self, info: RegameInfo, page_id: str):
        try:
            r = requests.patch(
                f'https://api.notion.com/v1/pages/{page_id}',
                headers=self.__headers(),
                data=self.__page_properties(info)
            )
            r.raise_for_status()
            time.sleep(0.5)
            print("update!!")
        except requests.exceptions.RequestException as e:
            print(r.text)
            print("エラー : ", e)
            raise

    def __page_properties(self, info: RegameInfo) -> json:
        data = {
            'parent': {'database_id': self.database_id},
            'properties': {
                'Name': {'title': [{'text': {'content': info.get_title()}}]},
                'Place': {'rich_text': [{'type': 'text', 'text': {'content': info.get_place()}}]},
                'Image': {'files': [{'type': 'external', 'name': info.get_title(), 'external': {'url': info.get_image()}}]},
                'Finish': {'checkbox': info.is_finished()},
                'Link': {'url': info.get_lp_url()},
            }
        }
        return json.dumps(data)

    def __get_existing_page(self, title: str) -> str:
        page_list = self.__get_page_list()
        page_id = None
        for page in page_list:
            name = page.get('properties').get('Name').get('title')[0].get('plain_text')
            page_id = page.get('id') if title == name else None
            if page_id is not None:
                return page_id
        return page_id

    def __get_page_list(self):
        if len(self.page_list) == 0:
            self.__get_page_recursive()

        return self.page_list

    def __get_page_recursive(self, next_cursor=None):
        try:
            data = {}
            if next_cursor is not None:
                data = json.dumps({'start_cursor': next_cursor})
            r = requests.post(
                f'https://api.notion.com/v1/databases/{self.database_id}/query',
                headers=self.__headers(),
                data=data,
            )
            r.raise_for_status()
            r_json = r.json()

            self.page_list.extend(r_json.get('results'))
            print(f'page_list count: {len(self.page_list)}')

            if r_json.get('has_more') is True:
                time.sleep(0.5)
                self.__get_page_recursive(r_json.get('next_cursor'))
        except Exception as e:
            print(r.text)
            print("エラー : ", e)
            raise

    def __headers(self):
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Notion-Version': self.notion_version,
            'Content-Type': 'application/json',
        }

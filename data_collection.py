import csv
import requests
from datetime import datetime
import time

import config

BASIC_LINK = 'https://api.vk.com/method/'


USER_FIELDS = [
    "has_photo", "sex", "bdate", "city", "country", "has_mobile", "contacts", "followers_count", "relatives",
    "relation", "personal", "activities", "music", "movies", "tv", "books", "about", "quotes", "counters",
    "can_access_closed", "last_name", "id", "first_name", "deactivated"
]

PURE_FIELDS = [
    "has_photo", "sex", "has_mobile", "followers_count"
]

# "has_photo", "sex", "has_mobile", "followers_count", "is_closed"

PRESENTED_FIELDS = [
    "contacts", "relatives", "relation", "personal", "activities", "music", "movies", "tv", "books", "about", "quotes"
]

COUNTER_FIELDS = [
    "albums", "audios", "friends", "pages", "subscriptions", "videos"
]


def get_offset(group_id):
    count = requests.get('https://api.vk.com/method/groups.getMembers', params={
        'access_token': config.ACCESS_TOKEN,
        'v': 5.103,
        'group_id': group_id,
        'sort': 'id_desc',
        'offset': 0,
        'fields': 'last_seen'
    }).json()['response']['count']
    return count // 1000
    # return count


def get_group_users(group_id):
    good_id_list = []
    offset = 0
    max_offset = get_offset(group_id)
    while offset <= max_offset:
        response = requests.get('https://api.vk.com/method/groups.getMembers', params={
            'access_token': config.ACCESS_TOKEN,
            'v': 5.103,
            'group_id': group_id,
            'sort': 'id_desc',
            'offset': offset,
            'fields': 'last_seen'
        }).json()['response']
        offset += 1
        for item in response['items']:
            good_id_list.append(item['id'])
    return good_id_list


def get_user_info(user_id):
    method = 'users.get?user_ids={user_ids}&fields={fields}&access_token={access_token}&v={api_version}'
    payload = {
        'user_ids': [user_id],
        'fields': ','.join(USER_FIELDS),
        'v': '5.130',
        'access_token': config.ACCESS_TOKEN
    }
    time.sleep(0.5)
    response = requests.get(BASIC_LINK + method, params=payload).json()
    info = response['response'][0]
    return info


def calculate_age(bdate: str):
    bdate_list = bdate.split(".")
    if len(bdate_list) != 3:
        return None
    bday, bmonth, byear = bdate_list
    today = datetime.today()
    return today.year - int(byear) - ((today.month, today.day) < (int(bmonth), int(bday)))


def transform_user_info(user_info):
    transformed_user_info = {
        "uid": user_info['id']
    }
    # print("User_info: ", user_info)
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)

    for user_field in PRESENTED_FIELDS:
        transformed_user_info[user_field] = int(user_field in user_info)

    if "deactivated" not in user_info.keys():
        for user_field in COUNTER_FIELDS:
            transformed_user_info[user_field] = user_info["counters"][user_field]
        transformed_user_info["status"] = 'active'
    else:
        for user_field in COUNTER_FIELDS:
            transformed_user_info[user_field] = None
        transformed_user_info["status"] = user_info["deactivated"]

    transformed_user_info["age"] = calculate_age(user_info["bdate"]) if "bdate" in user_info else None

    transformed_user_info["city"] = user_info["city"]["id"] if "city" in user_info else None

    transformed_user_info["country"] = user_info["country"]["id"] if "country" in user_info else None

    return transformed_user_info


def write_user_info_to_csv(user_info, filename):
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=user_info[0].keys())
        writer.writeheader()
        for user in user_info:
            # print("User in printing: ", user)
            writer.writerow(user)


'''def main():
    users = []
    with open('VK_UIDS.csv') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        if header is not None:
            for row in csv_reader:
                users.append(row[0])
    user_info = [transform_user_info(get_user_info(x)) for x in users]
    print("All user info: ", user_info)
     


if __name__ == '__main__':
    main()'''

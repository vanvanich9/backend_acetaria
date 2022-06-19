import vk_api
from config import token
import json
from random import shuffle

session = vk_api.VkApi(token=token)
vk = session.get_api()


# Backend 40
def add_memes(group_id: int, special_word=""):
    memes_albums_id = []
    if special_word != "":
        for i in vk.photos.getAlbums(group_id=group_id)["items"]:
            if special_word in i["title"]:
                memes_albums_id.append({"id": i["id"], "title": i["title"]})
    else:
        memes_albums_id = [{"id": "wall", "title": "Group wall"}]
    try:
        memes_info = get_jsons_for_all_memes()
        if memes_info is None:
            memes_info = []
    except:
        memes_info = []
    for i in memes_albums_id:
        for data in vk.photos.get(group_id=group_id, album_id=i["id"], extended=1,
                                  count=min(vk.photos.get(group_id=group_id, album_id=i["id"], extended=1)["count"],
                                            900))["items"]:
            link = f"https://vk.com/photo{data['owner_id']}_{data['id']}"
            author = data["user_id"]
            if author == 100:
                author = -group_id
            memes_info.append(
                {"album_title": i["title"], "date": data["date"], "album_id": i["id"], "meme_id": data["id"],
                 "author_id": author, "likes": data["likes"]["count"], "link": link,
                 "owner_id": data["owner_id"]})
    with open('data.json', 'w') as outfile:
        json.dump(memes_info, outfile)


def clear_data():
    with open('data.json', 'w') as infile:
        pass


def get_jsons_for_all_memes():
    with open('data.json', 'r') as infile:
        data = json.load(infile)
        return data


def from_json_to_user_view(element):
    element['author_id'] = "id" + str(element['author_id'])
    if int(element['author_id'][2:]) < 0:
        element['author_id'] = "public" + element['author_id'][3:]
    return f"Album: {element['album_title']}\nAuthor: https://vk.com/{element['author_id']}\nLikes: {element['likes']}\nLink to meme: {element['link']}"


def find_meme(json_memes, meme_id):
    for i in json_memes:
        if i['meme_id'] == meme_id:
            return i


# Backend 30
def priority_system(meme_id):
    json_memes = get_jsons_for_all_memes()
    json_memes.sort(key=lambda x: x["likes"], reverse=True)
    priority = find_meme(json_memes, meme_id)
    json_memes.remove(priority)
    priority_list_of_memes = []
    cnt = 0
    for i in json_memes:
        priority_list_of_memes += [i] * (cnt // 5 + 1)
        cnt += 1
    cnt //= 5
    cnt += json_memes[0]["likes"]
    priority_list_of_memes += [priority] * cnt
    shuffle(priority_list_of_memes)
    return priority_list_of_memes


# Backend 10
def print_all_memes():
    json_memes = get_jsons_for_all_memes()
    for i in json_memes:
        print(from_json_to_user_view(i))
        print("---------------------------------------------------------------")


# Backend 20
def like_system(is_priority_meme_id=-1):
    if is_priority_meme_id != -1:
        memes = priority_system(is_priority_meme_id)
    else:
        memes = get_jsons_for_all_memes()
        memes.sort(key=lambda x: x["date"])
    size = len(memes)
    index = 0
    while True:
        i = memes[index % size]
        index += 1
        if vk.likes.isLiked(type="photo", owner_id=i["owner_id"], item_id=i["meme_id"])["liked"] == 1:
            continue
        print(from_json_to_user_view(i))
        print("Do you want to like it? y/n\nIf you want stop it, write \"stop\".")
        state = True
        while True:
            command = input().lower()
            if command == "stop":
                print("Stopped")
                state = False
                break
            if command in ["y", "yes", "n", "no"]:
                if command[0] == 'y':
                    vk.likes.add(type="photo", owner_id=i["owner_id"], item_id=i["meme_id"])
                    print("Liked")
                else:
                    print("Skipped")
                break
            else:
                print("It is not correct command. Correct commands: yes (or y), no (or n), stop.")
        if not state:
            break
        print("---------------------------------------------------------------")


# like_system(.sort(key=lambda x: x["likes"], reverse=True))
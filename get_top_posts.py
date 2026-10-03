import requests
import json
import time

ACCESS_TOKEN = "vk1.a.XT5f7sCtw_oWq92wCQG7XkanZRIcfOvUfoqWcoTYPc2lQ7j53W7y7q2XLHFsfI873C_xlXWh-Ib-ZgJZYTEGlJ4AVZj20FgjqUWVIBAn0EFpdcuGMvPNfDc_v3xi34VR0i2jt0Ew99jY6LpNE-euxOWekhWSMe90lU0Cku28PelJOKlAiLgvYlGCo4GIhMx2HAYLUCr4SUa6jst0V0DxEQ"
SCREEN_NAME = "ex_nord_lux"
API_VERSION = "5.199"

def vk_api(method, params):
    params.update({"access_token": ACCESS_TOKEN, "v": API_VERSION})
    response = requests.post(f"https://api.vk.com/method/{method}", data=params)
    return response.json()

def get_group_id(screen_name):
    result = vk_api("groups.getById", {"group_id": screen_name})
    if "response" in result and "groups" in result["response"]:
        return result["response"]["groups"][0]["id"]
    else:
        raise Exception(f"Ошибка получения ID группы: {result}")

def get_wall_posts(owner_id, count=100):
    all_posts = []
    offset = 0
    while len(all_posts) < count:
        result = vk_api("wall.get", {
            "owner_id": -owner_id,
            "count": min(100, count - len(all_posts)),
            "offset": offset,
            "filter": "owner"
        })
        if "response" in result:
            items = result["response"]["items"]
            if not items:
                break
            all_posts.extend(items)
            offset += len(items)
            time.sleep(0.3)
        else:
            raise Exception(f"Ошибка получения постов: {result}")
    return all_posts[:count]

def main():
    print("Получаем ID сообщества...")
    group_id = get_group_id(SCREEN_NAME)
    print(f"ID группы: {group_id}")

    print("Загружаем посты...")
    posts = get_wall_posts(group_id, count=200)

    print(f"Всего постов: {len(posts)}")

    posts_with_likes = [
        {
            "id": p["id"],
            "date": p["date"],
            "text": p["text"][:200] + "..." if len(p["text"]) > 200 else p["text"],
            "likes": p["likes"]["count"],
            "reposts": p["reposts"]["count"],
            "url": f"https://vk.com/wall-{group_id}_{p['id']}"
        }
        for p in posts if "likes" in p
    ]

    top_posts = sorted(posts_with_likes, key=lambda x: x["likes"], reverse=True)[:20]

    print("\n=== ТОП-20 ПОСТОВ ПО ЛАЙКАМ ===\n")
    for i, post in enumerate(top_posts, 1):
        print(f"{i}. Лайков: {post['likes']} | Репостов: {post['reposts']}")
        print(f"   Дата: {time.strftime('%Y-%m-%d %H:%M', time.localtime(post['date']))}")
        print(f"   Текст: {post['text']}")
        print(f"   Ссылка: {post['url']}")
        print()

    with open("top_posts.json", "w", encoding="utf-8") as f:
        json.dump(top_posts, f, ensure_ascii=False, indent=2)
    print("Результат сохранён в top_posts.json")

if __name__ == "__main__":
    main()
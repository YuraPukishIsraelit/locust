import random
from locust import SequentialTaskSet, HttpUser, task, between
from faker import Faker

import json

from helper.parse_all_images import get_all_image
from helper.random_sting import random_password


class MySeqTask(SequentialTaskSet):
    fake = Faker()
    user_thread = 1

    def __int__(self, parent):

        super.__init__(parent)
        self.token = ''
        self.user_data = ''
        self.home_page_content = ''

    @task
    def update_counter_user(self):
        self.user_counter = self.user_thread
        MySeqTask.user_thread += 1
        print(f'User {self.user_counter} - staring the flow ')

    @task
    def create_acc_or_login(self):
        def login():
            email, password = random.choice(['yurapykish@gmail.com','yurapykish+4@gmail.com','yurapykish+3@gmail.com','yurapykish+1@gmail.com',]), 'q1q1q1q1A'
            params = {
                "email": email,
                "password": password
            }
            headers = {"content-type": "application/json"}

            response = self.client.post("https://auth.stag.cookz.life/auth/login",
                                        data=json.dumps(params), headers=headers)

            token = response.json()['token']
            print(f'OK -> User {self.user_counter} is logged in')
            return token, {"email": email, "password": password}

        def user_create_acc():
            while True:

                email, password = self.fake.profile()['mail'], random_password(8)

                params = {
                    "name": self.fake.profile()['username'],
                    "email": email,
                    "password": password
                }
                headers = {"content-type": "application/json"}

                response = self.client.post("https://auth.stag.cookz.life/auth/signup", data=json.dumps(params),
                                            headers=headers)
                if response.status_code == 201:
                    break
            params = {
                "email": email,
                "password": password
            }
            headers = {"content-type": "application/json"}

            response = self.client.post("https://auth.stag.cookz.life/auth/login",
                                        data=json.dumps(params), headers=headers)

            token = response.json()['token']
            print(f'OK -> User {self.user_counter} is logged in')
            return token, {"email": email, "password": password}

        if random.randint(0, 1) == 1:
            self.token, self.user_data = login()
        else:
            #self.token, self.user_data = login()
            self.token, self.user_data = user_create_acc()

    """This request is used for getting the (20) posts from the homepage"""

    @task
    def get_feeds_content(self):
        with self.client.get(f'https://feed.stag.cookz.life/feed/items?size=20',
                             headers={"Authorization": f"Bearer {self.token}"},
                             catch_response=True, name='/post/20feeds') as get_feeds_content:

            if get_feeds_content.status_code == 200:
               #print(get_feeds_content.text)
                print(f'OK -> User {self.user_counter}, go to homepage page ')
                get_feeds_content.success()
                self.home_page_content = get_feeds_content.json()
            else:
                get_feeds_content.failure(f" Error -> User {self.user_counter} cannot get the homepage. "
                                          f"Get code {get_feeds_content.status_code} "
                                          f"Get text {get_feeds_content.text}")

    """Now I get random post and open. Get all info about post. Get post comments.
    Get post ingredient. Get post list who made this dish"""

    @task
    def get_detailed_post_info(self):
        self.post_id = self.home_page_content['content'][random.randint(0, 19)]['post']['id']

        with self.client.get(f'https://feed.stag.cookz.life/feed/items/{self.post_id}',
                             headers={"Authorization": f"Bearer {self.token}"}, catch_response=True,
                             name='/post/info') as all_info:
            if all_info.status_code == 200:
                print(f'OK -> User {self.user_counter} open the post {self.post_id}')
                all_info.success()
            else:
                all_info.failure(f"Error -> Cannot receive info about post {self.post_id}"
                                 f" Get code {all_info.status_code}"
                                 f" Get text {all_info.text}")

    @task
    def get_post_ingredient(self):
        with self.client.get(f'https://feed.stag.cookz.life/dishes/{self.post_id}/recipe?system=METRIC',
                             headers={"Authorization": f"Bearer {self.token}"},
                             catch_response=True, name='/post/ingredient') as get_post_recipe:
            if get_post_recipe.status_code == 200:
                print(f'OK -> User {self.user_counter} get post ingredients {self.post_id}')
                get_post_recipe.success()
            else:
                get_post_recipe.failure(f"Error -> Cannot receive post ingredient for post {self.post_id} "
                                        f" Get code {get_post_recipe.status_code}"
                                        f" Get text {get_post_recipe.text}"
                                        )

    @task
    def get_post_comments(self):
        with self.client.get(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/comments',
                             headers={"Authorization": f"Bearer {self.token}"},
                             catch_response=True, name='/post/comments') as get_post_comments:

            if get_post_comments.status_code == 200:
                print(f'OK -> User {self.user_counter} get post comments -> {self.post_id}')
                get_post_comments.success()
            else:
                get_post_comments.failure(f"Error -> Cannot receive post ingredient for post {self.post_id}"
                                          f" Get code {get_post_comments.status_code}"
                                          f" Get text {get_post_comments.text}"
                                          )

    @task
    def get_list_who_made_this_dish(self):
        with self.client.get(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/made-this',
                             headers={"Authorization": f"Bearer {self.token}"}, catch_response=True,
                             name='/list/who_made_this_dish') as made_this:
            if made_this.status_code == 200:
                print(f'OK ->User {self.user_counter} open Made this list post {self.post_id}')
                made_this.success()
            else:
                made_this.failure(f"Error ->Cannot receive user who made this dish {self.post_id}"
                                  f" Get code {made_this.status_code}"
                                  f" Get text {made_this.text}")

    """ User add comment to the dish, like dish, add dish to the bookmarks, Made This"""

    @task
    def test_add_comment_to_dish(self):

        # User have 3 option for create a comment: Just string, String + Image; just image
        comment_type = random.randint(1, 3)
        if comment_type == 1 :
            """user will send just string"""
            # data for requests
            comment_data = {'value': self.fake.text(random.randint(10, 100))}
            with self.client.post(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/comments', files=comment_data,
                                  headers={"Authorization": f"Bearer {self.token}"},
                                  catch_response=True, name='/comment/string') as add_comment:

                if add_comment.status_code == 200:
                    print(f'OK -> User {self.user_counter} add comment (just string) to the post {self.post_id}')
                    add_comment.success()
                else:
                    add_comment.failure(f"Error -> User {self.user_counter} cannot add comment to the post {self.add_comment.text}")
        elif comment_type == 2:
            """user will send just image"""
            # data for requests
            image = get_all_image("helper/images/")
            file = [('files', (
                'random.png', open(f'helper/images/' + image, 'rb'),
                'image/png'))]
            with self.client.post(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/comments', files=file,
                                  headers={"Authorization": f"Bearer {self.token}"},
                                  catch_response=True, name='/comment/image') as add_comment:

                if add_comment.status_code == 200:
                    print(f'OK -> User {self.user_counter} add comment (just image) to the post {self.post_id}')
                    add_comment.success()
                else:
                    add_comment.failure(f"Error -> User {self.user_counter} cannot add comment to the post {self.add_comment.text}")
        else:
            """user will send String + image"""
            # data for requests
            comment_data = {'value': self.fake.text(random.randint(10, 100))}
            image = get_all_image("helper/images/")
            file = [('files', (
                'random.png', open(f'helper/images/' + image, 'rb'),
                'image/png'))]
            with self.client.post(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/comments', files=file,
                                  data=comment_data,
                                  headers={"Authorization": f"Bearer {self.token}"},
                                  catch_response=True, name='/comment/string+image') as add_comment:

                if add_comment.status_code == 200:
                    print(f'OK -> User {self.user_counter} add comment (String + image) to the post {self.post_id}')
                    add_comment.success()
                else:
                    add_comment.failure(f"Error -> User {self.user_counter} cannot add comment to the post {self.add_comment.text}")

    @task
    def user_made_this_dish(self):
        """add dish to the Made This"""
        with self.client.post(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/made-this',
                              headers={"Authorization": f"Bearer {self.token}"}, catch_response=True,
                              name='/user/add_post_to_made_this') as made_this:

            if made_this.status_code == 200:
                print(f'OK - > User {self.user_counter} tap on the Made this button')
                made_this.success()
            else:
                made_this.failure(f"Error -> User {self.user_counter} cannot add post {self.post_id} to the Made This"
                                  f" Get code {made_this.status_code}"
                                  f" Get text {made_this.text}")

    @task
    def add_post_to_bookmark(self):
        """add dish to the bookmark"""
        with self.client.post(f'https://feed.stag.cookz.life/me/feed/{self.post_id}/bookmarks',
                              headers={"Authorization": f"Bearer {self.token}"},
                              catch_response=True, name='/user/add_post_to_bookmark') as add_post_to_bookmark:
            if add_post_to_bookmark.status_code == 200:
                print(f'OK -> User {self.user_counter} add post {self.post_id} to the bookmarks')
                add_post_to_bookmark.success()
            else:
                add_post_to_bookmark.failure(
                    f"Error -> User {self.user_counter} cannot add post {self.post_id} to the bookmarks"
                    f" Get code {add_post_to_bookmark.status_code}"
                    f" Get text {add_post_to_bookmark.text}")

    @task
    def like_post(self):
        """User like post"""
        with self.client.post(f'https://feed.stag.cookz.life/feed/items/{self.post_id}/likes',
                              headers={"Authorization": f"Bearer {self.token}"}, catch_response=True,
                              name='/user/like-post') as like_post:
            if like_post.status_code == 200:
                print(f'OK -> User {self.user_counter} like post {self.post_id} ')
                like_post.success()
            else:
                like_post.failure(f"Error -> User {self.user_counter} cannot like_ post {self.post_id} "
                                  f" Get code {like_post.status_code} "
                                  f" Get text {like_post.text}")

    """User info section. Add profile and cover image"""

    @task
    def add_cover_photo(self):
        image = get_all_image("helper/images/")
        #print(image)
        file = [('file', (
            'random.png', open(f'helper/images/' + image, 'rb'),
            'image/png'))]
        with self.client.post(f'https://auth.stag.cookz.life/users/me/images/cover', files=file,
                              headers={"Authorization": f"Bearer {self.token}"},
                              catch_response=True, name='/user/add_cover_photo') as add_cover_photo:

            if add_cover_photo.status_code == 200:
                print(f'OK -> User {self.user_counter} cover photo')
                add_cover_photo.success()
            else:
                add_cover_photo.failure(f"Error -> User {self.user_counter} cannot add cover photo"
                                            f" Get {add_cover_photo.status_code}"
                                            f" Get {add_cover_photo.text}")

    @task
    def add_profile_photo(self):
        image = get_all_image("helper/images/")
        # print(image)
        file = [('file', (
            'random.png', open(f'helper/images/' + image, 'rb'),
            'image/png'))]
        with self.client.post(f'https://auth.stag.cookz.life/users/me/images/profile', files=file,
                              headers={"Authorization": f"Bearer {self.token}"},
                              catch_response=True, name='/user/add_profile_photo') as add_profile_photo:

            if add_profile_photo.status_code == 200:
                print(f'OK -> User {self.user_counter} profile photo')
                add_profile_photo.success()
            else:
                add_profile_photo.failure(f"Error -> User {self.user_counter} cannot add profile photo"
                                          f" Get {add_profile_photo.status_code}"
                                         f" Get {add_profile_photo.text}")

    @task
    def user_update_account_info(self):
        while True:
            params = {
                "email": self.user_data['email'],
                "username": self.fake.profile()['username'],
                "firstName": self.fake.first_name(),
                "lastName": self.fake.last_name(),
                "gender": random.choice(["FEMALE", "MALE"])
            }
            with self.client.put(f'https://auth.stag.cookz.life/users/me/account', data=json.dumps(params),
                                 headers={"Authorization": f"Bearer {self.token}", "content-type": "application/json"},
                                 catch_response=True, name='/update/user-info') as update_account:
                if update_account.status_code == 200:
                    print(f'OK -> User {self.user_counter} update profile info')
                    update_account.success()
                    break

    @task
    def add_tags(self):
        # firstly we have to see all user tags
        all_tags = self.client.get(f'https://auth.stag.cookz.life/predefined/tags',
                                   headers={"Authorization": f"Bearer {self.token}"})
        tag = all_tags.json()
        tags = tag[0]['tags'] + tag[1]['tags'] + tag[2]['tags']
        random_tag_ids = random.sample(tags, 5)

        with self.client.put(
                f'https://auth.stag.cookz.life/users/me/tags?tags={random_tag_ids[0]["id"]},{random_tag_ids[1]["id"]},'
                f'{random_tag_ids[2]["id"]},{random_tag_ids[3]["id"]},{random_tag_ids[4]["id"]}',
                headers={"Authorization": f"Bearer {self.token}"},
                catch_response=True, name='/add/tags') as user_update_tags:
            if user_update_tags.status_code == 200:
                print(f"OK -> User {self.user_counter}  add tags to the profile.")
                user_update_tags.success()
            else:
                user_update_tags.failure(f"Error -> User {self.user_counter} cannot add tags to the profile"
                                         f" Get {user_update_tags.status_code}"
                                         f" Get {user_update_tags.text}")


    @task
    def user_add_bio(self):

        param = {
            "value": self.fake.text(random.randint(20, 100))
        }
        with self.client.put(f'https://auth.stag.cookz.life/users/me/bio', data=json.dumps(param),
                             headers={"Authorization": f"Bearer {self.token}", "content-type": "application/json"},
                             catch_response=True, name='/add/bio') as update_user_bio:

            if update_user_bio.status_code == 200:
                print(f"OK -> User {self.user_counter} add BIO to the profile ")
                update_user_bio.success()
            else:
                update_user_bio.failure(
                    f"Error -> User {self.user_counter} cannot add BIO to the profile. Get {update_user_bio.text} "
                    f"Get {update_user_bio.status_code}")

    """Get users bookmark, dishes, made this"""

    @task
    def get_bookmarks(self):

        with self.client.get("https://feed.stag.cookz.life/feed/my/bookmarks",
                             headers={"Authorization": f"Bearer {self.token}",
                                      "content-type": "application/json"}, catch_response=True,
                             name='/user/bookmarks') as user_bookmarks:
            if user_bookmarks.status_code == 200:
                print(f"OK -> User {self.user_counter}  open his bookmark list ")
                user_bookmarks.success()
            else:
                user_bookmarks.failure(
                    f"Error -> User {self.user_counter} cannot open his bookmark "
                    f"Get {user_bookmarks.status_code}"
                    f" Get {user_bookmarks.text}")

    @task
    def made_this(self):

        with self.client.get("https://feed.stag.cookz.life/feed/my/made-this",
                             headers={"Authorization": f"Bearer {self.token}", "content-type": "application/json"},
                             catch_response=True, name='/user/made-this') as made_this:
            if made_this.status_code == 200:
                print(f"OK -> User {self.user_counter}  open his made_this list ")
                made_this.success()
            else:
                made_this.failure(
                    f"Error -> User {self.user_counter}, {self.user_data['email']} cannot open his made_this list"
                    f" Get {made_this.status_code}"
                    f" Get {made_this.text}")


    @task
    def my_dishes(self):

        with self.client.get("https://feed.stag.cookz.life/feed/my/dishes",
                             headers={"Authorization": f"Bearer {self.token}",
                                      "content-type": "application/json"}, name='/user/dishes',
                             catch_response=True) as my_dishes:
            if my_dishes.status_code == 200:
                print(f"OK -> User {self.user_counter} open his made_this list ")
                my_dishes.success()
                if len(my_dishes.json()['content']) > 0:
                    my_post_id = my_dishes.json()['content'][-1]

                    """Update delete post"""

                    @task
                    def update_post():
                        data = json.dumps({
                            "dish": "",

                            "post": {
                                "title": self.fake.text(random.randint(10, 50)),
                                "description": self.fake.text(random.randint(10, 50))
                            }
                        })
                        with self.client.put(f"https://feed.stag.cookz.life/feed/items/{my_post_id}", data=data,
                                             headers={'Authorization': f'Bearer {self.token}',
                                                      'Content-Type': 'application/json'},
                                             catch_response=True, name='/post/update') as update_my_dishes:
                            if update_my_dishes.status_code == 200:
                                print(f"OK -> User {self.user_counter} update his dish {my_post_id} ")
                                update_my_dishes.success()
                            else:
                                update_my_dishes.failure(f"User {self.user_counter} does not update "
                                                         f"his dish {my_post_id}"
                                                         f"Get {update_my_dishes.status_code}"
                                                         f"Get {update_my_dishes.text}")


            else:
                my_dishes.failure(
                    f"Error -> User {self.user_counter} cannot open his made_this list "
                    f"Get {my_dishes.status_code} "
                    f"Get {my_dishes.text}")

    """Searching screen"""

    @task
    def search_title_desc(self):
        """
            Search by dish title and description
        """
        key = self.fake.sentence(nb_words=1)
        key = key[:-1]
        with self.client.get(f"https://feed.stag.cookz.life/feed/items/search?search={key}",
                             headers={"Authorization": f"Bearer {self.token}", "content-type": "application/json"},
                             catch_response=True, name='/title/search') as search_title_desc:
            if search_title_desc.status_code == 200:
                print(f"OK -> User {self.user_counter} try to find a dish which include {key} "
                      f"in the title or description ")
                search_title_desc.success()
            else:
                search_title_desc.failure(
                    f"Error -> User {self.user_counter} cannot find the posts. Search key = {key} "
                    f"Get {search_title_desc.status_code} "
                    f"Get {search_title_desc.text} ")

    @task
    def search_hashtags(self):
        """
            Search by hashtags
        """
        key = self.fake.sentence(nb_words=1)
        key = key[:-1]
        with self.client.get(f"https://feed.stag.cookz.life/hashtags?search={key}",
                             headers={"Authorization": f"Bearer {self.token}",
                                      "content-type": "application/json"}, catch_response=True,
                             name='/hashtags/search') as search_hashtags:
            if search_hashtags.status_code == 200:
                print(f"OK -> User {self.user_counter} try to find a dish which include  {key} hashtags")
                search_hashtags.success()
            else:
                search_hashtags.failure(
                    f"Error -> User {self.user_counter} Hashtags. Search key {key} "
                    f"Get {search_hashtags.status_code} "
                    f"Get {search_hashtags.text} ")

    @task
    def test_search_name(self):
        """
            Search by username
        """
        key = self.fake.sentence(nb_words=1)
        key = key[:-1]
        with self.client.get(f"https://auth.stag.cookz.life/users?search={key}",
                             headers={"Authorization": f"Bearer {self.token}",
                                      "content-type": "application/json"}, catch_response=True,
                             name='/user/search') as test_search_name:
            if test_search_name.status_code == 200:
                print(f"OK -> User {self.user_counter} try to find a USER which include  {key} ")
                test_search_name.success()
            else:
                test_search_name.failure(
                    f"Error -> User {self.user_counter} cannot find a USER. Get {test_search_name.status_code} "
                    f"Get {test_search_name.text}")

    @task
    def test_search_category(self):
        """
            Search by category
        """

        all_subcategories_request = self.client.get('https://feed.stag.cookz.life/predefined/categories',
                                                    headers={"Authorization": f"Bearer {self.token}"})

        subcategories_list = []
        for category in all_subcategories_request.json():
            subcategories_list.extend(category["subCategories"])

        search_list = random.choices(subcategories_list, k=random.randint(1, len(subcategories_list)))
        search_query = 'https://feed.stag.cookz.life/feed/items/search?'
        for subcategory in search_list:
            search_query += f"categoryIds={subcategory['id']}&"

        with self.client.get(f"{search_query}", headers={"Authorization": f"Bearer {self.token}",
                                                         "content-type": "application/json"}, catch_response=True,
                             name='/category/search') as test_search_category:
            if test_search_category.status_code == 200:
                print(f"OK -> User {self.user_counter} provide search by categories ")
                test_search_category.success()
            else:
                test_search_category.failure(
                    f"Error - > User {self.user_counter} cannot find a USER. Get {test_search_category.status_code} "
                    f"Get {test_search_category.text}")

    @task
    def finish(self):
        print(f'User {self.user_counter} - finished the flow ')


class Load(HttpUser):
    host = 'https://auth.stag.cookz.life'
    tasks = [MySeqTask]
    wait_time = between(1, 4)

# print(fake.profile()['mail'])
# print(fake.profile()['username'], fake.profile()['mail'])
#from locust.main import runners
#runners.locust_runner.quit()
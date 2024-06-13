import enum
import json
import os
import requests
import threading

class TYPES(enum.Enum):
    NONE = 0
    PAGE = 1
    PRODUCT = 2
    SET_REVIEW = 3
    GET_REVIEW = 4
    SAVE_REVIEW = 5


class AdidasThread(threading.Thread):
    t_id: int = 0
    t_type: TYPES = TYPES.NONE
    t_url: str = ""
    t_page: int = 0

    t_products: list = []
    t_products_counter: int = 0
    pages: list = []
    products: list = []
    reviews_url: list = []
    product_reviews: list = []

    headers = {
        'authority': 'www.adidas.at',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'content-type': 'application/json',
        'user-agent': 'PostmanRuntime/7.35.0',
    }

    def __init__(
        self, t_id, t_type, t_url, t_page, group=None, 
        target=None, name=None, args=(), kwargs=None, *, daemon=None):

        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.t_id = t_id
        self.t_type = t_type
        self.t_url = t_url
        self.t_page = t_page
        # self.t_products = []


    @staticmethod
    def load_data(file_name):
        with open(file_name, "r") as f:
            file_contents = json.loads(f.read())
            f.close()
        return file_contents


    @staticmethod
    def save_data(data, file_name):
        items = []
        if os.path.exists(file_name):
            file_contents = AdidasThread.load_data(file_name)
            items.extend(file_contents)
        items.extend(data)
        with open(file_name, "w") as f:
            json.dump(items, f)
        return


    def request_url(self, params=None):
        try:
            if params is None:
                response = requests.get(self.t_url, headers=self.headers, allow_redirects=True,)
                if response.status_code != 200:
                    print(f"error {response.status_code} for {self.t_url}")
                    return
                return response
            response = requests.get(self.t_url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"error {response.status_code} for {self.t_url}")
                return
            return response
        except Exception as e:
            print(f"error {e} for {self.t_url} in Exception")
            return


    def set_pages(self):
        params = {'query': 'all', "start": 0}
        response = self.request_url(params=params)

        if response is None:
            return self.set_pages()

        response_json = response.json()
        item_list = response_json["raw"]["itemList"]
        pages_count = item_list["count"] // item_list["viewSize"]
        pages = [i for i in range(1, pages_count + 1)]
        AdidasThread.pages = pages

        return


    def get_products(self):
        params = {'query': 'all', "start": (self.t_id - 1) * 48}
        # print(params)
        response = self.request_url(params=params)
        if response is None:
            return
        response_json = response.json()

        try:
            self.t_products.append(response_json["raw"]["itemList"]["items"])
        except KeyError:
            return

        if not self.t_products:
            return self.get_products()

        
        print("COUNTER: ", AdidasThread.t_products_counter)
        AdidasThread.products.extend(AdidasThread.t_products)
        if AdidasThread.t_products_counter == 9:
            AdidasThread.save_data(AdidasThread.t_products, file_name=f"products{self.t_page}.json")
            AdidasThread.t_products_counter = 0
            AdidasThread.t_products = []
        else:
            AdidasThread.t_products_counter += 1


    def generate_offsets(offset_total, limit):
        offsets = []
        for i in range(0, offset_total):
            res = i * limit
            if res < offset_total:
                offsets.append(res)
            elif res > offset_total:
                res = res - (offset_total - offsets[-1])
                offsets.append(res)
                break
            else:
                break
        # offsets = list(reversed(offsets))
        return offsets


    def set_reviews_urls(self):
        # print('man injam')
        if len(AdidasThread.products) > 0:
            for _ in range(len(AdidasThread.products)):
                if len(AdidasThread.products) > 0:
                    product = AdidasThread.products.pop()[0]
                    # obj = {"productId": product["productId"], "modelId": product["modelId"]}
                    first_part = "https://www.adidas.at/api/models/"
                    second_part = "/reviews?bazaarVoiceLocale=de_AT&feature&includeLocales=de%2A&limit="
                    url = f'{first_part}{product["modelId"]}{second_part}5&offset=0'
                    self.t_url = url
                    response = self.request_url()
                    offset_total = response.json()["totalResults"]
                    offsets = AdidasThread.generate_offsets(offset_total=offset_total, limit=5)
                    obj = (url, offsets, product["productId"])
                    # print(obj)
                    AdidasThread.reviews_url.append(obj)
                else:
                    pass
        else:
            print("<set_reviews_urls>: no product available !")


    def get_reviews(self):
        # response = self.request_url()
        # if response is None:
        #     return
        # reviews = {"productId": self.t_page, "page_reviews":  response.json()}

        # AdidasThread.product_reviews.append(reviews)
        if len(AdidasThread.reviews_url) > 1:
            review_data = AdidasThread.reviews_url.pop()
            for offset in review_data[1]:
                url = review_data[0][0:-1] + str(offset) 
                print(url)
                response = requests.get(url, headers=AdidasThread.headers)
                if response is None:
                    return
                reviews = {"productId": review_data[2], "page_reviews":  response.json()}

                AdidasThread.product_reviews.append(reviews)        
    
    def save_reviews(self):
        reviews = AdidasThread.product_reviews
        self.save_data(reviews, "reviews.json")
        AdidasThread.product_reviews = []


    def run(self):
        if self.t_type == TYPES.PAGE:
            self.set_pages()

        elif self.t_type == TYPES.PRODUCT:
            self.get_products()

        elif self.t_type == TYPES.SET_REVIEW:
            self.set_reviews_urls()

        elif self.t_type == TYPES.GET_REVIEW:
            self.get_reviews()
            # pass
        
        elif self.t_type == TYPES.SAVE_REVIEW:
            self.save_reviews()
            # pass


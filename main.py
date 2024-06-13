import time

import AdidasThread as Th

if __name__ == "__main__":
    threads = []

    pages_thread = Th.AdidasThread(
        t_id=1,
        t_type=Th.TYPES.PAGE,
        t_url="https://www.adidas.at/api/plp/content-engine/search?",
        t_page=0
    )
    pages_thread.start()
    pages_thread.join()


    pages = Th.AdidasThread.pages

    adThread = Th.AdidasThread(t_id=0, t_type=Th.TYPES.NONE, t_url="", t_page=0)


    while True:
        print("LEN REVIEWS URL: ", len(adThread.reviews_url))
    # for i in range(10):

        if pages:
            print("\n\nLEN PAGES: ", len(pages))
            page = pages.pop()
            products_thread = Th.AdidasThread(
                t_id=page,
                t_type=Th.TYPES.PRODUCT,
                t_url="https://www.adidas.at/api/plp/content-engine/search?",
                t_page=page
            )
            products_thread.start()
            time.sleep(0.6)
            for _ in range(4):
                set_review_thread = Th.AdidasThread(
                    t_id=page,
                    t_type=Th.TYPES.SET_REVIEW,
                    t_url="https://www.adidas.at/api/plp/content-engine/search?",
                    t_page=page
                )
                set_review_thread.start()
                # set_review_thread.join()
                print("LEN REVIEWS URL: ", len(adThread.reviews_url))
                # print(adThread.reviews_url)
                

            if len(adThread.reviews_url) > 1:
                for i in range(16):
                    get_reviews_thread = Th.AdidasThread(
                        t_id=i,
                        t_type=Th.TYPES.GET_REVIEW,
                        t_url="",
                        t_page=""
                    )
                    print("GETTING REVIEWS: ", get_reviews_thread)
                    get_reviews_thread.start()
                    # get_reviews_thread.join()
                    time.sleep(0.2)

                time.sleep(0.2)
                save_reviews_thread = Th.AdidasThread(
                    t_id=i+5,
                    t_type=Th.TYPES.SAVE_REVIEW,
                    t_url="",
                    t_page=""
                )
                save_reviews_thread.start() 
                # save_reviews_thread.join() 

                          
        
        else:
            time.sleep(2)

            # for thread in threads:
            #     thread.join()
            print("DONE")
            break
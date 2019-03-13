import json
import urllib
import math
import re
from urllib import parse
from urllib import request
from urllib.parse import urlencode, quote_plus

# API URL
SERVER = 'https://qsz08t9vtl.execute-api.us-east-1.amazonaws.com/production'
GOOGLE_MAPS = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=AIzaSyAAZrBlAiCwBSoxQzU4iVL29LxmbHz7vBU'

def get_qloo(queries, location, radius):
    def getSearch(query, category, location):
        """This function searches and returns entities and their attributes.

        Args:
            query: a string containing the name/title of an entity.
            category: a string containing the parent category and sub-category seperated by '/' of the entity being searched.
                The following are supported parent category and sub-category pairings:
                    - books/books
                    - books/authors
                    - dining/restaurants
                    - fashion/brands
                    - film/movies
                    - music/artists
                    - travel/hotels
                    - tv/shows

        Returns:
            An array of search results with attributes ordered by relevance or an empty array if no results are found.
        """

        if query and category:
            if location:
                params = urllib.parse.urlencode({'category': category, 'query': query, }, quote_via=quote_plus)   # debug

                url = SERVER + '/search?{}'.format(params)

                with urllib.request.urlopen(url) as f:
                    data = f.read().decode('utf-8')

                data = json.loads(data)

                return data['results']
            else:
                params = urllib.parse.urlencode({'category': category, 'query': query}, quote_via=quote_plus)    # debug

                url = SERVER + '/search?{}'.format(params)

                with urllib.request.urlopen(url) as f:
                    data = f.read().decode('utf-8')

                data = json.loads(data)

                return data['results']


    def getRecs(Qid, dst_category, location, radius):
        """This function recommends entities and returns their attributes.

        Args:
            Qid: a string containing the Qloo ID for an entity.
            dst_category: a string containing the desired parent category and sub-category seperated by '/' for recommendations.
                The following are supported parent category and sub-category pairings:
                    - books/books
                    - books/authors
                    - dining/restaurants
                    - fashion/brands
                    - film/movies
                    - music/artists
                    - travel/hotels
                    - tv/shows

        Returns:
            An array of recommendations with their attributes ordered by affinity score.
        """

        if Qid and dst_category:
            params = urllib.parse.urlencode({'sample': Qid, 'category': dst_category, 'location': location, 'radius': radius}, quote_via=quote_plus)  # debug

            url = SERVER + '/recs?{}'.format(params)
            # print(url)
            with urllib.request.urlopen(url) as f:
                data = f.read().decode('utf-8')

            data = json.loads(data)
            # print(data)

            return data['results']

    """
    query, category: Entity to search for along with the category it belongs to
    result_category: Desired category for recommendations
    Example:
    query = 'Stromae'
    category = 'music/artists'
    result_category = 'music/songs'
    (warning, nonsense math)
    """
    def recommendations(queries, category, result_category, location, radius):
        search_results = []
        for query in queries:
            search_results.append(getSearch(query, category, [0, 0]))
        # print(search_results)
        # TODO: bound this and do it for multiple artists
        if search_results:
            id_for_recs = ""
            # print(id_for_recs)
            # print(max(1, math.floor(10 - len(queries) * 3)))
            for result in search_results:
                # print(result)
                try:
                    for i in range(0, max(1, math.floor(10 - len(queries) * 3))):
                        # print(i)
                        id_for_recs += result[i]['id'] + ','
                except:
                    print("you ran into indexing errors")
            id_for_recs = id_for_recs[:-1]
            # print(id_for_recs)

            recs_results = getRecs(id_for_recs, result_category, location, radius)

            # Return top 5 recommendations
            top_k = 20

            # print('Top {} {} for {}'.format(top_k, result_category, queries))
            reccs = {
            'reccs' : [],
            'affinity' : 0
            }
            affinity = 0
            print(len(recs_results))
            try:
                for idx in range(top_k):
                    reccs['reccs'].append(recs_results[idx]['name'])
                    affinity += recs_results[idx]['query']['affinity']
                # print('{}. {}'.format(idx+1, recs_results[idx]['name']))
            except:
                return "No results found in this location"
            affinity /= top_k
            # print(affinity)
            reccs['affinity'] = affinity
            return reccs
        else:
            print('No results found.')

    result = {}
    # result['hotels'] = recommendations(["John Coltrane", "Frank Sinatra"], "music/artists", "travel/hotels", "40.7128,-74.0060", 5)
    # # result['hotels'] = recommendations(["Adele", "Sylvan Esso", "Madonna", "John Coltrane", "Frank Sinatra"], "music/artists", "travel/hotels", "40.7128,-74.0060", 5)
    # result['restaurants'] = recommendations(["John Coltrane", "Frank Sinatra"], "music/artists", "dining/restaurants", "40.7128,-74.0060", 5)
    # result['artists'] = recommendations(["John Coltrane", "Frank Sinatra"], "music/artists", "music/artists", "40.7128,-74.0060", 5)
    # print(result)
    result['hotels'] = recommendations(queries, "music/artists", "travel/hotels", location, radius)
    # result['hotels'] = recommendations(["Adele", "Sylvan Esso", "Madonna", "John Coltrane", "Frank Sinatra"], "music/artists", "travel/hotels", "40.7128,-74.0060", 5)
    result['restaurants'] = recommendations(queries, "music/artists", "dining/restaurants", location, radius)
    result['artists'] = recommendations(queries, "music/artists", "music/artists", location, radius)

    # Adding latitude/longitude lookup for each hotel & restaurant
    hotelList = []
    restaurantList = []
    for hotel in result['hotels']['reccs']:
        print("hotel name:", hotel);
        hotel = re.sub(u"(\u0020)", "+", hotel)
        #hotel = hotel.replace(" ", "+")
        index = hotel.find('-')
        if index != -1:
            hotel = hotel[0:index]
        index = hotel.find('W+')
        if index != -1:
            hotel = hotel[0]

        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + hotel + ',+CA&key=AIzaSyAAZrBlAiCwBSoxQzU4iVL29LxmbHz7vBU'
        with urllib.request.urlopen(url) as f:
            mapData = f.read().decode('utf-8')
        mapData = json.loads(mapData)
        hotelList.append(mapData['results'][0]['geometry']['location'])
    for restaurant in result['restaurants']['reccs']:
        print("restaurant:", restaurant);
        restaurant = re.sub(u"(\u0020)", "+", restaurant)
        restaurant = re.sub(u"(\u00f4|\u2018|\u2019)", "'", restaurant)
        #restaurant = restaurant.replace(" ", "+")
        index = restaurant.find('-')
        if index != -1:
            restaurant = restaurant[0:index]
        if 'Sweet' in restaurant:
            restaurant = '324+N+Leavitt+St'

        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + restaurant + ',+CA&key=AIzaSyAAZrBlAiCwBSoxQzU4iVL29LxmbHz7vBU'
        with urllib.request.urlopen(url) as f:
            mapData = f.read().decode('utf-8')
        mapData = json.loads(mapData)
        restaurantList.append(mapData['results'][0]['geometry']['location'])


    result['hotels']['reccs'].append(hotelList)
    result['restaurants']['reccs'].append(restaurantList)

    print("hotelList:", hotelList)
    print("restaurantList:", restaurantList)

    return result
# print(get_qloo(["John Coltrane", "Frank Sinatra"], "40.7128,-74.0060", 5))

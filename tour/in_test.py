# XXX -- tour operator name
import datetime

class OurToXXXReqConvertor( object ):

    def __init__( self ): pass


    def our_req_to_dict( self, our_req, ext_req ):

        @staticmethod
        def __our_food_type_to_exid( food_type ):
            our_to_exid = \
            {
            #our_id | exid
              1  : ( 12, ),   # None
              2  : ( 1, ),    # BB
              3  : ( 7, ),    # HB
              4  : ( 8, ),    # FB
              5  : ( 9, 14 ), # All
              6  : ( 10, ),   # UAll
            }
            return our_to_exid[food_type]

        @staticmethod
        def __our_category_to_exid( category_id ):
            our_to_exid = \
            {
#           our_id | exid
              4  : 401, # 2*  -> 2*
              5  : 401, # 2*+ -> 2*
              6  : 402, # 3*  -> 3*
              7  : 402, # 3*+ -> 3*
              8  : 403, # 4*  -> 4*
              9  : 403, # 4*+ -> 4*
              10 : 404, # 5*  -> 5*
              11 : 404, # 5*+ -> 5*
              16 : 411, # HV2 -> HV2
              17 : 410, # HV1 -> HV1
            }
            return our_to_exid[category_id]

        def __currency_to_str( currency ):
            currency2str = \
            {
              currency.USD : 2,
              currency.EUR : 3,
              currency.RUB : 1
            }
            return currency2str[currency.get_id()]

        def __our_food_types_to_exids( food_types ):
            res = []
            for ft in food_types: res += __our_food_type_to_exid( ft )
            return res

        def __our_categories_to_exids( categories ):
            res = set()
            for c in categories: res.add( __our_category_to_exid( c ) )
            return list( res )

        r = {}

        r['STATEINC'] = ext_req.get_country_id()

        departure_id = ext_req.get_departure_id()
        if departure_id > 0:
          r['TOWNFROMINC']      = departure_id
          #r['hasTickets']      = True
          #r['ticketsIncluded'] = True
        else:
            pass
          # raise UnsupportedSearchParam( 2 )

        #cities = ext_req.get_city_ids()
        #if len( cities ):
          #r['cities'] = cities

        # meals
        meals = our_req.get_food_types()
        if len( meals ):
          r['MEAL'] = __our_food_types_to_exids( meals )

        # stars
        stars = our_req.get_hotel_categories()
        if len( stars ):
          r['STARS'] = __our_categories_to_exids( stars )

        # hotels
        hotels = ext_req.get_hotel_ids()
        if len( hotels ):
          r['HOTELS'] = hotels

        # adults
        adults = ext_req.get_number_of_adults()
        r['ADULT'] = adults if adults != 123 else 2

        # kids & ages
        __kids_list = ext_req.get_children()
        kids = len( __kids_list )
        if kids > 0:
          ages = [x.get_age() for x in __kids_list]
          r['CHILD'] = kids
          r['AGES'] = ages

        # nightsMin
        nights_min = ext_req.get_min_duration()
        if nights_min != -1: r['NIGHTS_FROM'] = nights_min

        # nightsMax
        nights_max = ext_req.get_max_duration()
        if nights_max != -1: r['NIGHTS_TILL'] = nights_max

        # priceMin
        price_min = ext_req.get_min_price()
        if price_min > 0: r['PRICE_MIN'] = int(price_min)

        # priceMax
        price_max = ext_req.get_max_price()
        if price_max > 0: r['PRICE_MAX'] = int(price_max)

        # currencyAlias
        currency = ext_req.get_currency()
        r['CURRENCY'] = __currency_to_str( currency )

        # departFrom
        depart_from = ext_req.get_min_date()
        if depart_from != datetime.date.min:
          r['CHECKIN_BEG'] = depart_from.strftime( '%d.%m.%Y' )

        # departTo
        depart_to = ext_req.get_max_date()
        if depart_to != datetime.date.max:
          r['CHECKIN_END'] = depart_to.strftime( '%d.%m.%Y' )

        # stops
        #r['FREIGHT'] = 0
        includeStop = our_req.get_include_stop()
        r['FILTER'] = int(not includeStop)

        r['page'] = 'search_tour'
        r['samo_action'] = 'PRICES'

        return r
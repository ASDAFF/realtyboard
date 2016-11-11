class Hotel:
  def __init__( self ):
    self.__id             = None
    self.__name           = None
    self.__URL            = None
    self.__category       = None
    self.__place          = None
    self.__accommodation  = None
    self.__room           = None
    self.__meal           = None
    self.__duration       = None

  def set_id( self, id ): self.__id = id
  def get_id( self ): return self.__id

  def set_name( self, name ): self.__name = name
  def get_name( self ): return self.__name

  def set_URL( self, URL ): self.__URL = URL
  def get_URL( self ): return self.__URL

  def set_category( self, category ): self.__category = category
  def get_category( self ): return self.__category

  def set_place( self, place ): self.__place = place
  def get_place( self ): return self.__place

  def set_accommodation( self, accommodation ): self.__accommodation = accommodation
  def get_accommodation( self ): return self.__accommodation

  def set_room( self, room ): self.__room = room
  def get_room( self ): return self.__room

  def set_meal( self, meal ): self.__meal = meal
  def get_meal( self ): return self.__meal

  def set_duration( self, duration ): self.__duration = duration
  def get_duration( self ): return self.__duration


class Tour:
  def __init__( self ):
    self.__source_id        = -1
    self.__price            = 0.0
    self.__currency         = None
    self.__hotels           = None
    self.__accommodation    = None
    self.__departure_date   = None
    self.__duration         = None
    self.__transport        = None
    self.__transport_incl   = None
    self.__hotel_status     = None
    self.__transport_status = None
    self.__stop_sale        = None
    self.__tour_type        = None
    self.__comment          = None
    self.__id               = None
    self.__spo              = None
    self.__link_data        = None

  def set_source_id( self, source_id ): self.__source_id = source_id
  def get_source_id( self ): return self.__source_id

  def set_price( self, price ): self.__price = price
  def get_price( self ): return self.__price

  def set_currency( self, currency ): self.__currency = currency
  def get_currency( self ): return self.__currency

  def set_hotels( self, hotels ): self.__hotels = hotels
  def get_hotels( self ): return self.__hotels

  def set_accommodation( self, accommodation ): self.__accommodation = accommodation
  def get_accommodation( self ): return self.__accommodation

  def set_departure_date( self, departure_date ): self.__departure_date = departure_date
  def get_departure_date( self ): return self.__departure_date

  def set_duration( self, duration ): self.__duration = duration
  def get_duration( self ): return self.__duration

  def set_transport( self, transport ): self.__transport = transport
  def get_transport( self ): return self.__transport

  def set_transport_incl( self, transport_incl ): self.__transport_incl = transport_incl
  def get_transport_incl( self ): return self.__transport_incl

  def set_hotel_status( self, hotel_status ): self.__hotel_status = hotel_status
  def get_hotel_status( self ): return self.__hotel_status

  def set_transport_status( self, transport_status ): self.__transport_status = transport_status
  def get_transport_status( self ): return self.__transport_status

  def set_stop_sale( self, stop_sale ): self.__stop_sale = stop_sale
  def get_stop_sale( self ): return self.__stop_sale

  def set_tour_type( self, tour_type ): self.__tour_type = tour_type
  def get_tour_type( self ): return self.__tour_type

  def set_comment( self, comment ): self.__comment = comment
  def get_comment( self ): return self.__comment

  def set_id( self, id ): self.__id = id
  def get_id( self ): return self.__id

  def set_spo( self, spo ): self.__spo = spo
  def get_spo( self ): return self.__spo

  def set_link_data( self, link_data ): self.__link_data = link_data
  def get_link_data( self ): return self.__link_data

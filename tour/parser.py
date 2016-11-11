# объекты-оболочки
# our_req -- тип питания, категория отеля, стопы(да/нет)
# ext_req -- город отправления, страна, ...
from tour.in_test import OurToXXXReqConvertor

class OurReq():
    pass

class ExtReq():
    pass

our_req = OurReq()

ext_req = ExtReq()


def __to_tour_objects(http_response):
    pass

def f(request):
    pass



convertor = OurToXXXReqConvertor()
request = convertor.our_req_to_dict(our_req, ext_req)

# f -- реализует передачу запроса и получение ответа
http_response = f(request)

# __to_tour_objects -- парсит ответ и возвращает массив объектов типа Tour
tours = __to_tour_objects(http_response)

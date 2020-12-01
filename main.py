import grpc
import addressbook_pb2
import addressbook_pb2_grpc
from concurrent import futures
import utils
import logging
import sys

def get_person(db, number):
    for item in db:
        for phone in item.phones:
            if phone.number == number.number:
                return item
    return None

def edit_person(db, new_person):
    edit = False
    index = 0
    for item in db:
        if item.id == new_person.id:
            edit = True
            break
        index = index + 1
    db[index] = new_person
    return edit

class RPCServiceServicer(addressbook_pb2_grpc.RPCServiceServicer):
    def __init__(self):
        self.db = utils.read_route_guide_database()

    def GetPersonByPhoneNumber(self, request, context):
        person = get_person(self.db, request)
        if person is None:
            return addressbook_pb2.Person()
        else:
            print("protobuf size: "+str(sys.getsizeof(person.SerializeToString())))
            return person

    def EditPeople(self, request_iterator, context):
        for request in request_iterator:
            res = edit_person(self.db, request)
            if not res:
                return addressbook_pb2.ResponseEdit(result=False)
        return addressbook_pb2.ResponseEdit(result=True)

    def ListPeopleByPhoneType(self, request, context):
        for item in self.db:
            for phone in item.phones:
                if phone.type == request.type:
                    yield item

    def GetPeopleById(self, request_iterator, context):
        people = []
        for request in request_iterator:
            for item in self.db:
                if item.id == request.id:
                    people.append(item)
                    yield item

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    addressbook_pb2_grpc.add_RPCServiceServicer_to_server(
        RPCServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Print all "Messages"(data points) and errors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# from garmin_fit_sdk import Decoder, Stream
#
# stream = Stream.from_file('/home/kevin/Downloads/21091110845/21091110845_ACTIVITY.fit')
# decoder = Decoder(stream)
# messages, errors = decoder.read()
#
# print(errors)
# print(messages)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Field Names for all messages ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from garmin_fit_sdk import Decoder, Stream, Profile

stream = Stream.from_file('/home/kevin/Downloads/21091110845/21091110845_ACTIVITY.fit')

decoder = Decoder(stream)

record_fields = set()
def mesg_listener(mesg_num, message):
    if mesg_num == Profile['mesg_num']['RECORD']:
        for field in message:
            record_fields.add(field)

messages, errors = decoder.read(mesg_listener = mesg_listener)

if len(errors) > 0:
    print(f"Something went wrong decoding the file: {errors}")
    # return

print(record_fields)
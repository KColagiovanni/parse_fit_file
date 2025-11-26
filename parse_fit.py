from garmin_fit_sdk import Decoder, Stream

stream = Stream.from_file('/home/kevin/Downloads/21091110845/21091110845_ACTIVITY.fit')
decoder = Decoder(stream)
messages, errors = decoder.read()

print(errors)
print(messages)
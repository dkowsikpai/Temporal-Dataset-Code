import string
import random
def id_generator(size=4, chars=string.ascii_uppercase):
   return ''.join(random.choice(chars) for _ in range(size))

for i in range(130):
   print(id_generator())
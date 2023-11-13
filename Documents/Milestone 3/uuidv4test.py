import uuid
import time

count = 0
start = time.time()
while count < 1000000:
    uuid.uuid4()
    count += 1
end = time.time()
print(f"The execution time for 1,000,000 uuid is: {end - start}")

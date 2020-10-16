import Master as M
import time
import Tag_Database as Tags
import matplotlib.pyplot as plt

Client = M.Make_Client('10.50.0.10')

times = list()

for _ in range(1000):

    start_time = time.time()

    Tag1= M.Read(Client, Tags.WF1H)

    M.Write(Client, Tags.WF1H, 0)

    times.append(1000*(time.time() - start_time))



plt.hist(times)
plt.xlabel('time (ms)')
plt.ylabel('counts')

plt.show()

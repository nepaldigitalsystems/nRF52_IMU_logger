import asyncio
from bleak import BleakScanner, BleakClient
import matplotlib.pyplot as plt


nordic_uuid = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

Ax= []
Avg_Ax= []
Ay= []
Avg_Ay= []
Az= []
Avg_Az= []
Gx= []
Avg_Gx = []
Gy= []
Avg_Gy = []
Gz= []
Avg_Gz = []

flagy = False
close_eventt = False

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(121, aspect='equal')
bx = fig.add_subplot(122, aspect='equal')

ax.set_title('Accelomerter')
bx.set_title('Gyroscope')

def handle_close(evt):
    global close_eventt
    close_eventt = True
    print('Closed Figure!')
fig.canvas.mpl_connect('close_event', handle_close)



def mov_average(Ax,Ay,Az,Gx,Gy,Gz): 
    global Avg_Ax, Avg_Ay, Avg_Az, Avg_Gx, Avg_Gy, Avg_Gz
    Avg_Ax = [Ax[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Ay = [Ay[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Az = [Az[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Gx = [Gx[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Gy = [Gy[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Gz = [Gz[x:x+10] for x in range(0,len(Ax),10)]
    Avg_Ax = [sorted(x) for x in Avg_Ax]
    Avg_Ay = [sorted(x) for x in Avg_Ay]
    Avg_Az = [sorted(x) for x in Avg_Az]
    Avg_Gx = [sorted(x) for x in Avg_Gx]
    Avg_Gy = [sorted(x) for x in Avg_Gy]
    Avg_Gz = [sorted(x) for x in Avg_Gz]

    Avg_Ax = [ sum(x[1:9])/8 for x in Avg_Ax]
    Avg_Ay = [ sum(x[1:9])/8 for x in Avg_Ay]
    Avg_Az = [ sum(x[1:9])/8 for x in Avg_Az]
    Avg_Gx = [ sum(x[1:9])/8 for x in Avg_Gx]
    Avg_Gy = [ sum(x[1:9])/8 for x in Avg_Gy]
    Avg_Gz = [ sum(x[1:9])/8 for x in Avg_Gz]

def callback(sender: int, data: bytearray):

    global flagy
    vals = data.decode('utf-8')
    val_list = vals.split()
    #print(val_list)
    Ax.append(eval(val_list[1])/16384)
    Ay.append(eval(val_list[3])/16384)
    Az.append(eval(val_list[5])/16384)
    Gx.append(eval(val_list[7])/131)
    Gy.append(eval(val_list[9])/131)
    Gz.append(eval(val_list[11])/131)
    if flagy == True:
        #print(len(Ax))
        Ax.pop(0)
        Gx.pop(0)
        Ay.pop(0)
        Gy.pop(0)
        Az.pop(0)
        Gz.pop(0)

        mov_average(Ax,Ay,Az,Gx,Gy,Gz)
        return

    if(len(Ax)>49):
        flagy = True

    #print(f"{sender}: {data}")


async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == "Nordic_UART":
            mydevice = d
            print("Found it")
        #print(d.address)
        #print(d.name)
        #print(type(d.name))
    

    async with BleakClient(mydevice.address) as client:
        svcs = await client.get_services()
  
        await client.start_notify(nordic_uuid, callback)
        while await client.is_connected():
            await asyncio.sleep(0.0000001)
            if close_eventt == True:
                break
           


            ax = fig.add_subplot(121)
            bx = fig.add_subplot(122)
            #ax.set_xlim((0, 50))
            #ax.set_ylim((0, 1000))
            X_axis = [i for i in range(len(Ax))]
            ax.set_title('Accelomerter')
            ax.plot(X_axis,Ax,label="Ax")
            ax.plot(X_axis,Ay,label="Ay")
            ax.plot(X_axis,Az,label="Az")
            ax.legend(loc="upper right")

            bx.set_title('Gyroscope')
            bx.plot(X_axis,Gx,label="Gx")
            bx.plot(X_axis,Gy,label="Gy")
            bx.plot(X_axis,Gz,label="Gz")
            bx.legend(loc="upper right")

            plt.show()
            plt.pause(0.01)
            plt.clf()

        #while True:
            #pass
        '''print("Services:")
        for service in svcs:
            print(service)'''


loop = asyncio.get_event_loop()
loop.run_until_complete(run())

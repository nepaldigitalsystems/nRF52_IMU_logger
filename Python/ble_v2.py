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
    Ax.sort()
    Ay.sort()
    Az.sort()
    Gx.sort()
    Gy.sort()
    Gz.sort()
    Avg_Ax.append(sum(Ax[7:43])/36)
    Avg_Ay.append(sum(Ay[7:43])/36)
    Avg_Az.append(sum(Az[7:43])/36)
    Avg_Gx.append(sum(Gx[7:43])/36)
    Avg_Gy.append(sum(Gy[7:43])/36)
    Avg_Gz.append(sum(Gz[7:43])/36)
    if(len(Avg_Ax)>50):
        Avg_Ax.pop(0)
        Avg_Ay.pop(0)
        Avg_Az.pop(0)
        Avg_Gx.pop(0)
        Avg_Gy.pop(0)
        Avg_Gz.pop(0)
        print("LEN OF avg" + str(len(Avg_Ax)))

    print(Avg_Ax)
    

def callback(sender: int, data: bytearray):
    global flagy
    vals = data.decode('utf-8')
    val_list = vals.split()
    Ax.append(eval(val_list[1])/16384)
    Ay.append(eval(val_list[3])/16384)
    Az.append(eval(val_list[5])/16384)
    Gx.append(eval(val_list[7])/131)
    Gy.append(eval(val_list[9])/131)
    Gz.append(eval(val_list[11])/131)
    if flagy == True:

        Ax.pop(0)
        Gx.pop(0)
        Ay.pop(0)
        Gy.pop(0)
        Az.pop(0)
        Gz.pop(0)
        
        mov_average(Ax[:],Ay[:],Az[:],Gx[:],Gy[:],Gz[:])
        return

    if(len(Ax)>49):
        flagy = True



async def run():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == "Nordic_UART":
            mydevice = d
            print("Found it")


    async with BleakClient(mydevice.address) as client:
        svcs = await client.get_services()
        '''val = await client.read_gatt_char(nordic_uuid)
        print(val)
        print(int.from_bytes(val,byteorder='big'))'''

        
        await client.start_notify(nordic_uuid, callback)
        while await client.is_connected():
            await asyncio.sleep(0.0000001)
            if close_eventt == True:
                break
         
            if flagy==True:
                ax = fig.add_subplot(121)
                bx = fig.add_subplot(122)

                X_axis = [i for i in range(len(Avg_Ax))]
                ax.set_title('Accelomerter')
                ax.plot(X_axis,Avg_Ax,label="Ax")
                ax.plot(X_axis,Avg_Ay,label="Ay")
                ax.plot(X_axis,Avg_Az,label="Az")
                ax.legend(loc="upper right")

                bx.set_title('Gyroscope')
                bx.plot(X_axis,Avg_Gx,label="Gx")
                bx.plot(X_axis,Avg_Gy,label="Gy")
                bx.plot(X_axis,Avg_Gz,label="Gz")
                bx.legend(loc="upper right")

                plt.show()
                plt.pause(0.01)
                plt.clf()



loop = asyncio.get_event_loop()
loop.run_until_complete(run())
#loop.run_until_complete(main())
# 1.定义一个函数recv_from_up从上位机接收数据，然后调用函数send_to_car将数据转发给小车
# 2.定义一个函数recv_from_car从小车接收数据，然后调用函数send_to_up将数据发给上位机
# 3.定义函数send_to_car
# 4.定义函数send_to_up
# 5.建立线程t1 = threading.Thread(target = recv_from_up)
# 6.建立线程t1 = threading.Thread(target = recv_from_car)


import socket
import time       # 可以用来得到时间戳
import threading   #同时执行多任务
import struct



def main():

    # 定义写入log事件的方法
    def writelog(log_data):
        # 获取当前时间（含毫秒）
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s.%03d" % (data_head, data_secs)

        with open("log.txt","a") as file1:
            file1.write(time_stamp + ":" + log_data + '\n')  # with open方法就不需要每次调用.close方法
            print("成功写入数据")



#  ===========================定义数据接收函数并调用数据发送函数=======================
    def recv_from_up():
        global ip_Ali
        global port_up
        global tcp_server_up
        global  client_up
        print("从上位机接收数据为：")

        tcp_server_up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_up.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
        # ip_Ali = input("请输入阿里云的公网ip"+"\n") # 服务器的ip地址
        ip_Ali = "47.102.36.187"  # 服务器的ip地址
        # port_up = input("请输入与上位机联通的端口:")  # 服务器的端口号
        port_up = 8082  # 接通上位机的端口号
        tcp_server_up.bind(("0", 8082 ))
        tcp_server_up.listen(128)
        flag = True

        while True:  # 在子类中重写run方法，建立与客户端的链接、通信
            print("开启监听线程,等待客户端链接")  # 开始监听是否有客户端链接该服务器
            # flag = True
            client_up, cltadd_up = tcp_server_up.accept()  # 检测到有客户端链接成功，建立一个新的服务器套接字与客户端通信，以及连接的客户端的地址
            print('监听到wifi连接')
            time.sleep(0.5)
            # while True:
            i = 0  # 记录发送次数

            while True:
                # data_from_up = client_up.recv(1024).decode('utf-8')  # 接收客户端发送的数据进行解码
                # data_from_up = client_up.recv(1024)  # 接收客户端发送的数据进行解码

                #=================写入log文档
                # 1、解码如果判为上位机上发的经纬度数据，则写入文档：time: 上位机上发经纬度数据
                # 2、解码如果判为上位机上发的请求状态数据的指令，则写入文档：time: 上位机上发请求状态数据的指令
                # 3、解码如果判为上位机上发的请求图像数据的指令，则写入文档：time: 上位机上发请求图像数据的指令
                # 4、分三种情况写send_to_car,每种情况后写入文档：time: 向下位机发送......
                while True:

                    data_from_up1 = client_up.recv(1)  # 接收客户端发送的数据进行解码
                    print("逐个读取字节")
                    try:
                        m1 = struct.unpack('B',data_from_up1)
                    except:
                        print("解析包头错误")
                    if (m1 == (255,)):  # 如果读到包头则一次性读完包头
                        data_from_up2 = client_car.recv(3)
                        break

                data_from_up3 = client_car.recv(20)
                try:
                    x5, x6, x7, x8, x9 = struct.unpack('5i', data_from_up3)  # x5:包长x6：包序号 x7:时间戳 x8:数据域1 x9:数据域2
                except:
                    print("解析前缀信息错误")

                if (x8 ==1):
                    # 上位机下发经纬度数据
                    data_from_up_lnglat = client_car.recv(1024)
                    log1 = "收到上位机要传给下位机的未来经纬度序列"
                    writelog(log1)  # 写入事件

                    data_from_up = data_from_up1 + data_from_up2 + data_from_up3 + data_from_up_lnglat
                    send_to_car(data_from_up)  # 将数据转发
                    log2 ="将上位机发送的未来经纬度序列传输给下位机"
                    writelog(log2)
                    print("成功转发经纬度给小车")

                if (x8 == 2):
                    # 请求上发状态数据
                    data_from_up_state = client_car.recv(1024)
                    log3 = "收到上位机要传给下位机的请求状态指令"
                    writelog(log3)  # 写入事件

                    data_from_up = data_from_up1 + data_from_up2 + data_from_up3 + data_from_up_state
                    send_to_car(data_from_up)  # 将数据转发
                    log4 = "将上位机发送的请求状态指令传输给下位机"
                    writelog(log4)
                    print("成功转发状态请求指令给小车")

                if (x8 == 3):
                    # 请求上发图像数据
                    data_from_up_image = client_car.recv(1024)
                    log5 = "收到上位机要传给下位机的请求图像指令"
                    writelog(log5)  # 写入事件

                    data_from_up = data_from_up1 + data_from_up2 + data_from_up3 + data_from_up_image
                    send_to_car(data_from_up)  # 将数据转发
                    log6 = "将上位机发送的请求图像指令传输给下位机"
                    writelog(log6)
                    print("成功转发图像请求指令给小车")



                #=================写入log文档

                print("客户端发送的数据是：", data_from_up)
                # if data:  # 如果收到的数据不为空，表示客户端仍在请求服务，继续为其服务
                if data_from_up:
                    send_to_car(data_from_up)  # 将数据转发
                    print("成功转发给小车")
                    # break
                else:
                    break


    def recv_from_car():
        global ip_Ali
        global port_car  # 与小车接通的端口
        global tcp_server_car
        global client_car
        print("从小车接收数据为：")

        tcp_server_car = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_car.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用

        # ip_Ali = input("请输入阿里云的公网ip")  # 服务器的ip地址
        # port_car = input("请输入与小车联通的端口:")  # 服务器的端口号
        port_car = 8083  # 与小车接通的端口号
        tcp_server_car.bind(("0", 8083))
        tcp_server_car.listen(128)
        flag = True

        while True:  # 在子类中重写run方法，建立与客户端的链接、通信
            print("开启监听线程,等待客户端链接")  # 开始监听是否有客户端链接该服务器
            # flag = True
            client_car, cltadd_car = tcp_server_car.accept()  # 检测到有客户端链接成功，建立一个新的服务器套接字与客户端通信，以及连接的客户端的地址
            print('监听到wifi连接')
            time.sleep(0.5)
            # while True:
            i = 0  # 记录发送次数
            while True:

                while True:

                    dataFromCar1 = client_car.recv(1)  # 接收客户端发送的数据进行解码
                    print("逐个读取字节")
                    try:
                        z1 = struct.unpack('B',dataFromCar1)
                    except:
                        print("解析包头错误")
                    if (z1 == (221,)):  # 如果读到包头则一次性读完包头
                        dataFromCar2 = client_car.recv(3)
                        break

                dataFromCar3 = client_car.recv(24)
                try:
                    x5, x6, x7, x8, x9, x10 = struct.unpack('6i', dataFromCar3)
                except:
                    print("解析前缀信息错误")

                if (x9 == 3):  # 如果上传数据字节数过多，则为图像信息
                    print("上传的是图像数据")
                    data_image1 = client_car.recv(1)
                    try:
                        image_geshi = struct.unpack('B', data_image1)
                    except:
                        print("解析图像格式错误")
                    # print("图像格式为：", image_geshi)
                    data_image2 = client_car.recv(4)
                    try:
                        image_len = struct.unpack('1i', data_image2)
                    except:
                        print("解析图像字节数错误")
                    # print("图像字节数：", image_len)
                    image_msg = b''
                    len1 = int(image_len[0])
                    image_length = len1  # 图像数据的字节长度
                    while (len1 > 0):
                        if len1 > 1024:  # 如果剩余图像字节数大于1024
                            buffer = client_car.recv(1024)
                            image_msg += buffer  # image_msg中储存的是读取的累加的图像数据
                            len1 = len1 - 1024
                        else:
                            buffer = client_car.recv(len1)
                            image_msg += buffer
                            break


                    tianchong_num = image_length % 4  # 计算填充的字节数
                    shengyu_num = tianchong_num + 16  # 剩下要读的字节数
                    data_image_shengyu  = client_car.recv(shengyu_num)

                    data_from_car =dataFromCar1 + dataFromCar2 + dataFromCar3 + data_image1 + data_image2 + image_msg +data_image_shengyu
                    log7 = "收到下位机上传的图像数据"
                    writelog(log7)  # 写入事件

                    send_to_up(data_from_car)  # 将图像数据转发
                    log8 = "将下位机上传的图像数据发送给上位机"
                    writelog(log8)  # 写入事件



                elif (x9 == 0):
                    print("上传的是无效数据")

                elif ( x9 == 1):
                    print("上传的是状态数据")
                    dataFromCar_state = client_car.recv(40)
                    data_from_car = dataFromCar1 + dataFromCar2 + dataFromCar3 + dataFromCar_state
                    log9 = "收到下位机上传的状态数据"
                    writelog(log9)  # 写入事件

                    send_to_up(data_from_car)
                    log10 = "将下位机上传的状态数据发送给上位机"
                    writelog(log10)  # 写入事件


                elif (x9 == 2):
                    print("上传的是经纬度数据")
                    dataFromCar_lnglat = client_car.recv(36)
                    data_from_car = dataFromCar1 + dataFromCar2 + dataFromCar3 + dataFromCar_lnglat
                    log11 = "收到下位机上传的小车当前时刻经纬度数据"
                    writelog(log11)  # 写入事件

                    send_to_up(data_from_car)
                    log12 = "将下位机上传的小车当前时刻经纬度数据发送给上位机"
                    writelog(log12)  # 写入事件


                else:
                    print("数据上发错误")
                    # break
#  ===========================定义数据接收函数并调用数据发送函数=======================

# =======================================定义数据发送函数======================================
    def send_to_up(data_from_car):
        print("发送给上位机的数据为：",data_from_car)
        global tcp_server_up
        global client_up
        flag = True

        while True:  # 在子类中重写run方法，建立与客户端的链接、通信
            data_to_up = "1111111"
            # client_up.send(data_to_up.encode("utf-8"))  # 向下位机发送数据包
            client_up.send(data_from_car)  # 向下位机发送数据包
            break

    def send_to_car(data_from_up):
        print("发送给小车的数据为：",data_from_up)
        global tcp_server_car
        global client_car
        flag = True
        # -----------------------------------------------------------------------------------------------
        while True:  # 在子类中重写run方法，建立与客户端的链接、通信
            data_to_car = "2222222"
            # client_car.send(data_to_car.encode("utf-8"))  # 向下位机发送数据包
            client_car.send(data_from_up)  # 向下位机发送数据包
            break
# =======================================定义数据发送函数======================================

# =========================================建立两个线程========================================
    t1 = threading.Thread(target=recv_from_up)
    t2 = threading.Thread(target=recv_from_car)
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    tcp_server_up.close()
    tcp_server_car.close()



if __name__ == "__main__":
    main()

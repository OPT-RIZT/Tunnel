from queue import Queue,LifoQueue,PriorityQueue
import sys

order_dict = {'测量':'%R1Q,50013:2' , '旋转':'%R1Q,50003:0,0,0,0,0,0,0' , '搜索':'%R1Q,9029:0.2618,0.2618,0','查询':'%R1Q,2003:0'}
order_list = Queue(maxsize=11)

order_list.put(order_dict['查询'])
order_list.put(order_dict['搜索'])
order_list.put(order_dict['测量'])
order_list.put(order_dict['旋转'])

print(order_list.queue[3][5:10])
print(order_list.queue)

if order_list.queue[3][5:10] == '50003':
    print(34)
print(order_list.get())
print(order_list.queue)
from flask import Flask, render_template, session, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from threading import Lock
import random

###########################
#########CONFIG############
###########################

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = '5dec1cfe7c0c2ec55c17fb44b43f7d14'
socket_ = SocketIO(app, async_mode=async_mode)

insThread = None
ins_thread_lock = Lock()
selThread = None
sel_thread_lock = Lock()
qckThread = None
qck_thread_lock = Lock()
hepThread = None
hep_thread_lock = Lock()
radThread = None
rad_thread_lock = Lock()

def insertion_sort(array, speed):
    global insThread       

    for step in range(1, len(array)):
        key = array[step]
        j = step  
        while j > 0 and array[j-1]>key:
            socket_.sleep(speed)
            socket_.emit('ins',{'data':{'algorithm':'insertion', 'array':array, 'step':step+1, 'compare':j}}, namespace='/sort')
            array[j] = array[j-1]
            j = j - 1
        array[j] = key
    socket_.sleep(speed)
    socket_.emit('ins',{'data':{'algorithm':'insertion', 'array':array, 'step':-1, 'compare':-1}}, namespace='/sort')
    insThread=None

def partition(array, low, high, speed):
  pivot = array[high]

  i = low - 1

  for j in range(low, high):
    socket_.emit('quick',{'data':{'algorithm':'quick', 'array':array}}, namespace='/sort')
    if array[j] <= pivot:
      i = i + 1
      socket_.emit('quick',{'data':{'algorithm':'quick', 'array':array}}, namespace='/sort')
      (array[i], array[j]) = (array[j], array[i])
    socket_.emit('quick',{'data':{'algorithm':'quick', 'array':array}}, namespace='/sort')

  (array[i + 1], array[high]) = (array[high], array[i + 1])
  socket_.sleep(speed)
  socket_.emit('quick',{'data':{'algorithm':'quick', 'array':array}}, namespace='/sort')

  return i + 1

def quickSort(array, low, high, speed):
  if low < high:
    pi = partition(array, low, high, speed)
    quickSort(array, low, pi - 1, speed)
    quickSort(array, pi + 1, high, speed)

def quick_sort(array, speed):
    global qckThread
    quickSort(array, 0, len(array)-1, speed)
    qckThread=None

def selection_sort(array, speed):
    global selThread

    for i in range(len(array)):
        bigindex=0
        for j in range(len(array)-i):
            socket_.sleep(speed)
            socket_.emit('sel',{'data':{'algorithm':'selection', 'array':array, 'step':bigindex, 'compare':j}}, namespace='/sort')
            if array[j]>array[bigindex]:
                bigindex=j
            
        array[bigindex], array[len(array)-i-1]=array[len(array)-i-1], array[bigindex]
        #socket_.sleep(speed)
        #socket_.emit('sel',{'data':{'algorithm':'selection', 'array':array, 'step':bigindex, 'compare':len(array)-i-1}}, namespace='/sort')
    socket_.sleep(speed)
    socket_.emit('sel',{'data':{'algorithm':'selection', 'array':array, 'step':-1, 'compare':-1}}, namespace='/sort')
    selThread=None

def heapify(arr, n, i, speed):
    # Find largest among root and children
      largest = i
      l = 2 * i + 1
      r = 2 * i + 2
  
      if l < n and arr[i] < arr[l]:
          largest = l
  
      if r < n and arr[largest] < arr[r]:
          largest = r

      # If root is not largest, swap with largest and continue heapifying
      if largest != i:
          arr[i], arr[largest] = arr[largest], arr[i]
          socket_.sleep(speed)
          socket_.emit('heap',{'data':{'algorithm':'heap', 'array':arr}}, namespace='/sort')
          heapify(arr, n, largest, speed)

def heap_sort(arr, speed):
      global hepThread
      n = len(arr)
  
      # Build max heap
      for i in range(n//2, -1, -1):
          socket_.emit('heap',{'data':{'algorithm':'heap', 'array':arr}}, namespace='/sort')
          heapify(arr, n, i, speed)
          socket_.emit('heap',{'data':{'algorithm':'heap', 'array':arr}}, namespace='/sort')
  
      for i in range(n-1, 0, -1):
          # Swap
          arr[i], arr[0] = arr[0], arr[i]
  
          # Heapify root element
          socket_.emit('heap',{'data':{'algorithm':'heap', 'array':arr}}, namespace='/sort')
          heapify(arr, i, 0, speed)
          socket_.emit('heap',{'data':{'algorithm':'heap', 'array':arr}}, namespace='/sort')
      hepThread=None

def radix_sort(nums, speed):
    global radThread
    RADIX=10
    placement=1
    max_digit=max(nums)
    while placement<max_digit:
        buckets=[list() for _ in range(RADIX)]
        tempArr={}
        for i in range(len(nums)):
            tempArr[i]=nums[i]
        for i in range(len(nums)):
            tmp=int((nums[i]/placement)%RADIX)
            arr=[j for j in tempArr.values()]
            for b in buckets:
                arr.extend(b)
            socket_.sleep(speed)
            socket_.emit('radix',{'data':{'algorithm':'radix', 'array':arr}}, namespace='/sort')
            buckets[tmp].append(nums[i])

            del tempArr[i]

        a=0
        for b in range(RADIX):
            buck=buckets[b]
            for i in buck:
                nums[a]=i
                a+=1
        placement*=RADIX
        socket_.emit('radix',{'data':{'algorithm':'radix', 'array':nums}}, namespace='/sort')
    radThread=None

###########################
#########ROUTES############
###########################

@app.route('/')
def index():
    return render_template('index.html', async_mode=socket_.async_mode)

###########################
#########SOCKETS###########
###########################

@socket_.on('insertion', namespace='/sort')
def insertion(data):
    message=data['data']
    global insThread
    with ins_thread_lock:
        if insThread is None:
            arr=arr=random.sample(range(message['min'], message['max']), message['max']-message['min'])#[i for i in range(message['max'], message['min']-1, -1)]

            insThread = socket_.start_background_task(insertion_sort, arr, message['speed'])
    emit('logging', {'data': 'Starting insertion sort'})

@socket_.on('selection', namespace='/sort')
def selection(data):
    message=data['data']
    global selThread
    with sel_thread_lock:
        if selThread is None:
            arr=arr=random.sample(range(message['min'], message['max']), message['max']-message['min'])#[i for i in range(message['max'], message['min']-1, -1)]

            selThread = socket_.start_background_task(selection_sort, arr, message['speed'])
    emit('logging', {'data': 'Starting selection sort'})

@socket_.on('quick', namespace='/sort')
def quick(data):
    message=data['data']
    global qckThread
    with qck_thread_lock:
        if qckThread is None:
            arr=arr=random.sample(range(message['min'], message['max']), message['max']-message['min'])#[i for i in range(message['max'], message['min']-1, -1)]

            qckThread = socket_.start_background_task(quick_sort, arr, message['speed'])
    emit('logging', {'data': 'Starting quick sort'})

@socket_.on('heap', namespace='/sort')
def heap(data):
    message=data['data']
    global hepThread
    with hep_thread_lock:
        if hepThread is None:
            arr=random.sample(range(message['min'], message['max']), message['max']-message['min'])#[i for i in range(message['max'], message['min']-1, -1)]
            hepThread = socket_.start_background_task(heap_sort, arr, message['speed'])
    emit('logging', {'data': 'Starting heap sort'})

@socket_.on('radix', namespace='/sort')
def radix(data):
    message=data['data']
    global radThread
    with rad_thread_lock:
        if radThread is None:
            arr=random.sample(range(message['min'], message['max']), message['max']-message['min'])#[i for i in range(message['max'], message['min']-1, -1)]
            radThread = socket_.start_background_task(radix_sort, arr, message['speed'])
    emit('logging', {'data': 'Starting heap sort'})

if __name__ == '__main__':
    socket_.run(app, debug=True)
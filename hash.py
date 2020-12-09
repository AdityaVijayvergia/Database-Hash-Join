import random 
# used only for generating one single random number between 2 values

MEMORY_SIZE = 15

class Tuple:
    def __init__(self,data = [], key = 0):
        self.data = data
        self.key = key
    
    def __str__(self):
        return 'Tuple:' + str(self.data)
    
    def __repr__(self):
        return 'Tuple:' + str(self.data)

class Block:
    def __init__(self, data=[]):
        self.max_size = 8
        self.data = data
        self.next = None

    def add(self, tuple):
        self.data.append(tuple)

    def __str__(self):
        return 'Block:' + str(self.data) + ' next='+str(self.next)
    
    def __repr__(self):
        return '\nBlock:' + str(self.data) + ' next='+str(self.next)

class Memory:
    def __init__(self):
        self.max_size = MEMORY_SIZE
        self.data = []

    def add_data(self, data):
        pos = len(self.data)
        self.data += [data]
        return pos 

    def add_data_multiple(self, data):
        pos = len(self.data)
        self.data += data
        return pos, len(self.data)

    def clear(self):
        self.data = []


    def __str__(self):
        return '\n____Memory____:\nsize='+str(len(self.data)) + '\n'+str(self.data)
    
    def __repr__(self):
        return '\n____Memory____:\nsize='+str(len(self.data)) + '\n'+str(self.data)

class Disk:
    def __init__(self):
        self.data = []

    def add_data(self, data):
        pos = len(self.data)
        self.data += [data]
        return pos 
    
    def add_data_multiple(self, data):
        pos = len(self.data)
        self.data += data
        return pos, len(self.data)

    def __str__(self):
        p = '\n'

        for i,d in enumerate(self.data):
            p+=str(i)+' '+str(d)+'\n'

        return '\n\n____Disk____:'+p
    
    def __repr__(self):
        self.__str__()

def data_generation(size = 5000, low = 10000, high = 50000, get_used = False, duplicates_allowed=False):
    used = []
    blocks = []
    block = Block([])
    while len(used)<size:
        no = random.randint(low, high)
        if no not in used or duplicates_allowed:
            tuple = Tuple([no, random.randint(low, high)])
            used.append(no)
            if len(block.data) >= block.max_size:
                blocks.append(block)
                block = Block([tuple])
            else:
                block.add(tuple)
    
    if len(block.data)>0:
        blocks.append(block)
    # print(relation)
    if get_used:
        return blocks, used
    return blocks


def data_generation_from_s(size, s_used, low=0, high=5000, get_used=False):
    used = []
    blocks = []
    block = Block([])
    while len(used)<size:
        no = random.randint(low, high-1)
        tuple = Tuple([random.randint(low, high-1), s_used[no]])
        used.append(s_used[no])
        if len(block.data) >= block.max_size:
            blocks.append(block)
            block = Block([tuple])
        else:
            block.add(tuple)
    
    if len(block.data)>0:
        blocks.append(block)
    # print(relation)
    if get_used:
        return blocks, used
    return blocks

def read_disk_to_memory(idx, disk, memory):
    if len(idx) > 8:
        return 'fail'
    start = None
    for i in idx:
        p =  memory.add_data(disk.data[i])
        if start==None:
           start = p
        end = p+1
    return start, end

def write_memory_to_disk(idx, disk, memory):
    start = None
    for i in idx:
        p = disk.add_data(memory.data[i])
        if start==None:
            start = p
        end = p+1
    return start, end

def get_hash(value):
    return value% (MEMORY_SIZE-1)


def hash_data(disk, memory, start, end, idx=0):

    memory.clear()

    for i in range(MEMORY_SIZE-1):
        memory.data.append(Block([]))


    pos_arr = {}
    pos = start

    while pos<end:
        # print(pos)
        midx, _ = read_disk_to_memory([pos],disk, memory)
        # print(memory)

        for t in memory.data[midx].data:
            # print(t)
            hash = get_hash(t.data[idx])    
            hash_block = memory.data[hash]
            # print(hash_block.max_size, len(hash_block.data))
            if len(hash_block.data)>=hash_block.max_size:
                disk_pos,_ = write_memory_to_disk([hash], disk, memory)
                # print('added new at',t)
                memory.data[hash] = Block([])
                memory.data[hash].next = disk_pos
                pos_arr[hash] = disk_pos
                hash_block = memory.data[hash]
            hash_block.data.append(t)
        

        memory.data.pop(MEMORY_SIZE-1)
        pos+=1
    

    for i in range(MEMORY_SIZE-1):
        if len(memory.data[i].data)>0:
            pos,_ = write_memory_to_disk([i],disk, memory)
            pos_arr[i] = pos
        elif memory.data[i].next!=None:
            pos_arr[i] = memory.data[i].next
    
    return pos_arr


def search(memory, start, end, k):
    p = start
    while p<end:
        block = memory.data[p]
        for t in block.data:
            key = t.data[0]
            if k==key:
                return t
        p+=1
    return None


def join(a, b, disk, memory):
    memory.clear()
    match_list = []
    print('\n\n______natural join:______')

    for ax in a:
        if ax not in b:
            continue
        # ax = bucket index
        start = 0
        ai = a[ax]
        # ai = bucket
        mem_pos,_ = read_disk_to_memory([ai], disk, memory)
        
        current_block = memory.data[mem_pos]
        while current_block.next!=None:
            mem_pos,_ = read_disk_to_memory([current_block.next], disk, memory)
            current_block = memory.data[mem_pos]

        end = len(memory.data)

        # ai bucket loaded in memory

        bi = b[ax]

        mem_pos,_ = read_disk_to_memory([bi], disk, memory)
        current_block = memory.data[mem_pos]

        while current_block:

            for t in current_block.data:
                match = search(memory, start, end, t.data[1])
                # print('_______]', t)
                if match!=None:
                    # print('match found:', [t.data[0]] + match.data)
                    match_list.append([t.data[0]] + match.data)
            
            if current_block.next == None:
                break
            mem_pos,_ = read_disk_to_memory([current_block.next], disk, memory)
            current_block = memory.data[mem_pos]
            
        


        memory.clear()
    return match_list
        # print(memory, start, end, ax)
        # break
    # print('_________________________')


def test():
    disk = Disk()
    memory = Memory()
    s = data_generation(5,0,5)
    print('\n\nS=',s)
    s, s_end = disk.add_data_multiple(s)

    r = data_generation(5,0,5)
    print('\n\nR=',r)
    r, r_end = disk.add_data_multiple(r)

    s = hash_data(disk, memory, s, s_end)
    r = hash_data(disk, memory, r, r_end, 1)

    print(disk, s, r)

    join(s,r,disk,memory)




disk = Disk()
memory = Memory()

# part 5.1===============================================================
s, keys = data_generation(5000, get_used=True)
disk_io = 0
# print('disk io for reading S', len(s))
disk_io += 3*len(s)
disk_io2 = disk_io
# print('\n\nS=',s)
s, s_end = disk.add_data_multiple(s)

r, r_keys = data_generation_from_s(1000, s_used = keys, high = len(keys), get_used=True)
# print('\n\nR=',r)
disk_io += 3*len(r)
r, r_end = disk.add_data_multiple(r)

# print('disk io for reading R', len(r))

s = hash_data(disk, memory, s, s_end)
r = hash_data(disk, memory, r, r_end, 1)

# print(disk, s, r)

rs_join = join(s,r,disk,memory)

for _ in range(20):
    no = random.randint(0, len(r_keys)-1)
    no = r_keys[no]
    # print(no)
    for row in rs_join:
        if row[1] == no:
            print(row)

print('\n\n____________________disk io=',disk_io)
# part5.2===================================================================\

r = data_generation(size = 1200, low=20000, high = 30000, duplicates_allowed=True)
disk_io2 += 3*len(r)
r, r_end = disk.add_data_multiple(r)
r = hash_data(disk, memory, r, r_end, 1)
rs_join = join(s,r,disk,memory)
print(rs_join)

print('\n\n____________________disk io=',disk_io2)

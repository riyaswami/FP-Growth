import itertools    # to create all the subsets 
import os           # to check file path
import time         # to compute time taken
import graphviz     # to draw the tree
import threading    # to use multi-threading


# sorting using nlogn
def heapify(arr, keys, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    if l < n and arr[i] > arr[l]:
        largest = l
    if r < n and arr[largest] > arr[r]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        keys[i], keys[largest] = keys[largest], keys[i]
        heapify(arr, keys, n, largest)

def heapSort(keys, arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, keys, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        keys[i], keys[0] = keys[0], keys[i]  # swap
        heapify(arr, keys, i, 0)
    return keys, arr

class Data:     # read data from text file
    def __init__(self, f):
        self.file = open(f, "r")  # 
        self.__items = {}   # item with frequencies(private)
        self.tcount = 0     # no. of transactions
        self.__trans = []   # all the transactions
        self.read_file()

    def read_file(self):    # reads the text file and save transaction in "trans"
        for l in self.file:
            self.tcount += 1
            all_items = l.split()
            temp = []
            for i in all_items:
                if(i not in temp):
                    temp.append(i)
                    if i not in self.__items.keys():    # Unique elements in each in transaction
                        self.__items[i] = 1
                    else:
                        self.__items[i] += 1
            self.__trans.append(temp)

    def get_trans(self):    # return transaction list
        return self.__trans

    def get_count_all_items(self):  # return items dictionary with freq
        return self.__items


    def display(self):
        print(self.__items)
        print("No. of Transactions:", self.tcount)
        print("Transactions", self.__trans)


class Node:         #represent node of the tree

    def __init__(self, n=0, link=None):
        self.item = n   # name of item
        self.count = 0  # count to be calculated while creating the tree
        self.children = {}  # dictionary of the all the children
        self.link = link  # link to nodes of same item
        self.parent = None  #to be used for linking the frequency table to the tree



class FPGrowth:
    def __init__(self, rd, msup, mconf):
        self.root = Node(None)  #blank node
        self.msup = (msup/100)*rd.tcount  #minimum support
        self.mconf = mconf    #minimum confidence
        self.create_tree(rd)

    def add(self, sort_trans):      # add nodes to the fp tree 
        for i in sort_trans:
            new = Node(i[0])
            new.count = 1
            if i[0] not in self.root.children.keys():
                self.root.children[i[0]] = new
            else:
                self.root.children[i[0]].count += 1
            curr_node = self.root
            for j in range(0, len(i)-1):
                name = i[j+1]
                new = Node(name)
                new.count = 1
                new.parent = curr_node.children[i[j]]
                if i[j+1] not in curr_node.children[i[j]].children:
                    curr_node.children[i[j]].children[i[j + 1]] = new
                else:
                    curr_node.children[i[j]].children[i[j + 1]].count += 1
                curr_node = curr_node.children[i[j]]

    def add_freq_tree(self, sort_trans, root):  # add nodes to component conditional fp trees
        for i in sort_trans:
            new = Node(i[0])
            new.count = i[len(i)-1]
            if i[0] not in root.children.keys():
                root.children[i[0]] = new
            else:
                root.children[i[0]].count += i[len(i)-1]
            curr_node = root
            for j in range(0, len(i)-2):
                name = i[j+1]
                new = Node(name)
                new.parent = curr_node.children[i[j]]
                if i[j+1] not in curr_node.children[i[j]].children:
                    new.count = i[len(i)-1]
                    curr_node.children[i[j]].children[i[j + 1]] = new
                else:
                    curr_node.children[i[j]].children[i[j + 1]].count += i[len(i)-1]
                curr_node = curr_node.children[i[j]]
        return root

    def print_bfs(self, node):      # prints bfs traversal and returns path
        print("~~~~~~~~~~~ BFS ~~~~~~~~~~~~~")
        path = []
        queue = []
        i = 0
        queue.append(node)
        while(len(queue) != 0):
            node = queue[i]
            del queue[i]
            arr = list(node.children.keys())
            for j in range(len(arr)):
                queue.append(node.children[arr[j]])
            path.append(node)
            print(node.item, node.count,end = ' ')
            if(node.parent is not None):
                print("child of: [", node.parent.item , node.parent.count,']')
            elif(node.item is not None):
                print ("child of root")
            else:
                print()
        return path

    def print_digraph(self, node, tname):   # create fp tree visualization
        stack = [(node,"NULL")]
        tree = graphviz.Digraph(comment = "FP Growth")
        l = {}
        tree.node('NULL',shape = "circle", color = 'lightblue2', style ='filled')
        while (len(stack) != 0):
            s = stack.pop()
            for i in s[0].children.keys():
                name = i+"#"+str(s[0].children[i].count)
                if(('\t"'+name+'"') in tree.body):
                    l[name]+=1
                    name+="_"+str(l[name])
                else:
                  l[name] = 1
                tree.node(name)   
                if(s[0].item == None):
                  tree.edge('NULL', name)
                else:
                  tree.edge(s[1],name)
                stack.append((s[0].children[i],name))
        tree.attr(label=r'Frequent Pattern Tree ')
        tree.attr(fontsize='20')
        #tree.attr('node', shape='circle', style='filled', color='gray')
        tree.view()
        tree.render('/content/drive/MyDrive/Project_fp/'+tname, view=True)


    def print_digraph_cond_tree(self, node, tname):   # create conditional fp tree visualization
        stack = [(node,"NULL")]     # here nodes are references
        tree = graphviz.Digraph(comment = "FP Growth")
        l = {}
        tree.node('NULL',shape = "circle", color = 'lightblue2', style ='filled')
        while (len(stack) != 0):
            s = stack.pop()
            for i in s[0].children.keys():
                name = i.item+"#"+str(s[0].children[i].count)
                if(s[0].children[i].count >= self.msup):
                  if(('\t"'+name+'"') in tree.body):
                    l[name]+=1
                    name+="_"+str(l[name])
                  else:
                    l[name] = 1
                  tree.node(name)   
                  if (s[0].item is not None and s[0].item.item == None):
                    tree.edge('NULL', name)
                  else:
                    tree.edge(s[1],name)
                stack.append((s[0].children[i],name))
        if( len(tree.body)>1):
          tree.attr(label=r' Conditional Frequent Pattern Tree for '+tname)
          tree.attr(fontsize='20')
          tree.render('/content/drive/MyDrive/Project_fp/'+tname, view=True)

    def print_dfs(self, node):        # dfs traversal and returns path
        #print("~~~~~~~~~~~DFS~~~~~~~~~~~~~")
        path =[]
        stack = [node]
        while (len(stack) != 0):
            s = stack.pop()
            path.append(s)
            '''print(s.item, s.count, end=' ')
            if(s.parent is not None):
                print('child of [', s.parent.item, s.parent.count, ']')
            elif(s.item is not None):
                print('child of Root')'''
            for i in s.children.keys():
                stack.append(s.children[i])
        return path

    def remove_non_freq(self, keys, vals):    # selects frequent items 
        for i in range(len(keys)-1, -1, -1):
            if vals[i] < self.msup:
                del vals[i]
                del keys[i]
            else:
                break
        return keys, vals

    def sort_trans(self, rd, keys, vals):   # sort the transactions and prioritize them according to frequencies.
        trans = rd.get_trans()
        freq_item_trans = []
        for i in range(len(trans)):
            t = len(trans[i])
            temp = []
            freq=[]
            for j in range(t):
                if trans[i][j] in keys:
                    ind = keys.index(trans[i][j])
                    temp.append(trans[i][j])
                    freq.append(vals[ind])
            temp, freq = heapSort(temp, freq)
            for k in range(1, len(temp)):
                if(freq[k-1] == freq[k]):     # setting priority for items with same frequency
                    if(temp[k-1] > temp[k]):
                        temp[k-1], temp[k] = temp[k], temp[k-1]
            if(temp !=[]):
              freq_item_trans.append(temp)
        return freq_item_trans

   
    def create_link(self, keys, vals, path):   #create links between the nodes of same items
        items = {}
        for i in range(len(path)):          # traverse for every node in complete path
            j = i+1
            while (j<len(path)):
                if(path[i].item == path[j].item):
                    path[i].link = path[j]
                    i = j
                j += 1
        for i in range(0, len(keys)):     # connect to the freq table
            for j in path:
                if keys[i] == j.item:
                    items[keys[i]] = (vals[i],j)
                    break
        return items    # return it as a dictionary


    def cond_pattern_tree(self, cp):     # create conditional fp tree 
        items = []        
        for i in cp.keys():
            node = Node(None)
            node = self.add_freq_tree(cp[i], node)
            t = threading.Thread(target = self.print_digraph_cond_tree, args=(node,i))   # the fp tree visualisation is created and saved by a separate thread
            t.start() 
            path = self.print_dfs(node)
            temp = []
            for j in range(1, len(path)):     # select items according to min support using dfs path
                if(path[j].count >= self.msup):
                    temp.append(path[j])
            if(temp != []):
                temp.append(i)
                items.append(temp)
        return self.print_freq_itemset(items)

    def generate_association_rules(self, L, trans):     # print association rules
        print("\n---------------------ASSOCIATION RULES------------------")
        print("S.NO.\t\tRULES \t SUPPORT \t CONFIDENCE")
        print("--------------------------------------------------------\n")
        num = 1
        for l in L:                   # for every freq itemset
            length = len(l)
            count = 1
            while count < length:     # create all subsets 
                r = set(itertools.combinations(l, count))
                count += 1
                for item in r:
                    inc1 = 0
                    inc2 = 0
                    s = []
                    m = []
                    for i in item:
                        s.append(i)
                    for T in trans:     # check their presence in the original transactions
                        if set(s).issubset(set(T)) == True:   # count of antecedent
                            inc1 += 1
                        if set(l).issubset(set(T)) == True:   # count of antecedent intrsection consequent
                            inc2 += 1
                    try:
                      if 100 * inc2 / inc1 >= self.mconf:       # create rules if >= min confidence
                          for index in l:
                              if index not in s:
                                  m.append(index)
                          print("<%d> : %s ==> %s %d%% %d%%" % (num, s, m, 100 * inc2 / len(trans), 100 * inc2 / inc1))
                          num += 1
                    except:
                      pass

    def print_freq_itemset(self, path):   #create freq item sets using sets
        temp = []
        freq_items = set()
        for j in path:
            t = set()
            for i in j[:-1]:
                t.add(i.item.item)
            t.add(j[-1])
            temp.append(list(t))
        for i in temp:
            c = 1
            while c <= len(i):
                freq_items.update(set(itertools.combinations(i, c)))
                c += 1
        print("~~~~~~~~~~~~ Frequent Item Sets ~~~~~~~~~~", end='\n\n')
        new = []
        for item in freq_items:   # convert itemsets to lists
            a = list(item)
            print(a, end=' ')
            if len(item) > 1:
                new.append(a)
        print()
        return (new)


    def cond_pattern(self, link_dict, keys):  # select conditional patterns from the link table
        cond_pattern = {}
        for i in range(len(keys)-1,-1,-1):
            curr = link_dict[keys[i]][1]
            while(curr is not None):
                temp = curr.parent
                arr = []
                c = curr.count
                while(temp is not None):
                    arr.append(temp)
                    temp = temp.parent
                arr.reverse()
                if(arr == []):
                    pass
                else:
                    arr.append(c)
                    if( keys[i] not in cond_pattern):
                        cond_pattern[keys[i]] = [arr]
                    else:
                        cond_pattern[keys[i]].append(arr)
                curr = curr.link
        return (cond_pattern)

    def create_tree(self, rd):    # perform all the steps to create the tree one by one
        items = rd.get_count_all_items()
        keys, vals = heapSort(list(items.keys()), list(items.values()))
        #print(keys, vals)
        keys, vals = self.remove_non_freq(keys, vals)
        sort_trans = self.sort_trans(rd, keys, vals)
        #print(sort_trans)
        self.add(sort_trans)
        path = self.print_dfs(self.root)
        #self.print_digraph(self.root, 'tree')
        t = threading.Thread(target = self.print_digraph, args=(self.root,'tree'))   # the fp tree visualisation is created and saved by a separate thread
        t.start()       #time taken by total program is less when multithreading is used 
        link_dict = self.create_link(keys, vals, path)
        conditional_pattern = self.cond_pattern(link_dict, keys)
        new = self.cond_pattern_tree(conditional_pattern)
        self.generate_association_rules(new, rd.get_trans())


if __name__ == '__main__':
    path = input("Enter complete path for the text file: ")
    while not os.path.isfile(path):
        print("No such path exists.")
        path = input("Please enter a valid path: ")
    while "txt" not in path:
        print("Not a text file (no .txt found in name)")
        path = input("Please enter a valid path: ")
    read_data = Data(path)
    print('Number of Transactions:', read_data.tcount)
    temp = read_data.get_count_all_items()
    print('Unique Items:', temp.keys())
    print('Count of Items:', len(temp.keys()))
    print("Item Frequencies:", temp)
    print('Want to check frequency of any item??')
    ch = input('Enter (Y/N): ')
    while(ch == 'y' or ch == 'Y'):
        it = input('Enter Item name: ').lower()
        if(it not in temp.keys()):
            print('Item not found')
        else:
            print(it, ':', temp[it])
        ch = input('Enter \'N\' to exit.')
    print()
    min_sup =  int(input("Enter minimum support in %: "))
    min_conf = int(input("Enter minimum confidence in %: "))
    t1 = time.time()
    fp_tree = FPGrowth(read_data, min_sup, min_conf)
    t2 = time.time()
    print('time taken: ', t2 - t1, 's')

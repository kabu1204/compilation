class BuildFirst():
    def __init__(self,VT,VN,G):
        self.VT=VT
        self.VN=VN
        self.G=G
        self.V=VT+VN
        self.first={}
        self.Empty=[]
        for key in self.V:
            self.first.setdefault(key,[])
        self.SearchForCharToEmpty()
        self.build()

    def SearchForCharToEmpty(self):
        for key,value in self.G.items():
            for P in value:
                if P == ["$"]:
                    self.Empty.append(key)
                    break
        self.Empty=list(set(self.Empty))
        while 1:
            prev=len(self.Empty)
            for key,value in self.G.items():
                for P in value:
                    flag=1
                    for X in P:
                        if not X in self.Empty:
                            flag=0
                            break
                    if flag==1:
                        self.Empty.append(key)
                self.Empty=list(set(self.Empty))
            if len(self.Empty)==prev:
                self.Empty.sort()
                return

    def fst(self,ch):
        if len(ch)==1:
            return self.first[ch[0]].copy()
        else:
            res=[]
            for i in ch:
                if not "$" in self.first[i]:
                    res+=self.first[i]
                    res=list(set(res))
                    res.sort()
                    return res.copy()
                else:
                    res+=self.first[i]
                    res=list(set(res))
                    res.remove("$")
            res+=["$"]
            res.sort()
            return res.copy()

    def fst_(self,beta,a):
        t=self.fst(beta)
        if not "$" in t:
            t.sort()
            return t
        else:
            t.remove("$")
            res=t+a
            res.sort()
            return res


    def build(self):
        for X in self.VT:
            self.first[X]=[X]

        for key,value in self.G.items():
            for P in value:
                if P[0] in self.VT:
                    self.first[key].append(P[0])
                    self.first[key]=list(set(self.first[key]))

        flag=1
        while flag:
            flag=0
            for key,value in self.G.items():
                prev=len(self.first[key])
                for P in value:
                    self.first[key]+=self.fst(P)
                    self.first[key]=list(set(self.first[key]))
                if len(self.first[key])!=prev:
                    flag=1


class BuildFollow():
    def __init__(self,First,start="W!"):
        self.First=First
        self.VN=self.First.VN
        self.VT=self.First.VT
        self.V=self.First.V
        self.G=self.First.G
        self.start=start
        self.first=self.First.first
        self.Empty=self.First.Empty
        self.follow={}
        for X in VN:
            self.follow.setdefault(X,[])
        self.fl()

    def fl(self):
        self.follow[self.start].append("#")

        while 1:
            flag=1
            for key,value in self.G.items():
                for P in value:
                    for i,X in enumerate(P):
                        if X in self.VT:
                            continue
                        prev=len(self.follow[X])
                        if i==len(P)-1:
                            self.follow[X]+=self.follow[key]
                            self.follow[X]=list(set(self.follow[X]))
                            continue
                        else:
                            first_t=self.First.fst(P[i+1:])
                            self.follow[X]+=first_t
                            self.follow[X]=list(set(self.follow[X]))

                            if "$" in first_t:
                                self.follow[X]+=self.follow[key]
                                self.follow[X]=list(set(self.follow[X]))
                        if len(self.follow[X])!=prev:
                            flag=0
            if flag:
                break
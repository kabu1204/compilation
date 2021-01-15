from First_Follow import BuildFirst
from Scanner import scanner
from queue import Queue
import argparse

VT = ["h", "i", "m", "o", "type", "program", "begin", "end", "if", "then", "else",
		"var", "repeat", "until", "while", "do", "or", "not", "and", "+", "-", "*", "/",
    	"(", ")", "<", "<>", "<=", ">=", ">", "=", ":", ":=", ",", ";", ".", "#", "$"]

VN = ["A", "B", "C", "D", "E", "F", "G", "J", "K", "L", "N",
    "P", "Q", "R","_R","R_","S","S_","WL","T","T_","_T", "U", "V","V_", "W","W_", "W!", "X", "Y", "Z"]


G = {"W!": [["W"]],
	"A": [["B"], ["C"], ["D"]],
    "B": [["B", "+", "E"], ["B", "-", "E"], ["E"]],
    "E": [["E", "*", "F"], ["E", "/", "F"], ["F"]],
    "F": [["-", "F"], ["G"]],
    "G": [["h"], ["i"], ["(", "B", ")"]],
    "C": [["C", "or", "J"], ["J"]],
    "J": [["J", "and", "K"], ["K"]],
    "K": [["L"], ["not", "K"]],
    "L": [["m"], ["i"], ["(", "C", ")"], ["i", "N", "i"], ["B", "N", "B"]],
    "N": [["<"], ["<>"], ["<="], [">="], [">"], ["="]],
    "D": [["o"], ["i"]],
    "P": [["Q"], ["R"], ["S"], ["T"], ["U"]],
    "Q": [["i", ":=", "B"]],
    "R": [["_R","P"], ["R_","P"]],
    "_R":[["if","C","then"]],
    "R_":[["_R","P","else"]],
    "S": [["S_", "P"]],
    "S_":[["WL","C","do"]],
    "WL":[["while"]],
    "T": [["_T", "C"]],
    "T_":[["repeat"]],
    "_T":[["T_","P","until"]],
    "U": [["begin", "V", "end"]],
    "V": [["V_", "V"], ["P"]],
    "V_":[["P",";"]],
    "W": [["W_", "X", "U", "."]],
    "W_": [["program", "i", ";"]],
    "X": [["var", "Y"], ["$"]],
    "Y": [["Z", ":", "type", ";", "Y"], ["Z", ":", "type", ";"]],
    "Z": [["i", ",", "Z"], ["i"]]
    }

Production = []

STATES=[]

TABLE = [{}]

InterVN={}

TEMP={}

VN_PLACE={}

ID_PLACE=[]

FIRST = BuildFirst(VT, VN, G)

Quaternion=[]

F=[]

Codebegin={}

TRUE={}

FALSE={}

CHAIN={}


def cmp(s,t):
	t = list(t)
	try:
		for elem in s:
			t.remove(elem)
	except ValueError:
		return False
	return not t


def CLOSURE(I):
	closure_I = list(I)
	for i in closure_I:
		i[2]=i[2].copy()
	flag=1
	while 1:
		prev = closure_I+[]
		for item in closure_I:
			if item[3] < item[4] and (item[1][item[3]] in VN):
				for P in G[item[1][item[3]]]:
					beta=item[1][item[3]+1:] if item[3]+1<item[4] else ["$"]
					forwarder=FIRST.fst_(beta.copy(),item[2].copy())
					if forwarder==[]:
						print(item,"\t",item[2].copy())
					flag=1
					for i in closure_I:
						if i[0]==item[1][item[3]] and i[1]==P and i[3]==0:
							flag=0
							if not set(forwarder)<=set(i[2]):
								i[2]+=forwarder
								i[2]=list(set(i[2]))
								i[2]=i[2].copy()
								i[2].sort()
					if flag:
						new_item = [item[1][item[3]], P, forwarder, 0, len(P), Production.index([item[1][item[3]], P])]
						if P==["$"]:
							new_item[3]=1
						if not new_item in closure_I:
							closure_I.append(new_item)
		if cmp(closure_I,prev):
			return closure_I.copy()


def GOTO(I, ch,n=0):
	J = []
	I_=list(I)
	for i in I_:
		i[2]=i[2].copy()
	for item in I_:
		if not item[3]<item[4]:
			continue
		if item[1][item[3]] == ch:
			new_item = item+[]
			new_item[2]=new_item[2].copy()
			new_item[3] += 1
			J.append(new_item)
	return CLOSURE(J)


def BuildLR1Table(termination=["W!",["W"],["#"],1,1]):
	q = Queue()
	q.put(STATES[0])
	_from=0
	J=[]
	while not q.empty():
		cur_I=q.get()
		_from=STATES.index(cur_I)
		in_characters=[]
		for item in cur_I:
			if item[3]<item[4]:
				in_characters.append(item[1][item[3]])
			else:
				for k in item[2]:
					if k in TABLE[_from].keys():
						pass
						# print("err",_from)
					else:
						TABLE[_from][k]=['r',Production.index(item[:2])]
						if len(cur_I)==1 and item[:5]==termination:
							TABLE[_from][k]=["acc"]
		in_characters=list(set(in_characters))
		in_characters.sort()
		for ch in in_characters:
			J=GOTO(cur_I,ch,_from)
			flag=1
			for _to,items in enumerate(STATES):
				if cmp(J,items):
					flag=0
					if ch in TABLE[_from].keys() and TABLE[_from][ch][0]=='r':
						pass
						# print("err",_from)
					else:
						TABLE[_from][ch]=['S',_to]
					break
			if flag:
				STATES.append(J)
				TABLE.append({})
				if ch in TABLE[_from].keys() and TABLE[_from][ch][0]=='r':
					pass
					# print("err",_from)
				else:
					TABLE[_from][ch]=['S',len(STATES)-1]
				q.put(J)


def BuildProduction():
	global Production
	for key, value in G.items():
		for P in value:
			Production.append([key, P])

def DrawLR1Table():
	with open("LR1Table.MD","w") as f:
		f.write("|$\\boldsymbol{STATE}$|$\\boldsymbol{ITEMS}$\n|:-:|:-:\n")
		for i,items in enumerate(STATES):
			col_0="$\\boldsymbol{I_{"+str(i)+"}}$"
			res=""
			for j,item in enumerate(items):
				item_=item.copy()
				item_[1]=item_[1].copy()
				item_[1].insert(item_[3],"\\cdot")
				right="\\ ".join(item_[1])
				res+="\\boldsymbol{"+item_[0]+"}\\rightarrow"
				res+="\\boldsymbol{"+right+" }"
				res+="\\ \\ \\ \\ \\boldsymbol{\\{"+",".join(item_[2])+"\\}}"
				if j<len(items)-1:
					res+=r"\\"
				res=res.replace('$',r"\varepsilon")
				res=res.replace('{#',r"{\#")

			col_1="$"+res+"$"
			col_1=col_1.replace("_",r"\_{}")
			f.write("|"+col_0+"|"+col_1+"\n")

		V=VT[:-1]+VN
		headers1="<table border=\"1\">\n\t<tr>\n\t\t<td rowspan=\"3\" align=\"center\">STATE</td>\n\t\t<td colspan=\"37\" align=\"center\">ACTION</td>\n\t\t<td colspan=\"31\" align=\"center\">GOTO</td>\n\t<tr>\n"
		headers2="\t<tr>\n"
		for i,ch in enumerate(V):
			headers2+="\t\t<td align=\"center\">"+ch+"</td>\n"
		headers2+="\t<tr>\n"
		for i,row in enumerate(TABLE):
			content="\t<tr>\n"
			content+="\t\t<td align=\"center\">"+str(i)+"</td>\n"
			for j,ch in enumerate(V):
				if ch in row.keys():
					if row[ch][0]!="acc":
						if ch in VT:
							content+="\t\t<td align=\"center\">"+row[ch][0]+str(row[ch][1])+"</td>\n"
						else:
							content+="\t\t<td align=\"center\">"+str(row[ch][1])+"</td>\n"
					else:
						content+="\t\t<td align=\"center\">"+row[ch][0]+"</td>\n"
				else:
					content+="\t\t<td align=\"center\"></td>\n"
			content+="\t<tr>\n"
			headers2+=content
		f.write(headers1)
		f.write(headers2)


def GetInterVNNumber(ch):
	if not ch in InterVN.keys():
		InterVN[ch]=0
	InterVN[ch]+=1
	return InterVN[ch]


class SemanticActions():
	def __init__(self):
		self.switch={
		"W_->program i ;":self.programBegin,
		"W->W_ X U .":self.programEnd,
		"Q->i := B":self.assignment1,
		"P->Q":self.assignment2,
		"B->B + E":self.plus,
		"B->B - E":self.minus,
		"E->E * F":self.mul,
		"E->E / F":self.div,
		"F->- F":self.negative,
		"G->( B )":self.arithmaticParentheses,
		"Z->i":self.defID,
		"Z->i , Z":self.defID,
		"G->i":self.fromID,
		"L->i":self.fromID,
		"D->i":self.fromID,
		"G->h":self.fromINT,
		"B->E":self.Pass,
		"E->F":self.Pass,
		"F->G":self.Pass,
		"L->i N i":self.ropExp,
		"L->B N B":self.ropExp,
		"N-><":self.rop,
		"N-><>":self.rop,
		"N-><=":self.rop,
		"N->>=":self.rop,
		"N->>":self.rop,
		"N->=":self.rop,
		"N-><":self.rop,
		"C->C or J":self.orExp,
		"J->J and K":self.andExp,
		"K->not K":self.notExp,
		"L->( C )":self.logicParentheses,
		"K->L":self.logicPass,
		"J->K":self.logicPass,
		"C->J":self.logicPass,
		"P->Q":self.logicPass,
		"P->R":self.logicPass,
		"P->S":self.logicPass,
		"P->T":self.logicPass,
		"P->U":self.logicPass,
		"V->P":self.logicPass,
		"_R->if C then":self.if_C_then,
		"R->_R P":self._R_P,
		"R_->_R P else":self._R_P_else,
		"R->R_ P":self.R__P,
		"WL->while":self.WL,
		"S_->WL C do":self.WL_C_do,
		"S->S_ P":self.S__P,
		"U->begin V end":self.begin_V_end,
		"V_->P ;":self.V_,
		"V->V_ V":self.V__V,
		"T_->repeat":self.T_,
		"_T->T_ P until":self.T__P_until,
		"T->_T C":self._T_C
		}


	def nextstat(self):
		return len(Quaternion)

	def newtemp(self,symbol):
		key=symbol[0]+str(symbol[1])
		TEMP[key]="T"+str(len(TEMP)+1)
		VN_PLACE[key]=TEMP[key]
		return TEMP[key]

	def GetPlace(self,symbol):
		if symbol[0] in VN:
			return VN_PLACE[symbol[0]+str(symbol[1])]
		else:
			return symbol[1]

	def GetKey(self,symbol):
		return symbol[0]+str(symbol[1])

	def getf(self,u):
		if F[u]==u:
			return u
		else:
			return self.getf(F[u])

	def merge(self,u,v):
		if u==-1:
			return v
		if v!=-1:
			f=self.getf(u)
			F[f]=v
		return u

	def backpatch(self,p,t):
		if p==-1:
			return
		if F[p]!=p:
			Quaternion[p][-1]=t
			self.backpatch(F[p],t)
		else:
			Quaternion[p][-1]=t

	def programBegin(self,left,symbols):
		keyL=self.GetKey(left)
		Quaternion.append(["program",symbols[1][1],"-","-"])
		F.append(len(F))
		Codebegin[keyL]=self.nextstat()

	def programEnd(self,left,symbols):
		key=self.GetKey(symbols[2])
		self.backpatch(CHAIN[key],self.nextstat())
		Quaternion.append(["sys","-","-","-"])
		F.append(len(F))

	def assignment1(self,left,symbols):
		if not symbols[0][1] in ID_PLACE:
			RaiseError("use_before_declaration",symbols[0][1])
			return
		else:
			Quaternion.append([":=",self.GetPlace(symbols[-1]),"-",symbols[0][1]])
			F.append(len(F))
			CHAIN[self.GetKey(left)]=-1

	def assignment2(self,left,symbols):
		CHAIN[left[0]+str(left[1])]=-1

	def plus(self,left,symbols):
		Quaternion.append(["+",self.GetPlace(symbols[0]),self.GetPlace(symbols[-1]),self.newtemp(left)])
		F.append(len(F))

	def minus(self,left,symbols):
		Quaternion.append(["-",self.GetPlace(symbols[0]),self.GetPlace(symbols[-1]),self.newtemp(left)])
		F.append(len(F))

	def mul(self,left,symbols):
		Quaternion.append(["*",self.GetPlace(symbols[0]),self.GetPlace(symbols[-1]),self.newtemp(left)])
		F.append(len(F))

	def div(self,left,symbols):
		Quaternion.append(["/",self.GetPlace(symbols[0]),self.GetPlace(symbols[-1]),self.newtemp(left)])
		F.append(len(F))

	def negative(self,left,symbols):
		Quaternion.append(["@",self.GetPlace(symbols[-1]),"-",newtemp(left)])
		F.append(len(F))

	def arithmaticParentheses(self,left,symbols):
		VN_PLACE[self.GetKey(left)]=self.GetPlace(symbols[1])

	def defID(self,left,symbols):
		if not symbols[0][1] in ID_PLACE:
			ID_PLACE.append(symbols[0][1])

	def fromID(self,left,symbols):
		if not symbols[0][1] in ID_PLACE:
			RaiseError("use_before_declaration",symbols[0])
		VN_PLACE[self.GetKey(left)]=symbols[0][1]

	def fromINT(self,left,symbols):
		VN_PLACE[self.GetKey(left)]=symbols[0][1]

	def Pass(self,left,symbols):
		VN_PLACE[self.GetKey(left)]=self.GetPlace(symbols[0])

	def rop(self,left,symbols):
		VN_PLACE[self.GetKey(left)]=symbols[0][0]

	def ropExp(self,left,symbols):
		key=self.GetKey(left)
		Codebegin[key]=self.nextstat()
		TRUE[key]=self.nextstat()
		FALSE[key]=self.nextstat()+1
		Quaternion.append(["j"+self.GetPlace(symbols[1]),self.GetPlace(symbols[0]),self.GetPlace(symbols[-1]),-1])
		F.append(len(F))
		Quaternion.append(["j","-","-",-1])
		F.append(len(F))

	def logicPass(self,left,symbols):
		keyL=self.GetKey(left)
		keyR=self.GetKey(symbols[0])
		if keyR in Codebegin.keys():
			Codebegin[keyL]=Codebegin[keyR]
		if keyR in CHAIN.keys():
			CHAIN[keyL]=CHAIN[keyR]
			return
		if keyR in TRUE.keys():
			TRUE[keyL]=TRUE[keyR]
		if keyR in FALSE.keys():
			FALSE[keyL]=FALSE[keyR]

	def orExp(self,left,symbols):
		keyL=self.GetKey(left)
		key1=self.GetKey(symbols[0])
		key2=self.GetKey(symbols[-1])
		Codebegin[keyL]=Codebegin[key1]
		self.backpatch(FALSE[key1],Codebegin[key2])
		TRUE[keyL]=self.merge(TRUE[key1],TRUE[key2])
		FALSE[keyL]=FALSE[key2]

	def andExp(self,left,symbols):
		keyL=self.GetKey(left)
		key1=self.GetKey(symbols[0])
		key2=self.GetKey(symbols[-1])
		Codebegin[keyL]=Codebegin[key1]
		self.backpatch(TRUE[key1],Codebegin[key2])
		TRUE[keyL]=TRUE[key2]
		FALSE[keyL]=self.merge(FALSE[key1],FALSE[key2])

	def notExp(self,left,symbols):
		keyL=self.GetKey(left)
		key1=self.GetKey(symbols[1])
		Codebegin[keyL]=Codebegin[key1]
		TRUE[keyL]=FALSE[key1]
		FALSE[keyL]=TRUE[key1]

	def logicParentheses(self,left,symbols):
		keyL=self.GetKey(left)
		key1=self.GetKey(symbols[1])
		Codebegin[keyL]=Codebegin[key1]
		TRUE[keyL]=TRUE[key1]
		FALSE[keyL]=FALSE[key1]

	def if_C_then(self,left,symbols):
		keyL=self.GetKey(left)
		keyC=self.GetKey(symbols[1])
		self.backpatch(TRUE[keyC],self.nextstat())
		CHAIN[keyL]=FALSE[keyC]

	def _R_P(self,left,symbols):
		keyL=self.GetKey(left)
		key_R=self.GetKey(symbols[0])
		keyP=self.GetKey(symbols[1])
		CHAIN[keyL]=self.merge(CHAIN[key_R],CHAIN[keyP])

	def _R_P_else(self,left,symbols):
		keyL=self.GetKey(left)
		key_R=self.GetKey(symbols[0])
		keyP=self.GetKey(symbols[1])
		q=self.nextstat()
		Quaternion.append(["j","-","-",-1])
		F.append(len(F))
		self.backpatch(CHAIN[key_R],self.nextstat())
		CHAIN[keyL]=self.merge(q,CHAIN[keyP])

	def R__P(self,left,symbols):
		keyL=self.GetKey(left)
		keyR_=self.GetKey(symbols[0])
		keyP=self.GetKey(symbols[1])
		CHAIN[keyL]=self.merge(CHAIN[keyR_],CHAIN[keyP])

	def WL(self,left,symbols):
		keyL=self.GetKey(left)
		Codebegin[keyL]=self.nextstat()

	def WL_C_do(self,left,symbols):
		keyL=self.GetKey(left)
		keyWL=self.GetKey(symbols[0])
		keyC=self.GetKey(symbols[1])
		Codebegin[keyL]=Codebegin[keyWL]
		self.backpatch(TRUE[keyC],self.nextstat())
		CHAIN[keyL]=FALSE[keyC]

	def S__P(self,left,symbols):
		keyL=self.GetKey(left)
		keyS_=self.GetKey(symbols[0])
		keyP=self.GetKey(symbols[1])
		self.backpatch(CHAIN[keyP],Codebegin[keyS_])
		Quaternion.append(["j","-","-",Codebegin[keyS_]])
		F.append(len(F))
		CHAIN[keyL]=CHAIN[keyS_]

	def begin_V_end(self,left,symbols):
		keyL=self.GetKey(left)
		keyV=self.GetKey(symbols[1])
		CHAIN[keyL]=CHAIN[keyV]

	def V_(self,left,symbols):
		self.backpatch(CHAIN[self.GetKey(symbols[0])],self.nextstat())

	def V__V(self,left,symbols):
		keyL=self.GetKey(left)
		keyV=self.GetKey(symbols[-1])
		CHAIN[keyL]=CHAIN[keyV]

	def T_(self,left,symbols):
		Codebegin[self.GetKey(left)]=self.nextstat()

	def T__P_until(self,left,symbols):
		keyL=self.GetKey(left)
		keyT_=self.GetKey(symbols[0])
		keyP=self.GetKey(symbols[1])
		Codebegin[keyL]=Codebegin[keyT_]
		self.backpatch(CHAIN[keyP],self.nextstat())

	def _T_C(self,left,symbols):
		keyL=self.GetKey(left)
		key_T=self.GetKey(symbols[0])
		keyC=self.GetKey(symbols[1])
		self.backpatch(FALSE[keyC],Codebegin[key_T])
		CHAIN[keyL]=TRUE[keyC]

	def __call__(self,left,symbols,idx):
		if Production[idx][0]+"->"+" ".join(Production[idx][1]) in self.switch.keys():
			self.switch[Production[idx][0]+"->"+" ".join(Production[idx][1])](left,symbols)


def RaiseError(type_,symbol):
	if type_=="use_before_declaration":
		print("Error:"+"\""+symbol[1]+"\" is used before declaration.")


def LR1Analyze(in_tokens):
	Semantics=SemanticActions()
	stack_of_states=[0,]
	stack_of_symbols=["#",]
	_in_tokens=in_tokens+[]

	while 1:
		cur_state=stack_of_states[-1]
		cur_token=_in_tokens[0]
		if not cur_token[0] in TABLE[cur_state].keys():
			raise KeyError(cur_token)
		elif TABLE[cur_state][cur_token[0]][0]=='S':
			stack_of_states.append(TABLE[cur_state][cur_token[0]][1])
			stack_of_symbols.append(cur_token)
			_in_tokens.pop(0)
		elif TABLE[cur_state][cur_token[0]][0]=='r':
			P=Production[TABLE[cur_state][cur_token[0]][1]]+[]
			symbols=[]
			if not P[1]==['$']:
				symbols=stack_of_symbols[-len(P[1]):]
				stack_of_states=stack_of_states[:-len(P[1])]
				stack_of_symbols=stack_of_symbols[:-len(P[1])]
			stack_of_symbols.append((P[0],GetInterVNNumber(P[0])))
			stack_of_states.append(TABLE[stack_of_states[-1]][P[0]][1])
			if not P[1]==['$']:
				Semantics(stack_of_symbols[-1],symbols,TABLE[cur_state][cur_token[0]][1])
		elif TABLE[cur_state][cur_token[0]][0]=="acc":
			return


def Print():
	print("姓名：YCY\n班级：2019CS2\n学号：2019__")
	for i,Quater in enumerate(Quaternion):
		print("(%d)\t(%s , %s , %s , %s)" % (i,Quater[0],Quater[1],Quater[2],Quater[3]))

def init():
	global STATES
	BuildProduction()
	I0 = [["W!", ["W"], ["#"], 0, 1, Production.index(["W!",["W"]])]]
	STATES=[CLOSURE(I0)]
	BuildLR1Table()
	DrawLR1Table()

if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file_path", type=str)
	file_path = parser.parse_args().file_path
	scan=scanner()
	scan(file_path)
	init()
	LR1Analyze(scan.OUTPUT)
	Print()
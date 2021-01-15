import re
import argparse

class scanner():
    def __init__(self):
        self.ReservedWords = ["and", "array", "begin", "bool", "call", "case", "char",
                 "constant", "dim", "do", "else", "end", "false", "for",
                 "if", "input", "integer", "not", "of", "or", "output",
                 "procedure", "program", "read", "real", "repeat", "set",
                 "stop", "then", "to", "true", "until", "var", "while", "write"]
        self.DoubleBoundaryWords = ["<>", "<=", ">=", ":=", "/*", "*/"]
        self.SingleBoundaryWords = ["+", "-", "*", "/", "=", "<",">", "(", ")", "[", "]", ":", ".", ";", ","]
        self.Type=["bool","char","integer","real"]
        self.Identifier = "^[a-zA-Z][a-zA-Z0-9]*$"

        self.Integer = "^[1-9]\d*$"

        self.Chars = "^'[^']*'$"

        self.Encoding = {"and": 1, "array": 2, "begin": 3, "bool": 4, "call": 5, "case": 6, "char": 7,
            "constant": 8, "dim": 9, "do": 10, "else": 11, "end": 12, "false": 13, "for": 14,
            "if": 15, "input": 16, "integer": 17, "not": 18, "of": 19, "or": 20, "output": 21,
            "procedure": 22, "program": 23, "read": 24, "real": 25, "repeat": 26, "set": 27,
            "stop": 28, "then": 29, "to": 30, "true": 31, "until": 32, "var": 33, "while": 34,
            "write": 35, "Identifier": 36, "Integer": 37, "Chars": 38, "(": 39, ")": 40, "*": 41,
            "*/": 42, "+": 43, ",": 44, "-": 45, ".": 46, "..": 47, "/": 48, "/*": 49, ":": 50,
            ":=": 51, ";": 52, "<": 53, "<=": 54, "<>": 55, "=": 56, ">": 57, ">=": 58, "[": 59, "]": 60}

        self.Letters = "a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(" ")

        self.Digits = "0 1 2 3 4 5 6 7 8 9".split(" ")

        self.CharacterList = {}

        self.OUTPUT=[]

        self.RegEx = {}

        self.transform_matrix = [[1, 2, 3, 4, 5], [6, 6, 3, 3, 3], [3, 2, 3, 3, 3], [3, 3, 3, 3, 3], [
                                7, 7, 7, 8, 3], [3, 2, 3, 3, 3], [6, 6, 3, 3, 3], [7, 7, 7, 8, 3], [3, 3, 3, 3, 3]]


    def DFA(self,word):
        p = 0
        cur_pos = 0
        cur_state = 0
        while cur_pos <= len(word):
            if cur_pos == len(word):
                if cur_state in [1, 6]:
                    return "ID"
                elif cur_state is 2:
                    return "INT"
                elif cur_state is 8:
                    return "CHAR"
                else:
                    return "ERROR"
            if word[cur_pos] in self.Letters:
                p = 0
            elif word[cur_pos] in self.Digits:
                p = 1
            elif word[cur_pos] is "'":
                p = 3
            elif word[cur_pos] is "-":
                p = 4
            else:
                p = 2
            if self.transform_matrix[cur_state][p] == 3:
                return "ERROR"
            else:
                cur_state=self.transform_matrix[cur_state][p]
            cur_pos += 1

    def BuildRegEx(self):
        self.RegEx["ReservedWords"] = "|".join(["^"+i+"$" for i in self.ReservedWords])
        self.RegEx["DoubleBoundaryWords"] = r"^<>$|^<=$|^>=$|^:=$|^/\*$|^\*/$"
        self.RegEx["SingleBoundaryWords"] = r"^[\+\-\*/=<>\(\)\[\]:\.;,]$"
        self.RegEx["Integer"] = self.Integer
        self.RegEx["Identifier"] = self.Identifier
        self.RegEx["Chars"] = self.Chars

    def GetWordList(self,file_path):
        with open(file_path, 'r') as f:
            raw = f.read()
        PreSplit = list(filter(lambda x : None if x in [' ','\n','\t'] else x,re.split(r'(<>|<=|>=|:=|/\*.*\*/|\.\.|[\+\-\(\)\[\];,\s])', raw)))
        WordList = []
        flag=0
        if "/*" in PreSplit and not "*/" in PreSplit:
            flag=1
        if "/*" in PreSplit and "*/" in PreSplit and "\n" in PreSplit[PreSplit.index("/*"):PreSplit.index("*/")]:
            flag=1
        if flag:
            self.RaiseError("/*")
        for SubStr in PreSplit:
            if not re.match("^/\*.*\*/$", SubStr) is None:
                continue
            if not SubStr in self.DoubleBoundaryWords:
                SubSplit = re.split(r'([\*/=<>:\.])', SubStr)
                for i in SubSplit:
                    WordList.append(i)
            else:
                WordList.append(SubStr)
        WordList = [i for i in WordList if not i in ['', ' ', '\t', '\n']]
        return WordList

    def Analysis(self,word):
        if not re.match(self.RegEx["ReservedWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["ReservedWords"], word).group()], end=' ')
            if not word in self.Type:
                self.OUTPUT.append((word,-1))
            else:
                self.OUTPUT.append(("type",word))
        elif not re.match(self.RegEx["DoubleBoundaryWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["DoubleBoundaryWords"], word).group()], end=' ')
            self.OUTPUT.append((word,-1))
        elif not re.match(self.RegEx["SingleBoundaryWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["SingleBoundaryWords"], word).group()], end=' ')
            self.OUTPUT.append((word,-1))
        else:
            res = self.DFA(word)
            if res == "ERROR":
                self.RaiseError(word)
                return
            else:
                if word in self.CharacterList.keys():
                    place = self.CharacterList[word]
                else:
                    place = len(self.CharacterList)+1
                    self.CharacterList[word] = place
            if res == "ID":
                print("(%d,%d)" % (self.Encoding["Identifier"], place), end=' ')
                self.OUTPUT.append(("i",word))
            elif res == "INT":
                print("(%d,%d)" % (self.Encoding["Integer"], place), end=' ')
                self.OUTPUT.append(("h",word))
            else:
                print("(%d,%d)" % (self.Encoding["Chars"], place), end=' ')
                self.OUTPUT.append(("o",word))

    def Analysis_NO_DFA(word):
        if not re.match(self.RegEx["ReservedWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["ReservedWords"], word).group()], end=' ')
        elif not re.match(self.RegEx["Identifier"], word) is None:
            id_name = re.match(self.RegEx["Identifier"], word).group()
            if id_name in self.CharacterList.keys():
                place = self.CharacterList[id_name]
            else:
                place = len(self.CharacterList)+1
                self.CharacterList[id_name] = place
            print("(%d,%d)" % (self.Encoding["Identifier"], place), end=' ')
        elif not re.match(self.RegEx["DoubleBoundaryWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["DoubleBoundaryWords"], word).group()], end=' ')
        elif not re.match(self.RegEx["SingleBoundaryWords"], word) is None:
            print("(%d,-)" %
                  self.Encoding[re.match(self.RegEx["SingleBoundaryWords"], word).group()], end=' ')
        elif not re.match(self.RegEx["Integer"], word) is None:
            int_name = re.match(self.RegEx["Integer"], word)
            if int_name in self.CharacterList.keys():
                place = self.CharacterList[id_name]
            else:
                place = len(self.CharacterList)+1
                self.CharacterList[int_name] = place
            print("(%d,%d)" % (self.Encoding["Integer"], place), end=' ')
        elif not re.match(self.RegEx["Chars"], word) is None:
            chars_name = re.match(self.RegEx["Chars"], word)
            if chars_name in self.CharacterList.keys():
                place = self.CharacterList[chars_name]
            else:
                place = len(self.CharacterList)+1
                self.CharacterList[chars_name] = place
            print("(%d,%d)" % (self.Encoding["Chars"], place), end=' ')
        else:
            self.RaiseError(word)

    def RaiseError(self,word):
        if not re.match("/\*", word) is None:
            print(r"The format of your COMMENT is WRONG, make sure the '/*' and '*/' are PAIRED and in the SAME LINE: %s" % word)
        elif not re.match("^'", word) is None:
            print("\nThe format of your CONST CHAR is WRONG, make sure the left and right \"'\" are PAIRED and in the SAME LINE: %s" % word)
        else:
            print("\nThere is a LEXICAL ERROR with the word: %s" % word)

    def __call__(self,file_path):
        WordList=self.GetWordList(file_path)
        self.BuildRegEx()
        for i,word in enumerate(WordList):
            self.Analysis(word)
            if (i+1) % 5 == 0:
                print("\n")
        print("\n")
        self.OUTPUT.append(("#",-1))

if __name__ == "__main__":
    print("姓名：YCY\n班级：2019CS2\n学号：2019__")
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str)
    file_path = parser.parse_args().file_path
    # WordList = GetWordList(file_path)
    # BuildRegEx()

    a=scanner()
    a(file_path)
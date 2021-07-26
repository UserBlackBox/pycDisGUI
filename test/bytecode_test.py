import math
from sys import exit

class Main:
    @staticmethod
    def main():
        try:
            num = int(input())
        except ValueError:
            exit(1)
        print(math.sqrt(num))
        print('test')
        for i in range(10):
            print(i)
        i = 0
        while i<10:
            i+=1
            print(i)
        if num%2==0:
            print('even')
        else:
            print('odd')
        del num
        exit(0)

Main.main()

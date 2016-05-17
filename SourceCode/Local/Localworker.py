# -*- coding: utf-8 -*-
import os
import time
from threading import Thread


class Localworker(Thread):

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.results = list()
        return


    def run(self):
        for task in self.tasks:

            arg = task.split()
            arg1 = float(str(arg[1])) / 1000
            arg = arg[0] + " " + str(arg1)
            try:
                os.system(arg)

                result = task + ' has completed...\n'
                validate = 0
            #print result
                self.results.append(validate)

            except:
                validate = 1
                self.results.append(validate)

        return


if __name__ == '__main__':
    pass

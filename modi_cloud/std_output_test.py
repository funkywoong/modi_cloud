from io import StringIO
import sys
import threading as th
import time

from example.test.test import gen_data, gen_model


X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
model = gen_model()
# output = str()
# watch_output = th.thread(target=)

class Watcher():

    def __init__(self):
        self.output = []
        self.old_stdout_temp = None
        self.new_stdout_temp = None
        self.flag = False

    def fit(self):
        print('fit')
        old_stdout = sys.stdout
        self.old_stdout_temp = old_stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        self.new_stdout_temp = new_stdout
        #sys.stdout = StringIO()
        # print(sys.stdout.flush())
        # print(type(new_stdout.getvalue()))
        model.fit(X_train, y_train, epochs=10, batch_size=32)
        # print('hi')
        self.output.append(self.new_stdout_temp.getvalue())
        sys.stdout = old_stdout
        # print(self.output)
        # print(len(self.output))
        print('bye')
        self.flag = True

    def watch_output(self):
        print('watch')
        tmp_list = list()
        while 1:
            tmp_list.append(self.new_stdout_temp.getvalue())
            time.sleep(0.05)

            if self.flag:
                break
            # if len(self.output) > 15000:
            #     break

        for each_item in tmp_list:
            print(each_item)
        print(len(tmp_list))
        # print(tmp_list)
        # while 1:
        #     print(output)

if __name__ == '__main__':
    
    w = Watcher()
    
    fit_th = th.Thread(target=w.fit)
    fit_th.daemon = True
    fit_th.start()

    watch_th = th.Thread(target=w.watch_output)
    watch_th.daemon = True
    watch_th.start()

    fit_th.join()
    watch_th.join()
    
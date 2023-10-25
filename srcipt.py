import multiprocessing as mp
from threading import Thread
import time
from MailScanner.MailScanner import MailMonitor

login1 = 'andrei.agasiants@unilever-rus.ru'
password1 = 'xbydxlcsjzoqgqfk'
search_string1 = 'SUBJECT "mail-scanner-test-work"'
filename1 = 'mail-scanner-file-work'

login2 = 'at-am@yandex.ru'
password2 = 'wjbfzxqwqqamkapj'
search_string2 = 'SUBJECT "mail-scanner-test-home"'
filename1 = 'mail-scanner-file-home'

def create_monitor(login, password, searching_string):
    mail = MailMonitor(
        "imap.yandex.ru", login, password
    )

    req_emails = set()
    while True:
        req_emails_list = mail.search_mail(searching_string)
        req_emails_set = set(req_emails_list)
        print(f'{login} - recieved ids: {req_emails_set}')
        if req_emails_set - req_emails:
            print(login, req_emails_set - req_emails, sep=': ')
            print(login, req_emails_set, sep=', ')
            req_emails = req_emails_set
        print(f'{login} - going to sleep for 30 sec')
        for i in range(30):
            print(i, end=' ')
            time.sleep(1)

def mail_monitor(instruction_list):
    print(instruction_list)
    for _, params in instruction_list.items():
        print(f'create thread with params {params}')
        thread = Thread(target=create_monitor, args=params)
        print(f'start thread with params {params}')
        thread.start()



def django_app():
    params = {'instruction1': [login1, password1, search_string1], }
    while True:
        print(f'start process with params {params}')
        p = mp.Process(target=mail_monitor, args=(params, ))
        p.start()
        reload = input('r? : ')
        if reload == 'r':
            p.terminate()
            params['instruction2'] = [login2, password2, search_string2]





if __name__ == '__main__':
    django_app()

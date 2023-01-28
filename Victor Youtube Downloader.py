from tkinter import CENTER, ttk, Tk, StringVar, Entry, Button, Label
from asyncio import AbstractEventLoop, get_event_loop
from threading import Thread
from yt_dlp import YoutubeDL
from os import path, environ
from re import compile, VERBOSE

""" TO CONVERT TO EXE I USED THE auto-py-to-exe """

ansi_escape = compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', VERBOSE)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = ansi_escape.sub('', d['_percent_str'].replace(' ', '').replace('%', ''))
        time_remaining = ansi_escape.sub('', d['_eta_str'].replace(' ', ''))
        size = ansi_escape.sub('', d['_total_bytes_str'].replace(' ', ''))
        size_remaining = ansi_escape.sub('', d['_downloaded_bytes_str'].replace(' ', ''))
        elapsed = ansi_escape.sub('', d['_elapsed_str'].replace(' ', ''))
        download_speed = ansi_escape.sub('', d['_speed_str'].replace(' ', ''))

        download_progressbar['value'] = float(percent)
        download_txt.set(f'\n{percent}% \n {size_remaining} of {size} at {download_speed} \n\n Time remaining: {time_remaining} \n Time elapsed: {elapsed}')
    if d['status'] == 'finished':
        download_txt.set('Finished. Your file is on your desktop in the "Downloaded Youtube Videos" folder')

def _asyncio_thread(async_loop: AbstractEventLoop, url):
    async_loop.run_until_complete(download(url))

def do_task(async_loop: AbstractEventLoop, url):
    """ Button-Event-Handler starting the asyncio part. """
    Thread(target=_asyncio_thread, args=(async_loop, url)).start()

async def download(url):
    desktop = path.join(path.join(environ['USERPROFILE']), 'Desktop')
    
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio',
        'outtmpl': '{0}/Downloaded Youtube Videos/%(title)s.%(ext)s'.format(desktop),
        'progress_hooks': [progress_hook],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    

if __name__ == '__main__':
    async_loop = get_event_loop()

    root = Tk()
    root.title('Victor\'s Youtube Downloader')
    root.geometry("500x400")

    download_txt = StringVar(master=root, value='Download status')

    url_label = Label(master=root, text='URL: ')
    url_label.place(relx=0.5, rely=0.05, anchor=CENTER)

    url = Entry(master=root, width=80)
    url.place(relx=0.5, rely=0.1, anchor=CENTER)

    download_btn = Button(master=root, text='Download', command=lambda: do_task(async_loop, url.get()))
    download_btn.place(relx=0.5, rely=0.25, anchor=CENTER)

    download_progressbar = ttk.Progressbar(master=root, value=0, length=320)
    download_progressbar.place(relx=0.5, rely=0.35, anchor=CENTER)

    download_perc = Label(master=root, textvariable=download_txt)
    download_perc.place(relx=0.5, rely=0.54, anchor=CENTER)

    root.mainloop()
